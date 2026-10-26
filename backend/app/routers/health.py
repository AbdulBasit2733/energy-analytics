from fastapi import APIRouter

from app.models.responses import HealthResponse
from app.services.cache_manager import cache_manager

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok" if cache_manager.is_loaded else "warming",
        cache_loaded=cache_manager.is_loaded,
        dates_cached=cache_manager.dates_cached,
        total_pairs=len(cache_manager.all_pairs),
    )
