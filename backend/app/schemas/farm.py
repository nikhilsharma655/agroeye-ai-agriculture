from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


class FarmBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    location: Optional[str] = None
    area: float = Field(..., gt=0, description="Farm area in hectares")
    soil_type: Optional[str] = Field(None, description="loamy, sandy, clay, black, red")
    soil_ph: Optional[float] = Field(None, ge=0, le=14)
    nitrogen: Optional[float] = Field(None, ge=0)
    phosphorus: Optional[float] = Field(None, ge=0)
    potassium: Optional[float] = Field(None, ge=0)
    moisture: Optional[float] = Field(None, ge=0, le=100)
    temperature: Optional[float] = None
    humidity: Optional[float] = Field(None, ge=0, le=100)
    current_crop: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None


class FarmCreate(FarmBase):
    pass


class FarmUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    area: Optional[float] = Field(None, gt=0)
    soil_type: Optional[str] = None
    soil_ph: Optional[float] = Field(None, ge=0, le=14)
    nitrogen: Optional[float] = Field(None, ge=0)
    phosphorus: Optional[float] = Field(None, ge=0)
    potassium: Optional[float] = Field(None, ge=0)
    moisture: Optional[float] = Field(None, ge=0, le=100)
    temperature: Optional[float] = None
    humidity: Optional[float] = Field(None, ge=0, le=100)
    current_crop: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None


class FarmOut(FarmBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
