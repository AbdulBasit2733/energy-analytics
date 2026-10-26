from collections import defaultdict
from datetime import datetime

from app.models.domain import ForecastActualPair, HourlyActual, HourlyForecast
from app.models.elexon import FuelHHRecord
from app.utils.time_helpers import floor_to_hour


def aggregate_fuelhh_to_hourly(records: list[FuelHHRecord]) -> list[HourlyActual]:
    hourly_groups: dict[datetime, list[int]] = defaultdict(list)

    for record in records:
        hour_key = floor_to_hour(record.start_time)
        hourly_groups[hour_key].append(record.generation)

    result = []
    for hour in sorted(hourly_groups.keys()):
        values = hourly_groups[hour]
        if not values:  # Defensive guard (shouldn't happen)
            continue

        result.append(
            HourlyActual(
                hour=hour,
                generation_mw=sum(values) / len(values),
                half_hour_count=len(values),
            )
        )
    return result


def pair_forecast_actual(
    forecasts: list[HourlyForecast],
    actuals: list[HourlyActual],
) -> list[ForecastActualPair]:
    actual_by_hour = {a.hour: a for a in actuals}
    pairs = []

    for f in forecasts:
        if f.hour in actual_by_hour:
            a = actual_by_hour[f.hour]
            error = f.generation_mw - a.generation_mw
            abs_error = abs(error)

            # Consistent with MAPE calculation: exclude near-zero actuals
            if a.generation_mw > 1.0:
                error_pct = (error / a.generation_mw) * 100
            else:
                error_pct = None

            pairs.append(
                ForecastActualPair(
                    hour=f.hour,
                    forecast_mw=f.generation_mw,
                    actual_mw=a.generation_mw,
                    error_mw=round(error, 1),
                    abs_error_mw=round(abs_error, 1),
                    error_pct=round(error_pct, 2) if error_pct is not None else None,
                )
            )

    return sorted(pairs, key=lambda p: p.hour)
