import math

from app.models.domain import ForecastActualPair
from app.services.accuracy_metrics import (
    calculate_daily_metrics,
    calculate_error_distribution,
    calculate_metrics,
)
from tests.conftest import utc


class TestCalculateMetrics:
    def test_known_values(self):
        pairs = [
            ForecastActualPair(
                hour=utc(2026, 1, 15, 0, 0),
                forecast_mw=1100.0, actual_mw=1000.0,
                error_mw=100.0, abs_error_mw=100.0, error_pct=10.0,
            ),
            ForecastActualPair(
                hour=utc(2026, 1, 15, 1, 0),
                forecast_mw=900.0, actual_mw=1000.0,
                error_mw=-100.0, abs_error_mw=100.0, error_pct=-10.0,
            ),
        ]
        m = calculate_metrics(pairs)
        assert m.mae == 100.0
        assert m.rmse == 100.0
        assert m.bias == 0.0
        assert m.paired_hours == 2

    def test_positive_bias(self):
        pairs = [
            ForecastActualPair(
                hour=utc(2026, 1, 15, 0, 0),
                forecast_mw=1200.0, actual_mw=1000.0,
                error_mw=200.0, abs_error_mw=200.0, error_pct=20.0,
            ),
            ForecastActualPair(
                hour=utc(2026, 1, 15, 1, 0),
                forecast_mw=1100.0, actual_mw=1000.0,
                error_mw=100.0, abs_error_mw=100.0, error_pct=10.0,
            ),
        ]
        m = calculate_metrics(pairs)
        assert m.bias == 150.0
        assert m.mae == 150.0
        assert m.max_overforecast == 200.0
        assert m.max_underforecast == 100.0

    def test_rmse_larger_than_mae_with_outlier(self):
        pairs = [
            ForecastActualPair(
                hour=utc(2026, 1, 15, h, 0),
                forecast_mw=1000.0, actual_mw=1000.0,
                error_mw=0.0, abs_error_mw=0.0, error_pct=0.0,
            )
            for h in range(9)
        ] + [
            ForecastActualPair(
                hour=utc(2026, 1, 15, 9, 0),
                forecast_mw=2000.0, actual_mw=1000.0,
                error_mw=1000.0, abs_error_mw=1000.0, error_pct=100.0,
            ),
        ]
        m = calculate_metrics(pairs)
        assert m.rmse > m.mae

    def test_mape_excludes_zero_actuals(self):
        pairs = [
            ForecastActualPair(
                hour=utc(2026, 1, 15, 0, 0),
                forecast_mw=500.0, actual_mw=0.0,
                error_mw=500.0, abs_error_mw=500.0, error_pct=None,
            ),
            ForecastActualPair(
                hour=utc(2026, 1, 15, 1, 0),
                forecast_mw=1100.0, actual_mw=1000.0,
                error_mw=100.0, abs_error_mw=100.0, error_pct=10.0,
            ),
        ]
        m = calculate_metrics(pairs)
        assert m.mape is not None
        assert m.mape == 10.0  # only the second pair contributes

    def test_all_zero_actuals_gives_none_mape(self):
        pairs = [
            ForecastActualPair(
                hour=utc(2026, 1, 15, 0, 0),
                forecast_mw=500.0, actual_mw=0.0,
                error_mw=500.0, abs_error_mw=500.0, error_pct=None,
            ),
            ForecastActualPair(
                hour=utc(2026, 1, 15, 1, 0),
                forecast_mw=300.0, actual_mw=0.5,
                error_mw=299.5, abs_error_mw=299.5, error_pct=None,
            ),
        ]
        m = calculate_metrics(pairs)
        # actuals > 1.0 filter: 0.0 and 0.5 both excluded
        assert m.mape is None

    def test_empty_pairs(self):
        m = calculate_metrics([])
        assert m.mae == 0.0
        assert m.rmse == 0.0
        assert m.bias == 0.0
        assert m.mape is None
        assert m.correlation is None
        assert m.paired_hours == 0

    def test_single_pair(self):
        pairs = [
            ForecastActualPair(
                hour=utc(2026, 1, 15, 0, 0),
                forecast_mw=11000.0, actual_mw=10000.0,
                error_mw=1000.0, abs_error_mw=1000.0, error_pct=10.0,
            ),
        ]
        m = calculate_metrics(pairs)
        assert m.mae == 1000.0
        assert m.rmse == 1000.0
        assert m.bias == 1000.0
        assert m.paired_hours == 1
        assert m.correlation is None  # can't compute with 1 point

    def test_sample_pairs_fixture(self, sample_pairs):
        m = calculate_metrics(sample_pairs)
        assert m.paired_hours == 24
        assert m.mae > 0
        assert m.rmse >= m.mae
        assert m.correlation is not None

    def test_perfect_forecast(self):
        pairs = [
            ForecastActualPair(
                hour=utc(2026, 1, 15, h, 0),
                forecast_mw=10000.0, actual_mw=10000.0,
                error_mw=0.0, abs_error_mw=0.0, error_pct=0.0,
            )
            for h in range(24)
        ]
        m = calculate_metrics(pairs)
        assert m.mae == 0.0
        assert m.rmse == 0.0
        assert m.bias == 0.0


class TestCalculateDailyMetrics:
    def test_groups_by_date(self, multi_day_pairs):
        daily = calculate_daily_metrics(multi_day_pairs)
        assert len(daily) == 2
        dates = [d.date for d in daily]
        from datetime import date
        assert date(2026, 1, 15) in dates
        assert date(2026, 1, 16) in dates

    def test_each_day_has_24_hours(self, multi_day_pairs):
        daily = calculate_daily_metrics(multi_day_pairs)
        for d in daily:
            assert d.paired_hours == 24

    def test_empty_input(self):
        daily = calculate_daily_metrics([])
        assert daily == []

    def test_single_day(self, sample_pairs):
        daily = calculate_daily_metrics(sample_pairs)
        assert len(daily) == 1
        assert daily[0].paired_hours == 24


class TestCalculateErrorDistribution:
    def test_basic_distribution(self, sample_pairs):
        bins = calculate_error_distribution(sample_pairs, bin_width=500.0)
        assert len(bins) > 0
        total_count = sum(b.count for b in bins)
        assert total_count == len(sample_pairs)

    def test_bin_width_respected(self, sample_pairs):
        bins = calculate_error_distribution(sample_pairs, bin_width=200.0)
        for b in bins:
            assert b.bin_end - b.bin_start == 200.0

    def test_empty_input(self):
        bins = calculate_error_distribution([], bin_width=500.0)
        assert bins == []

    def test_all_same_error(self):
        pairs = [
            ForecastActualPair(
                hour=utc(2026, 1, 15, h, 0),
                forecast_mw=10500.0, actual_mw=10000.0,
                error_mw=500.0, abs_error_mw=500.0, error_pct=5.0,
            )
            for h in range(10)
        ]
        bins = calculate_error_distribution(pairs, bin_width=500.0)
        matching = [b for b in bins if b.bin_start <= 500.0 < b.bin_end]
        assert len(matching) == 1
        assert matching[0].count == 10
