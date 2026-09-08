from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


class CropCreate(BaseModel):
    name: str = Field(..., min_length=1)
    variety: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    growth_stage: Optional[str] = "seedling"


class CropUpdate(BaseModel):
    variety: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    growth_stage: Optional[str] = None
    status: Optional[str] = None


class CropOut(BaseModel):
    id: str
    farm_id: str
    name: str
    variety: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    growth_stage: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
