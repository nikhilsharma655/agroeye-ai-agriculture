from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class CropRecommendationRequest(BaseModel):
    nitrogen: float = Field(..., ge=0, le=300)
    phosphorus: float = Field(..., ge=0, le=300)
    potassium: float = Field(..., ge=0, le=300)
    temperature: float = Field(..., ge=-10, le=60)
    humidity: float = Field(..., ge=0, le=100)
    ph: float = Field(..., ge=0, le=14)
    rainfall: float = Field(..., ge=0, le=1000)
    soil_type: Optional[str] = Field("loamy", description="loamy, sandy, clay, black, red")
    farm_id: Optional[str] = None


class CropOption(BaseModel):
    crop: str
    confidence: float


class CropRecommendationResponse(BaseModel):
    recommended_crop: str
    suitability_score: float
    top_recommendations: List[CropOption]
    explanation: str


class YieldPredictionRequest(BaseModel):
    crop: str
    area_hectare: float = Field(..., gt=0)
    nitrogen: float = Field(..., ge=0, le=300)
    phosphorus: float = Field(..., ge=0, le=300)
    potassium: float = Field(..., ge=0, le=300)
    temperature: float = Field(..., ge=-10, le=60)
    humidity: float = Field(..., ge=0, le=100)
    ph: float = Field(..., ge=0, le=14)
    rainfall: float = Field(..., ge=0, le=1000)
    farm_id: Optional[str] = None


class YieldPredictionResponse(BaseModel):
    crop: str
    yield_per_hectare: float
    estimated_total_yield: float
    confidence_range_per_hectare: Dict[str, float]
    unit: str
    note: Optional[str] = None


class FertilizerRequest(BaseModel):
    crop: str
    nitrogen: float = Field(..., ge=0, le=300)
    phosphorus: float = Field(..., ge=0, le=300)
    potassium: float = Field(..., ge=0, le=300)
    ph: float = Field(..., ge=0, le=14)
    soil_type: Optional[str] = "loamy"
    growth_stage: Optional[str] = "vegetative"
    farm_id: Optional[str] = None


class FertilizerResponse(BaseModel):
    recommended_fertilizer: List[str]
    approximate_quantity_kg_per_hectare: Dict[str, float]
    nutrient_deficiency: Dict[str, str]
    reason: str
    disclaimer: str = "AI-assisted estimate. Not a substitute for professional soil testing or agronomic advice."


class DiseaseRiskRequest(BaseModel):
    crop: str
    temperature: float = Field(..., ge=-10, le=60)
    humidity: float = Field(..., ge=0, le=100)
    rainfall: float = Field(..., ge=0, le=1000)
    soil_moisture: float = Field(..., ge=0, le=100)
    growth_stage: Optional[str] = "vegetative"
    previous_disease_history: Optional[bool] = False
    farm_id: Optional[str] = None


class DiseaseRiskResponse(BaseModel):
    risk_level: str
    risk_percentage: float
    possible_disease_category: str
    preventive_suggestions: List[str]
    class_probabilities: Dict[str, float]


class IrrigationRequest(BaseModel):
    crop: str
    soil_moisture: float = Field(..., ge=0, le=100)
    temperature: float = Field(..., ge=-10, le=60)
    humidity: float = Field(..., ge=0, le=100)
    rainfall: float = Field(..., ge=0, le=1000)
    growth_stage: Optional[str] = "vegetative"
    area_hectare: float = Field(..., gt=0)
    farm_id: Optional[str] = None


class IrrigationResponse(BaseModel):
    irrigation_required: bool
    water_status: str
    recommended_level: str
    estimated_requirement_litres: Dict[str, float]
    reason: str


class InsightItem(BaseModel):
    category: str
    severity: str
    title: str
    explanation: str
    recommended_action: str


class InsightsResponse(BaseModel):
    farm_id: str
    insights: List[InsightItem]


class LiveWeatherResponse(BaseModel):
    farm_id: str
    resolved_location: str
    temperature: float
    humidity: float
    rainfall: float
    observed_at: Optional[str] = None
    farm_updated: bool
