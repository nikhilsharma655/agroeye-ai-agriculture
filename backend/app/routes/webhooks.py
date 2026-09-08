"""
Inbound webhook endpoints consumed BY n8n (as opposed to app/services/n8n_service.py,
which sends OUTBOUND webhooks TO n8n). These let n8n pull data (daily summary)
or push processed results/acks back into AgroEye.
"""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.config import settings
from app.models.farm import Farm
from app.models.notification import Notification
from app.models.user import User
from app.utils.responses import success_response

router = APIRouter(prefix="/api/webhooks", tags=["n8n Webhooks"])


def _verify_n8n_secret(x_agroeye_signature: Optional[str]):
    if x_agroeye_signature != settings.N8N_WEBHOOK_SHARED_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail={"success": False, "message": "Invalid webhook signature",
                                     "error": "WEBHOOK_AUTH_ERROR"})


@router.post("/n8n/farm-alert", summary="n8n calls this to acknowledge a dispatched farm alert")
def n8n_farm_alert_ack(payload: dict, x_agroeye_signature: Optional[str] = Header(None), db: Session = Depends(get_db)):
    _verify_n8n_secret(x_agroeye_signature)
    return success_response("Farm alert acknowledged", data=payload)


@router.get("/n8n/daily-summary", summary="n8n's daily scheduled trigger fetches this farm summary")
def n8n_daily_summary(x_agroeye_signature: Optional[str] = Header(None), db: Session = Depends(get_db)):
    _verify_n8n_secret(x_agroeye_signature)
    farms = db.query(Farm).all()
    summaries = []
    for farm in farms:
        summaries.append({
            "farm_id": farm.id, "farm_name": farm.name, "owner_email": farm.owner.email if farm.owner else None,
            "current_crop": farm.current_crop, "soil_moisture": farm.moisture, "soil_ph": farm.soil_ph,
        })
    return success_response("Daily farm summary generated", data=summaries)


@router.post("/n8n/daily-summary", summary="n8n posts a generated notification back after sending the daily summary")
def n8n_daily_summary_notify(payload: dict, x_agroeye_signature: Optional[str] = Header(None),
                              db: Session = Depends(get_db)):
    _verify_n8n_secret(x_agroeye_signature)
    user_id = payload.get("user_id")
    message = payload.get("message", "Your daily farm summary is ready.")
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.add(Notification(user_id=user.id, title="Daily Farm Summary", message=message,
                                 notification_type="system", source="n8n"))
            db.commit()
    return success_response("Notification recorded")


@router.post("/n8n/notify", summary="Generic inbound notification hook from n8n")
def n8n_generic_notify(payload: dict, x_agroeye_signature: Optional[str] = Header(None), db: Session = Depends(get_db)):
    _verify_n8n_secret(x_agroeye_signature)
    user_id = payload.get("user_id")
    title = payload.get("title", "Notification")
    message = payload.get("message", "")
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.add(Notification(user_id=user.id, title=title, message=message,
                                 notification_type=payload.get("type", "general"), source="n8n"))
            db.commit()
    return success_response("Notification recorded")
