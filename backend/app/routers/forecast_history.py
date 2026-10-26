from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.models.responses import ForecastHistoryResponse, ForecastRun, TimeSeriesPoint
from app.services.cache_manager import cache_manager
from app.services.forecast_selector import get_all_forecast_runs, get_cutoff_time

router = APIRouter(tags=["forecast-history"])


@router.get("/forecast-history", response_model=ForecastHistoryResponse)
async def get_forecast_history(
    date_param: date = Query(..., alias="date", description="Delivery date (YYYY-MM-DD)"),
):
    windfor_records = cache_manager.get_windfor_for_date(date_param)
    if not windfor_records:
        raise HTTPException(status_code=404, detail=f"No forecast data for {date_param.isoformat()}")

    runs = get_all_forecast_runs(windfor_records, date_param)
    cutoff = get_cutoff_time(date_param, settings.forecast_cutoff_hour)
    selected_publish = cache_manager.get_forecast_publish_time(date_param)

    forecast_runs = []
    for publish_time in sorted(runs.keys()):
        hourly = runs[publish_time]
        forecast_runs.append(
            ForecastRun(
                publish_time=publish_time,
                is_selected=(publish_time == selected_publish),
                forecasts=[
                    TimeSeriesPoint(
                        hour=h.hour,
                        forecast_mw=h.generation_mw,
                    )
                    for h in hourly
                ],
            )
        )

    return ForecastHistoryResponse(
        delivery_date=date_param,
        cutoff_time=cutoff,
        runs=forecast_runs,
    )
