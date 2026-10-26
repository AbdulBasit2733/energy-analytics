from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    elexon_base_url: str = "https://data.elexon.co.uk/bmrs/api/v1"
    forecast_cutoff_hour: int = Field(default=9, ge=0, le=23)
    analysis_year: int = Field(default=2026, ge=2020, le=2030)
    analysis_month: int = Field(default=1, ge=1, le=12)
    cache_dir: str = "./cache"
    cache_ttl_seconds: int = Field(default=86400 * 30, ge=0)
    httpx_timeout: float = Field(default=30.0, gt=0, le=300)
    httpx_max_retries: int = Field(default=3, ge=0, le=10)
    backend_port: int = Field(default=8000, ge=1024, le=65535)
    backend_host: str = "0.0.0.0"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @field_validator("forecast_cutoff_hour")
    @classmethod
    def validate_cutoff_hour(cls, v: int) -> int:
        if not 0 <= v <= 23:
            raise ValueError(f"forecast_cutoff_hour must be 0-23, got {v}")
        return v

    @field_validator("analysis_month")
    @classmethod
    def validate_month(cls, v: int) -> int:
        if not 1 <= v <= 12:
            raise ValueError(f"analysis_month must be 1-12, got {v}")
        return v

    @field_validator("analysis_year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        if not 2020 <= v <= 2030:
            raise ValueError(f"analysis_year out of reasonable range: {v}")
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
