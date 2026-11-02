from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    INTERVIEW_TAKEN = "Interview Taken"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    company_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    job_title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    status: Mapped[ApplicationStatus] = mapped_column(
        SQLAlchemyEnum(
            ApplicationStatus,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ]
        ),
        default=ApplicationStatus.APPLIED,
        nullable=False
    )

    applied_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="applications"
    )