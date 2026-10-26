import asyncio
import json
import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from app.config import settings
from app.models.domain import ForecastActualPair, HourlyActual, HourlyForecast
from app.models.elexon import FuelHHRecord, WindForRecord
from app.services.data_processor import aggregate_fuelhh_to_hourly, pair_forecast_actual
from app.services.elexon_client import elexon_client
from app.services.forecast_selector import select_day_ahead_forecast
from app.utils.time_helpers import date_to_utc_datetime, iter_dates

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self):
        self._fuelhh: list[FuelHHRecord] = []
        self._windfor_by_date: dict[date, list[WindForRecord]] = {}
        self._hourly_actuals: list[HourlyActual] = []
        self._selected_forecasts: dict[date, list[HourlyForecast]] = {}
        self._forecast_publish_times: dict[date, datetime | None] = {}
        self._pairs: list[ForecastActualPair] = []
        self._pairs_by_date: dict[date, list[ForecastActualPair]] = {}
        self._all_windfor: dict[date, list[WindForRecord]] = {}
        self._loaded = False
        self._max_cached_months = 12  # Limit cache to 12 months to prevent OOM

    def _evict_old_cache(self):
        """Evict oldest cached months if exceeding limit."""
        # Count unique months, not individual dates
        cached_months = set((d.year, d.month) for d in self._pairs_by_date.keys())

        if len(cached_months) > self._max_cached_months:
            sorted_dates = sorted(self._pairs_by_date.keys())

            # Calculate how many months to evict
            months_to_evict = len(cached_months) - self._max_cached_months

            # Find all dates in oldest N months
            month_counts = {}
            for d in sorted_dates:
                month_key = (d.year, d.month)
                month_counts[month_key] = month_counts.get(month_key, 0) + 1

            oldest_months = sorted(month_counts.keys())[:months_to_evict]
            to_evict = [d for d in sorted_dates if (d.year, d.month) in oldest_months]

            for d in to_evict:
                self._pairs_by_date.pop(d, None)
                self._selected_forecasts.pop(d, None)
                self._forecast_publish_times.pop(d, None)
                self._windfor_by_date.pop(d, None)
                self._all_windfor.pop(d, None)

            # Rebuild _pairs list
            self._pairs = []
            for pairs_list in self._pairs_by_date.values():
                self._pairs.extend(pairs_list)
            self._pairs.sort(key=lambda p: p.hour)

            logger.info("Evicted %d months (%d dates), %d months remain",
                       months_to_evict, len(to_evict), len(cached_months) - months_to_evict)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def fuelhh_records(self) -> list[FuelHHRecord]:
        return self._fuelhh

    @property
    def hourly_actuals(self) -> list[HourlyActual]:
        return self._hourly_actuals

    @property
    def all_pairs(self) -> list[ForecastActualPair]:
        return self._pairs

    @property
    def dates_cached(self) -> int:
        return len(self._pairs_by_date)

    def get_pairs_for_range(
        self, start: date | None = None, end: date | None = None,
    ) -> list[ForecastActualPair]:
        if start is None and end is None:
            return self._pairs
        return [
            p for p in self._pairs
            if (start is None or p.hour.date() >= start)
            and (end is None or p.hour.date() <= end)
        ]

    def get_pairs_for_date(self, d: date) -> list[ForecastActualPair]:
        return self._pairs_by_date.get(d, [])

    def get_selected_forecasts(self, d: date) -> list[HourlyForecast]:
        return self._selected_forecasts.get(d, [])

    def get_forecast_publish_time(self, d: date) -> datetime | None:
        return self._forecast_publish_times.get(d)

    def get_actuals_for_range(
        self, start: date | None = None, end: date | None = None,
    ) -> list[HourlyActual]:
        if start is None and end is None:
            return self._hourly_actuals
        return [
            a for a in self._hourly_actuals
            if (start is None or a.hour.date() >= start)
            and (end is None or a.hour.date() <= end)
        ]

    def get_windfor_for_date(self, d: date) -> list[WindForRecord]:
        return self._all_windfor.get(d, [])

    async def warm_cache(self):
        cache_dir = Path(settings.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        analysis_start = date(settings.analysis_year, settings.analysis_month, 1)
        if settings.analysis_month == 12:
            analysis_end = date(settings.analysis_year + 1, 1, 1) - timedelta(days=1)
        else:
            analysis_end = date(settings.analysis_year, settings.analysis_month + 1, 1) - timedelta(days=1)

        fuelhh_cache = cache_dir / "fuelhh.json"
        if fuelhh_cache.exists():
            logger.info("Loading FUELHH from disk cache")
            raw = json.loads(fuelhh_cache.read_text())
            self._fuelhh = [FuelHHRecord.model_validate(r) for r in raw]
        else:
            logger.info("Fetching FUELHH from Elexon API...")
            self._fuelhh = await elexon_client.fetch_fuelhh(analysis_start, analysis_end)
            fuelhh_cache.write_text(
                json.dumps([r.model_dump(by_alias=True, mode="json") for r in self._fuelhh])
            )

        self._hourly_actuals = aggregate_fuelhh_to_hourly(self._fuelhh)
        logger.info("Aggregated to %d hourly actuals", len(self._hourly_actuals))

        delivery_dates = list(iter_dates(analysis_start, analysis_end))

        async def fetch_windfor_for_date(d: date) -> tuple[date, list[WindForRecord]]:
            cache_file = cache_dir / f"windfor_{d.isoformat()}.json"
            if cache_file.exists():
                raw = json.loads(cache_file.read_text())
                records = [WindForRecord.model_validate(r) for r in raw]
            else:
                start_dt = date_to_utc_datetime(d, 0)
                end_dt = date_to_utc_datetime(d, 23)
                publish_from = date_to_utc_datetime(d - timedelta(days=2), 0)
                cutoff_dt = date_to_utc_datetime(d - timedelta(days=1), settings.forecast_cutoff_hour)
                records = await elexon_client.fetch_windfor(
                    start_time_from=start_dt,
                    start_time_to=end_dt,
                    publish_from=publish_from,
                    publish_to=cutoff_dt,
                )
                cache_file.write_text(
                    json.dumps([r.model_dump(by_alias=True, mode="json") for r in records])
                )
            return d, records

        batch_size = 5
        failed_dates = []
        for i in range(0, len(delivery_dates), batch_size):
            batch = delivery_dates[i : i + batch_size]
            results = await asyncio.gather(
                *[fetch_windfor_for_date(d) for d in batch],
                return_exceptions=True,
            )
            for idx, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_date = batch[idx]
                    logger.error("Failed to fetch WINDFOR for %s: %s", failed_date, result)
                    failed_dates.append(failed_date)
                    continue
                d, records = result
                self._all_windfor[d] = records
                self._windfor_by_date[d] = records

        if failed_dates:
            logger.warning("CRITICAL: Failed to fetch data for %d dates: %s",
                          len(failed_dates), failed_dates)

        for d in delivery_dates:
            forecasts_for_date = self._windfor_by_date.get(d, [])
            selected, publish_time = select_day_ahead_forecast(
                forecasts_for_date, d, settings.forecast_cutoff_hour,
            )
            self._selected_forecasts[d] = selected
            self._forecast_publish_times[d] = publish_time

            actuals_for_date = [a for a in self._hourly_actuals if a.hour.date() == d]
            day_pairs = pair_forecast_actual(selected, actuals_for_date)
            self._pairs_by_date[d] = day_pairs
            self._pairs.extend(day_pairs)

        self._pairs.sort(key=lambda p: p.hour)
        self._loaded = True

        # Evict old cache to prevent memory growth
        self._evict_old_cache()

        logger.info(
            "Cache ready: %d dates, %d hourly pairs, %.1f%% completeness",
            len(delivery_dates),
            len(self._pairs),
            (len(self._pairs) / (len(delivery_dates) * 24)) * 100 if delivery_dates else 0,
        )


cache_manager = CacheManager()
