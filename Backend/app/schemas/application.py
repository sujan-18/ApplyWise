from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=150)
    job_title: str = Field(min_length=2, max_length=150)
    status: ApplicationStatus = ApplicationStatus.APPLIED
    applied_date: date = Field(default_factory=date.today)
    notes: str | None = Field(default=None, max_length=2000)


class ApplicationUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=2, max_length=150)
    job_title: str | None = Field(default=None, min_length=2, max_length=150)
    status: ApplicationStatus | None = None
    applied_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    job_title: str
    status: ApplicationStatus
    applied_date: date
    notes: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime