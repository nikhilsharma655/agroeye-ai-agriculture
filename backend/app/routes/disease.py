from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.farm import Farm
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.schemas.ml_schemas import DiseaseRiskRequest, DiseaseRiskResponse
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response
from app.services import ml_service, n8n_service

router = APIRouter(prefix="/api/disease", tags=["Disease Risk"])


@router.post("/predict", response_model=None, summary="Predict crop disease risk",
             description="Uses structured environmental data (temperature, humidity, rainfall, soil moisture, "
                         "growth stage, disease history) to predict disease risk level. The backend is structured "
                         "so an image-based CNN model can be added later as an alternate inference path.")
def predict_disease_risk(payload: DiseaseRiskRequest, current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    try:
        result = ml_service.predict_disease_risk(
            crop=payload.crop, temperature=payload.temperature, humidity=payload.humidity,
            rainfall=payload.rainfall, soil_moisture=payload.soil_moisture,
            growth_stage=payload.growth_stage or "vegetative",
            previous_disease_history=payload.previous_disease_history or False,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail={"success": False, "message": "Disease risk model failed",
                                     "error": "ML_PREDICTION_ERROR"}) from exc

    if payload.farm_id:
        farm = db.query(Farm).filter(Farm.id == payload.farm_id, Farm.user_id == current_user.id).first()
        if farm:
            db.add(Prediction(farm_id=farm.id, prediction_type="disease_risk",
                               model_name="disease_risk_model", input_payload=payload.model_dump(),
                               output_payload=result, confidence=result["risk_percentage"]))
            if result["risk_level"] == "high":
                alert = Alert(farm_id=farm.id, alert_type="disease_risk", severity="high",
                               message=f"High disease risk detected for {payload.crop}: "
                                       f"{result['possible_disease_category']}",
                               payload=result)
                db.add(alert)
                db.commit()
                triggered = n8n_service.send_farm_alert(
                    farm.id, "disease_risk", "high",
                    f"High disease risk detected for {payload.crop}", result,
                )
                alert.n8n_triggered = triggered
                db.commit()
            else:
                db.commit()

    response = DiseaseRiskResponse(**result)
    return success_response("Disease risk prediction generated successfully", data=response.model_dump(mode="json"))


@router.post("/predict-image", response_model=None, summary="[Preview] Predict disease from a leaf photo",
             description="Accepts a leaf/crop image for future CNN-based disease detection. No image model is "
                         "trained yet in this project — this endpoint exists as the integration point described "
                         "in the ML architecture, and currently returns a 501 with guidance. Wiring in a real "
                         "model only requires implementing ml/inference/disease_image_infer.py; this route and "
                         "the structured-data /predict endpoint above never need to change.")
def predict_disease_from_image(image: UploadFile = File(...), crop: Optional[str] = Form(None),
                                current_user: User = Depends(get_current_user)):
    try:
        image_bytes = image.file.read()
        result = ml_service.predict_disease_from_image(image_bytes, crop=crop)
        return success_response("Disease prediction generated from image", data=result)
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={"success": False, "message": str(exc), "error": "IMAGE_MODEL_NOT_AVAILABLE"},
        ) from exc
