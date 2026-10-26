import asyncio
import logging
from datetime import date, datetime

import httpx

from app.config import settings
from app.models.elexon import FuelHHRecord, WindForRecord

logger = logging.getLogger(__name__)


class ElexonClient:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.elexon_base_url,
                timeout=settings.httpx_timeout,
                limits=httpx.Limits(
                    max_connections=20,         # Max 20 concurrent connections
                    max_keepalive_connections=5,  # Reuse 5 connections
                ),
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _get_with_retry(self, path: str, params: dict) -> list[dict]:
        client = await self._get_client()
        last_error: Exception | None = None

        for attempt in range(settings.httpx_max_retries):
            try:
                response = await client.get(path, params=params)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, list):
                    logger.warning("Expected list from %s, got %s", path, type(data).__name__)
                    return []
                return data
            except (httpx.HTTPStatusError, httpx.TransportError) as e:
                last_error = e
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500:
                    raise
                wait = 2**attempt
                logger.warning("Attempt %d failed for %s: %s. Retrying in %ds", attempt + 1, path, e, wait)
                await asyncio.sleep(wait)

        logger.error("All %d attempts failed for %s", settings.httpx_max_retries, path)
        if last_error:
            raise last_error
        return []

    async def fetch_fuelhh(
        self,
        settlement_date_from: date,
        settlement_date_to: date,
        fuel_type: str = "WIND",
    ) -> list[FuelHHRecord]:
        params = {
            "settlementDateFrom": settlement_date_from.isoformat(),
            "settlementDateTo": settlement_date_to.isoformat(),
            "fuelType": fuel_type,
        }
        logger.info("Fetching FUELHH: %s", params)
        raw = await self._get_with_retry("/datasets/FUELHH/stream", params)
        records = [FuelHHRecord.model_validate(r) for r in raw]
        logger.info("Fetched %d FUELHH records", len(records))
        return records

    async def fetch_windfor(
        self,
        start_time_from: datetime,
        start_time_to: datetime,
        publish_from: datetime | None = None,
        publish_to: datetime | None = None,
    ) -> list[WindForRecord]:
        params: dict[str, str] = {
            "from": start_time_from.isoformat(),
            "to": start_time_to.isoformat(),
        }
        if publish_from:
            params["publishDateTimeFrom"] = publish_from.isoformat()
        if publish_to:
            params["publishDateTimeTo"] = publish_to.isoformat()
        logger.info("Fetching WINDFOR: %s", params)
        raw = await self._get_with_retry("/datasets/WINDFOR/stream", params)
        records = [WindForRecord.model_validate(r) for r in raw]
        logger.info("Fetched %d WINDFOR records", len(records))
        return records


elexon_client = ElexonClient()
