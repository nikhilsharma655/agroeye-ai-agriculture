from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserOut, TokenResponse
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_user
from app.utils.responses import success_response

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=None, status_code=status.HTTP_201_CREATED,
             summary="Register a new farmer account")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": "An account with this email already exists",
                    "error": "EMAIL_ALREADY_EXISTS"},
        )
    user = User(
        name=payload.name, email=payload.email, hashed_password=hash_password(payload.password),
        phone=payload.phone, location=payload.location, farm_size=payload.farm_size,
        preferred_language=payload.preferred_language,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)
    return success_response(
        "Account created successfully",
        data=TokenResponse(access_token=token, user=UserOut.model_validate(user)).model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/login", summary="Login and receive a JWT access token")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "Invalid email or password", "error": "INVALID_CREDENTIALS"},
        )
    token = create_access_token(subject=user.id)
    return success_response(
        "Login successful",
        data=TokenResponse(access_token=token, user=UserOut.model_validate(user)).model_dump(mode="json"),
    )


@router.post("/logout", summary="Logout (client discards the JWT)")
def logout(current_user: User = Depends(get_current_user)):
    # JWTs are stateless; logout is handled client-side by discarding the token.
    # A token-blacklist table can be added here later if server-side revocation is required.
    return success_response("Logged out successfully")
