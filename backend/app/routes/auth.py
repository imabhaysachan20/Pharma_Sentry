from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from backend.app.models.user import DBUser
from backend.app.schemas.auth import UserSignup, UserLogin, TokenResponse, RefreshRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(DBUser).filter(DBUser.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    # Create new user
    hashed_pwd = hash_password(user_data.password)
    new_user = DBUser(name=user_data.name, email=user_data.email, password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate tokens
    access = create_access_token({"sub": new_user.email, "id": new_user.id})
    refresh = create_refresh_token({"sub": new_user.email, "id": new_user.id})

    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    access = create_access_token({"sub": user.email, "id": user.id})
    refresh = create_refresh_token({"sub": user.email, "id": user.id})

    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest):
    payload = verify_token(data.refresh_token, expected_type="refresh")
    access = create_access_token({"sub": payload["email"], "id": payload["id"]})
    refresh = create_refresh_token({"sub": payload["email"], "id": payload["id"]})
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}
