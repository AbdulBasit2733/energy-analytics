from datetime import date, datetime, timezone

import pytest

from app.models.domain import ForecastActualPair, HourlyActual, HourlyForecast
from app.models.elexon import FuelHHRecord, WindForRecord


def utc(year, month, day, hour=0, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


@pytest.fixture
def fuelhh_two_half_hours():
    """Two half-hour records for the same hour (00:00 and 00:30 on Jan 15)."""
    return [
        FuelHHRecord(
            dataset="FUELHH",
            publish_time=utc(2026, 1, 15, 0, 30),
            start_time=utc(2026, 1, 15, 0, 0),
            settlement_date=date(2026, 1, 15),
            settlement_period=1,
            fuel_type="WIND",
            generation=10000,
        ),
        FuelHHRecord(
            dataset="FUELHH",
            publish_time=utc(2026, 1, 15, 1, 0),
            start_time=utc(2026, 1, 15, 0, 30),
            settlement_date=date(2026, 1, 15),
            settlement_period=2,
            fuel_type="WIND",
            generation=12000,
        ),
    ]


@pytest.fixture
def fuelhh_single_half_hour():
    """Only one half-hour record for the 01:00 hour."""
    return [
        FuelHHRecord(
            dataset="FUELHH",
            publish_time=utc(2026, 1, 15, 1, 30),
            start_time=utc(2026, 1, 15, 1, 0),
            settlement_date=date(2026, 1, 15),
            settlement_period=3,
            fuel_type="WIND",
            generation=14000,
        ),
    ]


@pytest.fixture
def fuelhh_full_day():
    """48 half-hour records for Jan 15 (settlement periods 1-48)."""
    records = []
    for sp in range(1, 49):
        hour = (sp - 1) // 2
        minute = 0 if (sp - 1) % 2 == 0 else 30
        records.append(
            FuelHHRecord(
                dataset="FUELHH",
                publish_time=utc(2026, 1, 15, hour, minute + 30 if minute == 0 else 0)
                if minute == 0
                else utc(2026, 1, 15, hour + 1, 0)
                if hour < 23
                else utc(2026, 1, 16, 0, 0),
                start_time=utc(2026, 1, 15, hour, minute),
                settlement_date=date(2026, 1, 15),
                settlement_period=sp,
                fuel_type="WIND",
                generation=10000 + sp * 100,
            )
        )
    return records


@pytest.fixture
def windfor_multiple_runs():
    """Multiple forecast runs for Jan 15 delivery, with different publish times."""
    records = []
    publish_times = [
        utc(2026, 1, 13, 18, 30),  # D-2 evening
        utc(2026, 1, 14, 4, 30),   # D-1 early morning
        utc(2026, 1, 14, 7, 30),   # D-1 morning (latest before 09:00 cutoff)
        utc(2026, 1, 14, 11, 30),  # D-1 late morning (AFTER cutoff)
    ]
    for pt in publish_times:
        for hour in range(24):
            records.append(
                WindForRecord(
                    dataset="WINDFOR",
                    publish_time=pt,
                    start_time=utc(2026, 1, 15, hour, 0),
                    generation=15000 + hour * 50 + publish_times.index(pt) * 200,
                )
            )
    return records


@pytest.fixture
def windfor_only_after_cutoff():
    """All forecasts published AFTER the 09:00 UTC cutoff on D-1."""
    records = []
    for hour in range(24):
        records.append(
            WindForRecord(
                dataset="WINDFOR",
                publish_time=utc(2026, 1, 14, 11, 30),
                start_time=utc(2026, 1, 15, hour, 0),
                generation=16000 + hour * 50,
            )
        )
    return records


@pytest.fixture
def sample_hourly_actuals():
    """24 hourly actual values for Jan 15."""
    return [
        HourlyActual(
            hour=utc(2026, 1, 15, h, 0),
            generation_mw=10000.0 + h * 200.0,
            half_hour_count=2,
        )
        for h in range(24)
    ]


@pytest.fixture
def sample_hourly_forecasts():
    """24 hourly forecast values for Jan 15."""
    return [
        HourlyForecast(
            hour=utc(2026, 1, 15, h, 0),
            generation_mw=10500.0 + h * 180.0,
            publish_time=utc(2026, 1, 14, 7, 30),
        )
        for h in range(24)
    ]


@pytest.fixture
def sample_pairs():
    """Pre-built paired data for metric calculations."""
    pairs = []
    for h in range(24):
        forecast = 10500.0 + h * 180.0
        actual = 10000.0 + h * 200.0
        error = forecast - actual
        pairs.append(
            ForecastActualPair(
                hour=utc(2026, 1, 15, h, 0),
                forecast_mw=forecast,
                actual_mw=actual,
                error_mw=round(error, 1),
                abs_error_mw=round(abs(error), 1),
                error_pct=round(error / actual * 100, 2) if actual != 0 else None,
            )
        )
    return pairs


@pytest.fixture
def multi_day_pairs():
    """Pairs spanning Jan 15 and Jan 16 for daily metrics testing."""
    pairs = []
    for day_offset in range(2):
        d = 15 + day_offset
        for h in range(24):
            forecast = 12000.0 + h * 100.0 + day_offset * 500.0
            actual = 11500.0 + h * 110.0 + day_offset * 400.0
            error = forecast - actual
            pairs.append(
                ForecastActualPair(
                    hour=utc(2026, 1, d, h, 0),
                    forecast_mw=forecast,
                    actual_mw=actual,
                    error_mw=round(error, 1),
                    abs_error_mw=round(abs(error), 1),
                    error_pct=round(error / actual * 100, 2) if actual != 0 else None,
                )
            )
    return pairs
