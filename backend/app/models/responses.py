from datetime import date, datetime

from pydantic import BaseModel

from app.models.domain import AccuracyMetrics, DailyAccuracy


class DashboardKPIs(BaseModel):
    period: str
    total_actual_mwh: float
    total_forecast_mwh: float
    avg_actual_mw: float
    avg_forecast_mw: float
    mae_mw: float
    rmse_mw: float
    bias_mw: float
    mape_pct: float | None
    data_completeness_pct: float
    hours_analyzed: int
    latest_forecast_publish_time: datetime | None


class TimeSeriesPoint(BaseModel):
    hour: datetime
    forecast_mw: float | None = None
    actual_mw: float | None = None
    error_mw: float | None = None


class ForecastRun(BaseModel):
    publish_time: datetime
    is_selected: bool
    forecasts: list[TimeSeriesPoint]


class ForecastHistoryResponse(BaseModel):
    delivery_date: date
    cutoff_time: datetime
    runs: list[ForecastRun]


class ErrorDistributionBin(BaseModel):
    bin_start: float
    bin_end: float
    count: int


class AccuracyResponse(BaseModel):
    summary: AccuracyMetrics
    daily: list[DailyAccuracy]
    error_distribution: list[ErrorDistributionBin]


class MetadataResponse(BaseModel):
    data_source: str
    api_base_url: str
    analysis_period: str
    forecast_cutoff_description: str
    forecast_cutoff_hour_utc: int
    resolution_actual: str
    resolution_forecast: str
    aggregation_method: str
    units: str
    timezone: str
    total_delivery_dates: int
    total_hourly_pairs: int
    data_completeness_pct: float
    bias_convention: str


class HealthResponse(BaseModel):
    status: str
    cache_loaded: bool
    dates_cached: int
    total_pairs: int
