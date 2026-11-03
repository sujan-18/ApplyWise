from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.security import hash_password, verify_password

from app.schemas.auth import LoginRequest, TokenResponse
from app.token import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Return the authenticated user's safe profile fields."""
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    profile_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    updates = profile_data.model_dump(exclude_unset=True)
    if any(value is None for value in updates.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Profile fields cannot be null",
        )

    email = updates.get("email")
    if email and email != current_user.email:
        existing_user = db.scalar(
            select(User).where(User.email == email, User.id != current_user.id)
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

    for field, value in updates.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)]
):
    statement = select(User).where(
        User.email == user_data.email
    )

    existing_user = db.scalar(statement)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=TokenResponse)
def login_user(
    login_data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    statement = select(User).where(User.email == login_data.email)
    user = db.scalar(statement)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    password_is_valid = verify_password(
        login_data.password,
        user.hashed_password,
    )

    if not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user_id=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
