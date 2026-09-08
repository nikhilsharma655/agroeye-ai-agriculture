from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.schemas.crop import CropCreate, CropUpdate, CropOut
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response

router = APIRouter(prefix="/api/crops", tags=["Crops"])


def _get_owned_farm_or_404(farm_id: str, current_user: User, db: Session) -> Farm:
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == current_user.id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"success": False, "message": "Farm not found", "error": "FARM_NOT_FOUND"})
    return farm


@router.get("/farm/{farm_id}", summary="List crops for a farm")
def list_crops(farm_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _get_owned_farm_or_404(farm_id, current_user, db)
    crops = db.query(Crop).filter(Crop.farm_id == farm_id).order_by(Crop.created_at.desc()).all()
    return success_response("Crops retrieved", data=[CropOut.model_validate(c).model_dump(mode="json") for c in crops])


@router.post("/farm/{farm_id}", status_code=status.HTTP_201_CREATED, summary="Add a crop to a farm")
def add_crop(farm_id: str, payload: CropCreate, current_user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    _get_owned_farm_or_404(farm_id, current_user, db)
    crop = Crop(farm_id=farm_id, **payload.model_dump())
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return success_response("Crop added successfully", data=CropOut.model_validate(crop).model_dump(mode="json"),
                             status_code=status.HTTP_201_CREATED)


@router.put("/{crop_id}", summary="Update a crop")
def update_crop(crop_id: str, payload: CropUpdate, current_user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    crop = db.query(Crop).join(Farm).filter(Crop.id == crop_id, Farm.user_id == current_user.id).first()
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"success": False, "message": "Crop not found", "error": "CROP_NOT_FOUND"})
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(crop, field, value)
    db.commit()
    db.refresh(crop)
    return success_response("Crop updated successfully", data=CropOut.model_validate(crop).model_dump(mode="json"))


@router.delete("/{crop_id}", summary="Delete a crop")
def delete_crop(crop_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    crop = db.query(Crop).join(Farm).filter(Crop.id == crop_id, Farm.user_id == current_user.id).first()
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"success": False, "message": "Crop not found", "error": "CROP_NOT_FOUND"})
    db.delete(crop)
    db.commit()
    return success_response("Crop deleted successfully")
