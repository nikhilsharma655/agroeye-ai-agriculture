from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.farm import Farm
from app.models.prediction import Prediction
from app.schemas.ml_schemas import CropRecommendationRequest, CropRecommendationResponse
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response
from app.services import ml_service, n8n_service

router = APIRouter(prefix="/api/recommendations", tags=["Crop Recommendation"])


@router.post("/crop", response_model=None, summary="Get AI crop recommendations",
             description="Runs the trained Scikit-learn classifier to recommend the top suitable crops "
                         "for the given soil and climate parameters.")
def recommend_crop(payload: CropRecommendationRequest, current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    try:
        result = ml_service.recommend_crop(
            nitrogen=payload.nitrogen, phosphorus=payload.phosphorus, potassium=payload.potassium,
            temperature=payload.temperature, humidity=payload.humidity, ph=payload.ph,
            rainfall=payload.rainfall, soil_type=payload.soil_type or "loamy",
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail={"success": False, "message": "Crop recommendation model failed",
                                     "error": "ML_PREDICTION_ERROR"}) from exc

    if payload.farm_id:
        farm = db.query(Farm).filter(Farm.id == payload.farm_id, Farm.user_id == current_user.id).first()
        if farm:
            db.add(Prediction(farm_id=farm.id, prediction_type="crop_recommendation",
                               model_name="crop_recommendation_model",
                               input_payload=payload.model_dump(), output_payload=result,
                               confidence=result["suitability_score"]))
            db.commit()
            n8n_service.send_recommendation_created(farm.id, "crop_recommendation",
                                                      f"Recommended crop: {result['recommended_crop']}")

    response = CropRecommendationResponse(**result)
    return success_response("Crop recommendation generated successfully", data=response.model_dump(mode="json"))
