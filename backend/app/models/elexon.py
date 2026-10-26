from datetime import date, datetime

from pydantic import BaseModel, Field


class FuelHHRecord(BaseModel):
    dataset: str
    publish_time: datetime = Field(alias="publishTime")
    start_time: datetime = Field(alias="startTime")
    settlement_date: date = Field(alias="settlementDate")
    settlement_period: int = Field(alias="settlementPeriod")
    fuel_type: str = Field(alias="fuelType")
    generation: int

    model_config = {"populate_by_name": True}


class WindForRecord(BaseModel):
    dataset: str
    publish_time: datetime = Field(alias="publishTime")
    start_time: datetime = Field(alias="startTime")
    generation: int

    model_config = {"populate_by_name": True}
