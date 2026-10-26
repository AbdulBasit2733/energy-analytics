from datetime import datetime, timezone

from app.models.domain import HourlyActual, HourlyForecast
from app.services.data_processor import aggregate_fuelhh_to_hourly, pair_forecast_actual
from tests.conftest import utc


class TestAggregateFuelhhToHourly:
    def test_two_half_hours_averaged(self, fuelhh_two_half_hours):
        result = aggregate_fuelhh_to_hourly(fuelhh_two_half_hours)
        assert len(result) == 1
        assert result[0].hour == utc(2026, 1, 15, 0, 0)
        assert result[0].generation_mw == 11000.0  # (10000 + 12000) / 2
        assert result[0].half_hour_count == 2

    def test_single_half_hour_used_as_is(self, fuelhh_single_half_hour):
        result = aggregate_fuelhh_to_hourly(fuelhh_single_half_hour)
        assert len(result) == 1
        assert result[0].hour == utc(2026, 1, 15, 1, 0)
        assert result[0].generation_mw == 14000.0
        assert result[0].half_hour_count == 1

    def test_empty_input(self):
        result = aggregate_fuelhh_to_hourly([])
        assert result == []

    def test_full_day_produces_24_hours(self, fuelhh_full_day):
        result = aggregate_fuelhh_to_hourly(fuelhh_full_day)
        assert len(result) == 24
        for r in result:
            assert r.half_hour_count == 2

    def test_results_sorted_by_hour(self, fuelhh_full_day):
        result = aggregate_fuelhh_to_hourly(fuelhh_full_day)
        hours = [r.hour for r in result]
        assert hours == sorted(hours)

    def test_mixed_complete_and_incomplete(self, fuelhh_two_half_hours, fuelhh_single_half_hour):
        combined = fuelhh_two_half_hours + fuelhh_single_half_hour
        result = aggregate_fuelhh_to_hourly(combined)
        assert len(result) == 2
        complete = [r for r in result if r.half_hour_count == 2]
        incomplete = [r for r in result if r.half_hour_count == 1]
        assert len(complete) == 1
        assert len(incomplete) == 1


class TestPairForecastActual:
    def test_matching_hours_paired(self, sample_hourly_actuals, sample_hourly_forecasts):
        pairs = pair_forecast_actual(sample_hourly_forecasts, sample_hourly_actuals)
        assert len(pairs) == 24

    def test_error_calculation(self, sample_hourly_actuals, sample_hourly_forecasts):
        pairs = pair_forecast_actual(sample_hourly_forecasts, sample_hourly_actuals)
        first = pairs[0]
        expected_error = 10500.0 - 10000.0
        assert first.error_mw == expected_error
        assert first.abs_error_mw == abs(expected_error)

    def test_unmatched_hours_excluded(self):
        actuals = [
            HourlyActual(hour=utc(2026, 1, 15, 0, 0), generation_mw=10000.0, half_hour_count=2),
            HourlyActual(hour=utc(2026, 1, 15, 2, 0), generation_mw=12000.0, half_hour_count=2),
        ]
        forecasts = [
            HourlyForecast(hour=utc(2026, 1, 15, 0, 0), generation_mw=10500.0, publish_time=utc(2026, 1, 14, 7, 30)),
            HourlyForecast(hour=utc(2026, 1, 15, 1, 0), generation_mw=11000.0, publish_time=utc(2026, 1, 14, 7, 30)),
        ]
        pairs = pair_forecast_actual(forecasts, actuals)
        assert len(pairs) == 1
        assert pairs[0].hour == utc(2026, 1, 15, 0, 0)

    def test_zero_actual_gives_none_error_pct(self):
        actuals = [
            HourlyActual(hour=utc(2026, 1, 15, 0, 0), generation_mw=0.0, half_hour_count=2),
        ]
        forecasts = [
            HourlyForecast(hour=utc(2026, 1, 15, 0, 0), generation_mw=500.0, publish_time=utc(2026, 1, 14, 7, 30)),
        ]
        pairs = pair_forecast_actual(forecasts, actuals)
        assert len(pairs) == 1
        assert pairs[0].error_pct is None
        assert pairs[0].error_mw == 500.0

    def test_empty_forecasts(self, sample_hourly_actuals):
        pairs = pair_forecast_actual([], sample_hourly_actuals)
        assert pairs == []

    def test_empty_actuals(self, sample_hourly_forecasts):
        pairs = pair_forecast_actual(sample_hourly_forecasts, [])
        assert pairs == []

    def test_pairs_sorted_by_hour(self, sample_hourly_actuals, sample_hourly_forecasts):
        pairs = pair_forecast_actual(sample_hourly_forecasts, sample_hourly_actuals)
        hours = [p.hour for p in pairs]
        assert hours == sorted(hours)

    def test_negative_error_when_underforecast(self):
        actuals = [
            HourlyActual(hour=utc(2026, 1, 15, 0, 0), generation_mw=15000.0, half_hour_count=2),
        ]
        forecasts = [
            HourlyForecast(hour=utc(2026, 1, 15, 0, 0), generation_mw=12000.0, publish_time=utc(2026, 1, 14, 7, 30)),
        ]
        pairs = pair_forecast_actual(forecasts, actuals)
        assert pairs[0].error_mw == -3000.0
