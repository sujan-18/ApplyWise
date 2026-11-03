
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    HTTPException,
    Query,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Application, User, ApplicationStatus
from app.schemas.application import (
    ApplicationResponse,
    ApplicationCreate,
    ApplicationUpdate,
)


router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


# GET: Retrieve all applications belonging to the logged-in user
@router.get("/", response_model=list[ApplicationResponse])
def get_my_applications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    status_filter: ApplicationStatus | None = Query(
        default=None,
        alias="status",
    ),
):
    statement = select(Application).where(
        Application.user_id == current_user.id
    )

    # Apply status filtering only when a status is provided
    if status_filter is not None:
        statement = statement.where(
            Application.status == status_filter
        )

    statement = (
        statement
        .order_by(Application.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    applications = db.scalars(statement).all()

    return applications


# POST: Create a new application
@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    application_data: ApplicationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    new_application = Application(
        company_name=application_data.company_name,
        job_title=application_data.job_title,
        status=application_data.status,
        applied_date=application_data.applied_date,
        notes=application_data.notes,
        user_id=current_user.id,
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application


# GET: Retrieve one application
@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    statement = select(Application).where(
        Application.id == application_id,
        Application.user_id == current_user.id,
    )

    application = db.scalar(statement)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application


# PATCH: Update an application
@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    application_data: ApplicationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    statement = select(Application).where(
        Application.id == application_id,
        Application.user_id == current_user.id,
    )

    application = db.scalar(statement)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    update_data = application_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)

    return application


# DELETE: Delete an application
@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_application(
    application_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    statement = select(Application).where(
        Application.id == application_id,
        Application.user_id == current_user.id,
    )

    application = db.scalar(statement)

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    db.delete(application)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
