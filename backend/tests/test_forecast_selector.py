from datetime import date, datetime, timezone

from app.services.forecast_selector import (
    get_all_forecast_runs,
    get_cutoff_time,
    select_day_ahead_forecast,
)
from tests.conftest import utc


class TestGetCutoffTime:
    def test_default_cutoff(self):
        cutoff = get_cutoff_time(date(2026, 1, 15))
        assert cutoff == utc(2026, 1, 14, 9, 0)

    def test_custom_cutoff_hour(self):
        cutoff = get_cutoff_time(date(2026, 1, 15), cutoff_hour=11)
        assert cutoff == utc(2026, 1, 14, 11, 0)

    def test_jan_1_cutoff_is_dec_31(self):
        cutoff = get_cutoff_time(date(2026, 1, 1))
        assert cutoff == utc(2025, 12, 31, 9, 0)


class TestSelectDayAheadForecast:
    def test_selects_latest_before_cutoff(self, windfor_multiple_runs):
        forecasts, publish_time = select_day_ahead_forecast(
            windfor_multiple_runs, date(2026, 1, 15), cutoff_hour=9,
        )
        assert publish_time == utc(2026, 1, 14, 7, 30)
        assert len(forecasts) == 24

    def test_rejects_forecasts_after_cutoff(self, windfor_multiple_runs):
        forecasts, publish_time = select_day_ahead_forecast(
            windfor_multiple_runs, date(2026, 1, 15), cutoff_hour=9,
        )
        # The 11:30 run is after cutoff, should not be selected
        assert publish_time != utc(2026, 1, 14, 11, 30)

    def test_all_forecasts_for_delivery_date_only(self, windfor_multiple_runs):
        forecasts, _ = select_day_ahead_forecast(
            windfor_multiple_runs, date(2026, 1, 15), cutoff_hour=9,
        )
        for f in forecasts:
            assert f.hour.date() == date(2026, 1, 15)

    def test_forecasts_sorted_by_hour(self, windfor_multiple_runs):
        forecasts, _ = select_day_ahead_forecast(
            windfor_multiple_runs, date(2026, 1, 15), cutoff_hour=9,
        )
        hours = [f.hour for f in forecasts]
        assert hours == sorted(hours)

    def test_fallback_when_none_before_cutoff(self, windfor_only_after_cutoff):
        forecasts, publish_time = select_day_ahead_forecast(
            windfor_only_after_cutoff, date(2026, 1, 15), cutoff_hour=9,
        )
        # Falls back to earliest available (which is 11:30, the only run)
        assert publish_time == utc(2026, 1, 14, 11, 30)
        assert len(forecasts) == 24

    def test_empty_input_returns_empty(self):
        forecasts, publish_time = select_day_ahead_forecast(
            [], date(2026, 1, 15), cutoff_hour=9,
        )
        assert forecasts == []
        assert publish_time is None

    def test_no_matching_delivery_date(self, windfor_multiple_runs):
        # All fixtures are for Jan 15; asking for Jan 20 should return nothing
        forecasts, publish_time = select_day_ahead_forecast(
            windfor_multiple_runs, date(2026, 1, 20), cutoff_hour=9,
        )
        assert forecasts == []
        assert publish_time is None

    def test_custom_cutoff_includes_more(self, windfor_multiple_runs):
        # With cutoff at 12, the 11:30 run should now be eligible
        forecasts, publish_time = select_day_ahead_forecast(
            windfor_multiple_runs, date(2026, 1, 15), cutoff_hour=12,
        )
        assert publish_time == utc(2026, 1, 14, 11, 30)

    def test_forecast_values_match_selected_run(self, windfor_multiple_runs):
        forecasts, publish_time = select_day_ahead_forecast(
            windfor_multiple_runs, date(2026, 1, 15), cutoff_hour=9,
        )
        # The 07:30 run is index 2 in publish_times, so generation = 15000 + hour*50 + 2*200
        for f in forecasts:
            h = f.hour.hour
            expected = 15000 + h * 50 + 2 * 200
            assert f.generation_mw == float(expected)


class TestGetAllForecastRuns:
    def test_groups_by_publish_time(self, windfor_multiple_runs):
        runs = get_all_forecast_runs(windfor_multiple_runs, date(2026, 1, 15))
        assert len(runs) == 4

    def test_each_run_has_24_hours(self, windfor_multiple_runs):
        runs = get_all_forecast_runs(windfor_multiple_runs, date(2026, 1, 15))
        for publish_time, hourly in runs.items():
            assert len(hourly) == 24

    def test_empty_for_wrong_date(self, windfor_multiple_runs):
        runs = get_all_forecast_runs(windfor_multiple_runs, date(2026, 1, 20))
        assert len(runs) == 0
