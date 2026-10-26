from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.models.responses import TimeSeriesPoint
from app.services.cache_manager import cache_manager
from app.utils.validators import validate_date_range

router = APIRouter(tags=["timeseries"])


@router.get("/timeseries", response_model=list[TimeSeriesPoint])
async def get_timeseries(
    date_param: date | None = Query(None, alias="date", description="Single date (YYYY-MM-DD)"),
    start: date | None = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    end: date | None = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
):
    # Validate mutually exclusive params
    if date_param and (start or end):
        raise HTTPException(
            status_code=400,
            detail="Cannot use both 'date' and 'from'/'to' parameters. Use one or the other.",
        )

    if date_param:
        start = date_param
        end = date_param

    validate_date_range(start, end)
    pairs = cache_manager.get_pairs_for_range(start, end)
    actuals = cache_manager.get_actuals_for_range(start, end)

    actual_by_hour = {a.hour: a.generation_mw for a in actuals}
    pair_by_hour = {p.hour: p for p in pairs}

    all_hours = sorted(set(actual_by_hour.keys()) | set(pair_by_hour.keys()))

    result = []
    for hour in all_hours:
        p = pair_by_hour.get(hour)
        actual_val = actual_by_hour.get(hour)

        result.append(
            TimeSeriesPoint(
                hour=hour,
                forecast_mw=p.forecast_mw if p else None,
                actual_mw=actual_val if actual_val is not None else (p.actual_mw if p else None),
                error_mw=p.error_mw if p else None,
            )
        )

    return result
