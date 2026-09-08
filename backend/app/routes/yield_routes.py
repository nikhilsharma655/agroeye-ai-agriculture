from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.farm import Farm
from app.models.prediction import Prediction
from app.schemas.ml_schemas import YieldPredictionRequest, YieldPredictionResponse
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response
from app.services import ml_service

router = APIRouter(prefix="/api/yield", tags=["Yield Prediction"])


@router.post("/predict", response_model=None, summary="Predict estimated crop yield",
             description="Runs the trained Scikit-learn regression model to estimate yield per hectare "
                         "and total yield for the given crop and conditions.")
def predict_yield(payload: YieldPredictionRequest, current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    try:
        result = ml_service.predict_yield(
            crop=payload.crop, area_hectare=payload.area_hectare, nitrogen=payload.nitrogen,
            phosphorus=payload.phosphorus, potassium=payload.potassium, temperature=payload.temperature,
            humidity=payload.humidity, ph=payload.ph, rainfall=payload.rainfall,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail={"success": False, "message": "Yield prediction model failed",
                                     "error": "ML_PREDICTION_ERROR"}) from exc

    if payload.farm_id:
        farm = db.query(Farm).filter(Farm.id == payload.farm_id, Farm.user_id == current_user.id).first()
        if farm:
            db.add(Prediction(farm_id=farm.id, prediction_type="yield_prediction",
                               model_name="yield_prediction_model",
                               input_payload=payload.model_dump(), output_payload=result))
            db.commit()

    response = YieldPredictionResponse(**result)
    return success_response("Yield prediction generated successfully", data=response.model_dump(mode="json"))
