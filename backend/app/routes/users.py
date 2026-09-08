from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", summary="Get the current user's profile")
def get_me(current_user: User = Depends(get_current_user)):
    return success_response("User profile retrieved", data=UserOut.model_validate(current_user).model_dump(mode="json"))


@router.put("/me", summary="Update the current user's profile")
def update_me(payload: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return success_response("Profile updated", data=UserOut.model_validate(current_user).model_dump(mode="json"))
