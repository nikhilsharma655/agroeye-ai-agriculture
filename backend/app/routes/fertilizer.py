from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.farm import Farm
from app.models.recommendation import Recommendation
from app.schemas.ml_schemas import FertilizerRequest, FertilizerResponse
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response
from app.services import fertilizer_service

router = APIRouter(prefix="/api/fertilizer", tags=["Fertilizer Recommendation"])


@router.post("/recommend", response_model=None, summary="Get fertilizer recommendation",
             description="Computes nutrient deficiencies against crop-specific N-P-K targets and "
                         "returns an AI-assisted fertilizer recommendation. Not a guaranteed agronomic prescription.")
def recommend_fertilizer(payload: FertilizerRequest, current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    result = fertilizer_service.recommend_fertilizer(
        crop=payload.crop, nitrogen=payload.nitrogen, phosphorus=payload.phosphorus,
        potassium=payload.potassium, ph=payload.ph, soil_type=payload.soil_type or "loamy",
        growth_stage=payload.growth_stage or "vegetative",
    )

    if payload.farm_id:
        farm = db.query(Farm).filter(Farm.id == payload.farm_id, Farm.user_id == current_user.id).first()
        if farm:
            db.add(Recommendation(farm_id=farm.id, category="fertilizer",
                                   title=f"Fertilizer plan for {payload.crop}", detail=result, severity="info"))
            db.commit()

    response = FertilizerResponse(**result)
    return success_response("Fertilizer recommendation generated successfully", data=response.model_dump(mode="json"))
