from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.farm import Farm
from app.schemas.ml_schemas import InsightsResponse, InsightItem
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response
from app.services import insights_service

router = APIRouter(prefix="/api/insights", tags=["AI Insights"])


@router.get("", response_model=None, summary="Get AI insights across all of the user's farms")
def get_all_insights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farms = db.query(Farm).filter(Farm.user_id == current_user.id).all()
    all_insights = []
    for farm in farms:
        insights = insights_service.generate_insights(farm)
        response = InsightsResponse(farm_id=farm.id, insights=[InsightItem(**i) for i in insights])
        all_insights.append(response.model_dump(mode="json"))
    return success_response("Insights retrieved for all farms", data=all_insights)
