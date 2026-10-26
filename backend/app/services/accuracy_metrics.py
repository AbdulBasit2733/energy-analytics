from itertools import groupby

import numpy as np

from app.models.domain import AccuracyMetrics, DailyAccuracy, ForecastActualPair
from app.models.responses import ErrorDistributionBin


def calculate_metrics(pairs: list[ForecastActualPair]) -> AccuracyMetrics:
    if not pairs:
        return AccuracyMetrics(
            mae=0.0, rmse=0.0, mape=None, bias=0.0,
            max_overforecast=0.0, max_underforecast=0.0,
            correlation=None, paired_hours=0,
        )

    forecasts = np.array([p.forecast_mw for p in pairs])
    actuals = np.array([p.actual_mw for p in pairs])
    errors = forecasts - actuals
    abs_errors = np.abs(errors)

    mae = float(np.mean(abs_errors))
    rmse = float(np.sqrt(np.mean(errors**2)))
    bias = float(np.mean(errors))

    nonzero_mask = actuals > 1.0
    if nonzero_mask.any():
        mape = float(np.mean(abs_errors[nonzero_mask] / actuals[nonzero_mask]) * 100)
    else:
        mape = None

    if len(pairs) > 1:
        correlation = float(np.corrcoef(forecasts, actuals)[0, 1])
        if np.isnan(correlation):
            correlation = None
    else:
        correlation = None

    return AccuracyMetrics(
        mae=round(mae, 1),
        rmse=round(rmse, 1),
        mape=round(mape, 2) if mape is not None else None,
        bias=round(bias, 1),
        max_overforecast=round(float(np.max(errors)), 1),
        max_underforecast=round(float(np.min(errors)), 1),
        correlation=round(correlation, 4) if correlation is not None else None,
        paired_hours=len(pairs),
    )


def calculate_daily_metrics(pairs: list[ForecastActualPair]) -> list[DailyAccuracy]:
    sorted_pairs = sorted(pairs, key=lambda p: p.hour.date())
    daily = []

    for date_key, group in groupby(sorted_pairs, key=lambda p: p.hour.date()):
        day_pairs = list(group)
        metrics = calculate_metrics(day_pairs)
        daily.append(
            DailyAccuracy(
                date=date_key,
                mae=metrics.mae,
                rmse=metrics.rmse,
                bias=metrics.bias,
                paired_hours=metrics.paired_hours,
            )
        )

    return daily


def calculate_error_distribution(
    pairs: list[ForecastActualPair],
    bin_width: float = 500.0,
) -> list[ErrorDistributionBin]:
    if not pairs:
        return []

    # Defensive validation (also validated at router level)
    if bin_width <= 0:
        raise ValueError(f"bin_width must be > 0, got {bin_width}")

    if bin_width > 100000:
        raise ValueError(f"bin_width too large: {bin_width}")

    errors = [p.error_mw for p in pairs]
    min_error = min(errors)
    max_error = max(errors)

    bin_start = (int(min_error / bin_width) - 1) * bin_width
    bin_end_limit = (int(max_error / bin_width) + 2) * bin_width

    bins: list[ErrorDistributionBin] = []
    current = bin_start
    while current < bin_end_limit:
        count = sum(1 for e in errors if current <= e < current + bin_width)
        bins.append(
            ErrorDistributionBin(
                bin_start=current,
                bin_end=current + bin_width,
                count=count,
            )
        )
        current += bin_width

    return [b for b in bins if b.count > 0]
