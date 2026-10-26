import logging
from datetime import date, datetime, timedelta, timezone

from app.models.domain import HourlyForecast
from app.models.elexon import WindForRecord

logger = logging.getLogger(__name__)


def get_cutoff_time(delivery_date: date, cutoff_hour: int = 9) -> datetime:
    day_before = delivery_date - timedelta(days=1)
    return datetime(
        day_before.year, day_before.month, day_before.day,
        cutoff_hour, 0, 0, tzinfo=timezone.utc,
    )


def select_day_ahead_forecast(
    all_forecasts: list[WindForRecord],
    delivery_date: date,
    cutoff_hour: int = 9,
) -> tuple[list[HourlyForecast], datetime | None]:
    cutoff = get_cutoff_time(delivery_date, cutoff_hour)

    delivery_start = datetime(
        delivery_date.year, delivery_date.month, delivery_date.day,
        0, 0, 0, tzinfo=timezone.utc,
    )
    delivery_end = delivery_start + timedelta(hours=23)

    eligible = [
        f for f in all_forecasts
        if f.publish_time < cutoff
        and delivery_start <= f.start_time <= delivery_end
    ]

    used_fallback = False
    if not eligible:
        logger.warning(
            "No forecast before cutoff %s for delivery %s. Using earliest available.",
            cutoff.isoformat(), delivery_date.isoformat(),
        )
        eligible = [
            f for f in all_forecasts
            if delivery_start <= f.start_time <= delivery_end
        ]
        used_fallback = True

    if not eligible:
        logger.warning("No forecasts at all for delivery %s", delivery_date.isoformat())
        return [], None

    latest_publish = max(f.publish_time for f in eligible)
    selected = [f for f in eligible if f.publish_time == latest_publish]

    if used_fallback:
        logger.info(
            "Fallback forecast for %s: publishTime=%s",
            delivery_date.isoformat(), latest_publish.isoformat(),
        )
    else:
        logger.info(
            "Selected forecast for %s: publishTime=%s (%d records)",
            delivery_date.isoformat(), latest_publish.isoformat(), len(selected),
        )

    result = sorted(
        [
            HourlyForecast(
                hour=f.start_time,
                generation_mw=float(f.generation),
                publish_time=f.publish_time,
            )
            for f in selected
        ],
        key=lambda h: h.hour,
    )
    return result, latest_publish


def get_all_forecast_runs(
    all_forecasts: list[WindForRecord],
    delivery_date: date,
) -> dict[datetime, list[HourlyForecast]]:
    delivery_start = datetime(
        delivery_date.year, delivery_date.month, delivery_date.day,
        0, 0, 0, tzinfo=timezone.utc,
    )
    delivery_end = delivery_start + timedelta(hours=23)

    relevant = [
        f for f in all_forecasts
        if delivery_start <= f.start_time <= delivery_end
    ]

    runs: dict[datetime, list[HourlyForecast]] = {}
    for f in relevant:
        if f.publish_time not in runs:
            runs[f.publish_time] = []
        runs[f.publish_time].append(
            HourlyForecast(
                hour=f.start_time,
                generation_mw=float(f.generation),
                publish_time=f.publish_time,
            )
        )

    for publish_time in runs:
        runs[publish_time].sort(key=lambda h: h.hour)

    return runs
