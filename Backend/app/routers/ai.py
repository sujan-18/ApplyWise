import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.database import get_db
from app.dependencies import get_current_user
from app.models import ResumeAnalysis, User
from app.routers.resume import extract_resume_text
from app.schemas.resume import (
    ResumeAnalysisResponse,
    SavedResumeAnalysisResponse,
)
from app.services.gemini_service import analyze_resume


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/analyze-resume",
    response_model=ResumeAnalysisResponse,
)
async def analyze_uploaded_resume(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        extracted_text = await extract_resume_text(file)
        analysis = await run_in_threadpool(analyze_resume, extracted_text)

        resume_record = ResumeAnalysis(
            user_id=current_user.id,
            filename=file.filename or "resume",
            analysis=analysis,
        )
        db.add(resume_record)
        db.commit()
        db.refresh(resume_record)

        return {
            "message": "Resume analyzed and saved successfully!",
            "user_id": current_user.id,
            "filename": resume_record.filename,
            "analysis": resume_record.analysis,
        }
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        logger.exception("Resume analysis failed")
        if getattr(error, "status_code", None) in {408, 429, 500, 502, 503, 504}:
            raise HTTPException(
                status_code=503,
                detail="The AI service is temporarily unavailable. Please try again shortly.",
            ) from error
        raise HTTPException(
            status_code=502,
            detail="Resume analysis failed. Please check the file and try again.",
        ) from error


@router.get(
    "/resume-analyses",
    response_model=list[SavedResumeAnalysisResponse],
)
def get_my_resume_analyses(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    statement = (
        select(ResumeAnalysis)
        .where(ResumeAnalysis.user_id == current_user.id)
        .order_by(ResumeAnalysis.created_at.desc())
    )
    return db.scalars(statement).all()


@router.get(
    "/resume-analyses/{analysis_id}",
    response_model=SavedResumeAnalysisResponse,
)
def get_resume_analysis(
    analysis_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    statement = select(ResumeAnalysis).where(
        ResumeAnalysis.id == analysis_id,
        ResumeAnalysis.user_id == current_user.id,
    )
    resume_analysis = db.scalars(statement).first()

    if resume_analysis is None:
        raise HTTPException(status_code=404, detail="Resume analysis not found.")

    return resume_analysis
