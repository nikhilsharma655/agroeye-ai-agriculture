from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.farm import Farm
from app.models.weather_record import WeatherRecord
from app.schemas.farm import FarmCreate, FarmUpdate, FarmOut
from app.schemas.ml_schemas import InsightsResponse, InsightItem, LiveWeatherResponse
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response
from app.services import insights_service, weather_service

router = APIRouter(prefix="/api/farms", tags=["Farms"])


def _get_owned_farm_or_404(farm_id: str, current_user: User, db: Session) -> Farm:
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "message": "Farm not found", "error": "FARM_NOT_FOUND"},
        )
    return farm


@router.get("", summary="List all farms owned by the current user")
def list_farms(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farms = db.query(Farm).filter(Farm.user_id == current_user.id).order_by(Farm.created_at.desc()).all()
    return success_response("Farms retrieved", data=[FarmOut.model_validate(f).model_dump(mode="json") for f in farms])


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a new farm")
def create_farm(payload: FarmCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farm = Farm(user_id=current_user.id, **payload.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return success_response("Farm created successfully", data=FarmOut.model_validate(farm).model_dump(mode="json"),
                             status_code=status.HTTP_201_CREATED)


@router.get("/{farm_id}", summary="Get a single farm by ID")
def get_farm(farm_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farm = _get_owned_farm_or_404(farm_id, current_user, db)
    return success_response("Farm retrieved", data=FarmOut.model_validate(farm).model_dump(mode="json"))


@router.put("/{farm_id}", summary="Update a farm")
def update_farm(farm_id: str, payload: FarmUpdate, current_user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    farm = _get_owned_farm_or_404(farm_id, current_user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(farm, field, value)
    db.commit()
    db.refresh(farm)
    return success_response("Farm updated successfully", data=FarmOut.model_validate(farm).model_dump(mode="json"))


@router.delete("/{farm_id}", summary="Delete a farm")
def delete_farm(farm_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farm = _get_owned_farm_or_404(farm_id, current_user, db)
    db.delete(farm)
    db.commit()
    return success_response("Farm deleted successfully")


@router.get("/{farm_id}/insights", response_model=None, summary="Get AI-generated insights for a farm")
def get_farm_insights(farm_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farm = _get_owned_farm_or_404(farm_id, current_user, db)
    insights = insights_service.generate_insights(farm)
    response = InsightsResponse(farm_id=farm.id, insights=[InsightItem(**i) for i in insights])
    return success_response("Insights generated successfully", data=response.model_dump(mode="json"))


@router.post("/{farm_id}/weather/refresh", response_model=None, summary="Fetch live weather for a farm's location",
             description="Looks up current temperature, humidity, and rainfall for the farm's location via a "
                         "live weather API (Open-Meteo — no API key required), logs it to weather history, and "
                         "updates the farm's stored readings so subsequent recommendations use fresh data. "
                         "Requires the farm to have a location set; fails gracefully with a clear error otherwise.")
def refresh_farm_weather(farm_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farm = _get_owned_farm_or_404(farm_id, current_user, db)

    if not farm.location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "This farm has no location set, so live weather can't be looked up.",
                    "error": "FARM_LOCATION_MISSING"},
        )

    try:
        weather = weather_service.get_live_weather_for_location(farm.location)
    except weather_service.WeatherServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": str(exc), "error": "WEATHER_SERVICE_ERROR"},
        ) from exc

    db.add(WeatherRecord(farm_id=farm.id, temperature=weather["temperature"],
                          humidity=weather["humidity"], rainfall=weather["rainfall"]))
    farm.temperature = weather["temperature"]
    farm.humidity = weather["humidity"]
    db.commit()

    response = LiveWeatherResponse(
        farm_id=farm.id, resolved_location=weather["resolved_location"],
        temperature=weather["temperature"], humidity=weather["humidity"], rainfall=weather["rainfall"],
        observed_at=weather.get("observed_at"), farm_updated=True,
    )
    return success_response("Live weather fetched and farm readings updated", data=response.model_dump(mode="json"))
