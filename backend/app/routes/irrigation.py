from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.farm import Farm
from app.models.recommendation import Recommendation
from app.models.alert import Alert
from app.schemas.ml_schemas import IrrigationRequest, IrrigationResponse
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response
from app.services import irrigation_service, n8n_service

router = APIRouter(prefix="/api/irrigation", tags=["Irrigation"])


@router.post("/recommend", response_model=None, summary="Get irrigation recommendation",
             description="Computes soil moisture deficit adjusted for temperature, humidity, rainfall, and "
                         "growth stage, entirely in the backend, to recommend whether irrigation is needed.")
def recommend_irrigation(payload: IrrigationRequest, current_user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    result = irrigation_service.recommend_irrigation(
        crop=payload.crop, soil_moisture=payload.soil_moisture, temperature=payload.temperature,
        humidity=payload.humidity, rainfall=payload.rainfall, area_hectare=payload.area_hectare,
        growth_stage=payload.growth_stage or "vegetative",
    )

    if payload.farm_id:
        farm = db.query(Farm).filter(Farm.id == payload.farm_id, Farm.user_id == current_user.id).first()
        if farm:
            db.add(Recommendation(farm_id=farm.id, category="irrigation",
                                   title=f"Irrigation: {result['water_status']}", detail=result,
                                   severity="high" if result["water_status"] == "Critical" else "info"))
            if result["water_status"] in ("Low", "Critical"):
                alert = Alert(farm_id=farm.id, alert_type="irrigation", severity="high",
                              message=f"Soil moisture is {result['water_status'].lower()} for {payload.crop}",
                              payload=result)
                db.add(alert)
                db.commit()
                triggered = n8n_service.send_irrigation_alert(
                    farm.id, result["water_status"], result["estimated_requirement_litres"],
                )
                alert.n8n_triggered = triggered
                db.commit()
            else:
                db.commit()

    response = IrrigationResponse(**result)
    return success_response("Irrigation recommendation generated successfully", data=response.model_dump(mode="json"))
