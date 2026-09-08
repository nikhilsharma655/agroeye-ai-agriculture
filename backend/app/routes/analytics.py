from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.farm import Farm
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview", summary="Dashboard overview metrics for the current user")
def analytics_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farms = db.query(Farm).filter(Farm.user_id == current_user.id).all()
    farm_ids = [f.id for f in farms]

    total_farms = len(farms)
    current_crops = list({f.current_crop for f in farms if f.current_crop})
    avg_moisture = round(sum(f.moisture or 0 for f in farms) / total_farms, 1) if total_farms else None
    avg_ph = round(sum(f.soil_ph or 0 for f in farms) / total_farms, 2) if total_farms else None

    open_alerts = 0
    if farm_ids:
        open_alerts = db.query(func.count(Alert.id)).filter(
            Alert.farm_id.in_(farm_ids), Alert.is_resolved.is_(False)
        ).scalar() or 0

    recent_predictions = []
    if farm_ids:
        recent_predictions = (
            db.query(Prediction)
            .filter(Prediction.farm_id.in_(farm_ids))
            .order_by(Prediction.created_at.desc())
            .limit(10)
            .all()
        )

    data = {
        "total_farms": total_farms,
        "current_crops": current_crops,
        "average_soil_moisture": avg_moisture,
        "average_soil_ph": avg_ph,
        "open_alerts": open_alerts,
        "recent_predictions": [
            {
                "id": p.id, "farm_id": p.farm_id, "type": p.prediction_type,
                "model_name": p.model_name, "output": p.output_payload,
                "created_at": p.created_at.isoformat(),
            }
            for p in recent_predictions
        ],
    }
    return success_response("Analytics overview retrieved", data=data)


@router.get("/farms/{farm_id}/history", summary="Historical predictions for a single farm")
def farm_history(farm_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"success": False, "message": "Farm not found", "error": "FARM_NOT_FOUND"})
    predictions = (
        db.query(Prediction).filter(Prediction.farm_id == farm_id)
        .order_by(Prediction.created_at.asc()).all()
    )
    data = [
        {"id": p.id, "type": p.prediction_type, "output": p.output_payload, "created_at": p.created_at.isoformat()}
        for p in predictions
    ]
    return success_response("Farm history retrieved", data=data)
