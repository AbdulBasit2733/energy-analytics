from datetime import date

from fastapi import APIRouter, Query

from app.models.domain import AccuracyMetrics, DailyAccuracy
from app.models.responses import ErrorDistributionBin
from app.services.accuracy_metrics import (
    calculate_daily_metrics,
    calculate_error_distribution,
    calculate_metrics,
)
from app.services.cache_manager import cache_manager
from app.utils.validators import validate_date_range

router = APIRouter(tags=["accuracy"])


@router.get("/accuracy/summary", response_model=AccuracyMetrics)
async def get_accuracy_summary(
    start: date | None = Query(None, alias="from"),
    end: date | None = Query(None, alias="to"),
):
    validate_date_range(start, end)
    pairs = cache_manager.get_pairs_for_range(start, end)
    return calculate_metrics(pairs)


@router.get("/accuracy/daily", response_model=list[DailyAccuracy])
async def get_accuracy_daily(
    start: date | None = Query(None, alias="from"),
    end: date | None = Query(None, alias="to"),
):
    validate_date_range(start, end)
    pairs = cache_manager.get_pairs_for_range(start, end)
    return calculate_daily_metrics(pairs)


@router.get("/accuracy/error-distribution", response_model=list[ErrorDistributionBin])
async def get_error_distribution(
    bin_width: float = Query(500.0, gt=0, le=10000, description="Bin width in MW (1-10000)"),
    start: date | None = Query(None, alias="from"),
    end: date | None = Query(None, alias="to"),
):
    validate_date_range(start, end)
    pairs = cache_manager.get_pairs_for_range(start, end)
    return calculate_error_distribution(pairs, bin_width)
