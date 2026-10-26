from datetime import date

from fastapi import APIRouter, Query

from app.config import settings
from app.models.responses import DashboardKPIs, MetadataResponse
from app.services.accuracy_metrics import calculate_metrics
from app.services.cache_manager import cache_manager
from app.utils.validators import validate_date_range

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/kpis", response_model=DashboardKPIs)
async def get_dashboard_kpis(
    start: date | None = Query(None, description="Start date (YYYY-MM-DD)", alias="from"),
    end: date | None = Query(None, description="End date (YYYY-MM-DD)", alias="to"),
):
    validate_date_range(start, end)
    pairs = cache_manager.get_pairs_for_range(start, end)
    metrics = calculate_metrics(pairs)

    actuals = cache_manager.get_actuals_for_range(start, end)
    total_actual_mw_sum = sum(a.generation_mw for a in actuals)
    total_actual_mwh = total_actual_mw_sum * 1.0

    forecasts_mw_sum = sum(p.forecast_mw for p in pairs)
    total_forecast_mwh = forecasts_mw_sum * 1.0

    hours_analyzed = metrics.paired_hours
    avg_actual_mw = total_actual_mw_sum / len(actuals) if actuals else 0.0
    avg_forecast_mw = forecasts_mw_sum / hours_analyzed if hours_analyzed else 0.0

    analysis_start = date(settings.analysis_year, settings.analysis_month, 1)
    if settings.analysis_month == 12:
        analysis_end = date(settings.analysis_year + 1, 1, 1)
    else:
        analysis_end = date(settings.analysis_year, settings.analysis_month + 1, 1)
    total_expected_hours = ((analysis_end - analysis_start).days) * 24
    completeness = (hours_analyzed / total_expected_hours * 100) if total_expected_hours else 0.0

    latest_publish = None
    if pairs:
        latest_date = max(p.hour.date() for p in pairs)
        latest_publish = cache_manager.get_forecast_publish_time(latest_date)

    return DashboardKPIs(
        period=f"January {settings.analysis_year}",
        total_actual_mwh=round(total_actual_mwh, 1),
        total_forecast_mwh=round(total_forecast_mwh, 1),
        avg_actual_mw=round(avg_actual_mw, 1),
        avg_forecast_mw=round(avg_forecast_mw, 1),
        mae_mw=metrics.mae,
        rmse_mw=metrics.rmse,
        bias_mw=metrics.bias,
        mape_pct=metrics.mape,
        data_completeness_pct=round(completeness, 1),
        hours_analyzed=hours_analyzed,
        latest_forecast_publish_time=latest_publish,
    )


@router.get("/metadata", response_model=MetadataResponse)
async def get_metadata():
    pairs = cache_manager.all_pairs
    analysis_start = date(settings.analysis_year, settings.analysis_month, 1)
    if settings.analysis_month == 12:
        analysis_end = date(settings.analysis_year + 1, 1, 1)
    else:
        analysis_end = date(settings.analysis_year, settings.analysis_month + 1, 1)
    total_expected_hours = ((analysis_end - analysis_start).days) * 24
    completeness = (len(pairs) / total_expected_hours * 100) if total_expected_hours else 0.0

    return MetadataResponse(
        data_source="Elexon BMRS (Balancing Mechanism Reporting Service)",
        api_base_url=settings.elexon_base_url,
        analysis_period=f"{settings.analysis_year}-{settings.analysis_month:02d}",
        forecast_cutoff_description=(
            f"Day-ahead forecast cutoff at {settings.forecast_cutoff_hour:02d}:00 UTC on D-1. "
            "The most recent WINDFOR forecast published before this cutoff is selected."
        ),
        forecast_cutoff_hour_utc=settings.forecast_cutoff_hour,
        resolution_actual="Half-hourly (30 min) — FUELHH dataset",
        resolution_forecast="Hourly — WINDFOR dataset",
        aggregation_method="FUELHH half-hourly values averaged to hourly for comparison with WINDFOR",
        units="MW (megawatts)",
        timezone="UTC (January is GMT, so UTC = UK local time)",
        total_delivery_dates=cache_manager.dates_cached,
        total_hourly_pairs=len(pairs),
        data_completeness_pct=round(completeness, 1),
        bias_convention="Positive bias = forecast exceeded actual (over-forecast)",
    )
