from typing import Annotated

from fastapi import APIRouter, Depends,status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Application, User
from app.schemas.application import ApplicationResponse, ApplicationCreate


router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


@router.get("/", response_model=list[ApplicationResponse])
def get_my_applications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    statement = (
        select(Application)
        .where(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
    )

    applications = db.scalars(statement).all()

    return applications

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