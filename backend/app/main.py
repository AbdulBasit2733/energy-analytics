import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import accuracy, dashboard, forecast_history, health, timeseries

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.cache_manager import cache_manager
    from app.services.elexon_client import elexon_client

    logger.info("Starting cache warm-up from Elexon BMRS API...")
    await cache_manager.warm_cache()
    logger.info("Cache warm-up complete.")
    yield
    # CRITICAL: Close HTTPX client to prevent connection leaks
    logger.info("Closing HTTPX client...")
    await elexon_client.close()
    logger.info("Shutting down.")


app = FastAPI(
    title="UK Wind Forecast Accuracy API",
    description="Backend for UK Wind Forecast Accuracy Dashboard — January 2026",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(timeseries.router, prefix="/api")
app.include_router(forecast_history.router, prefix="/api")
app.include_router(accuracy.router, prefix="/api")
