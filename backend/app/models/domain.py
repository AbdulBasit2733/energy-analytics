from datetime import date, datetime

from pydantic import BaseModel


class HourlyActual(BaseModel):
    hour: datetime
    generation_mw: float
    half_hour_count: int


class HourlyForecast(BaseModel):
    hour: datetime
    generation_mw: float
    publish_time: datetime


class ForecastActualPair(BaseModel):
    hour: datetime
    forecast_mw: float
    actual_mw: float
    error_mw: float
    abs_error_mw: float
    error_pct: float | None


class AccuracyMetrics(BaseModel):
    mae: float
    rmse: float
    mape: float | None
    bias: float
    max_overforecast: float
    max_underforecast: float
    correlation: float | None
    paired_hours: int


class DailyAccuracy(BaseModel):
    date: date
    mae: float
    rmse: float
    bias: float
    paired_hours: int
