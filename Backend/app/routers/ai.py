
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ResumeAnalysis
import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from app.dependencies import get_current_user
from app.models import User
from app.schemas.resume import ResumeAnalysisResponse

from app.services.gemini_service import (
    test_gemini_connection,
    analyze_resume,
)

from app.routers.resume import extract_resume_text
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ResumeAnalysis
from app.schemas.resume import SavedResumeAnalysisResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/test")
def test_ai(
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        result = test_gemini_connection()

        return {
            "message": "Gemini connected successfully!",
            "user_id": current_user.id,
            "ai_response": result,
        }

    except Exception:
        logger.exception("Gemini connection test failed")

        raise HTTPException(
            status_code=502,
            detail="Could not connect to the AI service."
        )


@router.post(
    "/analyze-resume",
    response_model=ResumeAnalysisResponse
)
async def analyze_uploaded_resume(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        # Extract text from uploaded PDF or DOCX
        extracted_text = await extract_resume_text(file)

        # Analyze the extracted text using Gemini
        analysis = analyze_resume(extracted_text)

        return {
            "message": "Resume analyzed successfully!",
            "user_id": current_user.id,
            "filename": file.filename or "resume",
            "analysis": analysis,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Resume analysis failed")

        raise HTTPException(
            status_code=502,
            detail="Resume analysis failed. Please try again later."
        )


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
        # Step 1: Extract text from the uploaded resume
        extracted_text = await extract_resume_text(file)

        # Step 2: Analyze the resume using Gemini
        analysis = analyze_resume(extracted_text)

        # Step 3: Create a database record
        resume_record = ResumeAnalysis(
            user_id=current_user.id,
            filename=file.filename or "resume",
            analysis=analysis,
        )

        # Step 4: Add the record to the database session
        db.add(resume_record)

        # Step 5: Save the record in PostgreSQL
        db.commit()

        # Step 6: Get the generated ID and database values
        db.refresh(resume_record)

        # Step 7: Return the saved analysis
        return {
            "message": "Resume analyzed and saved successfully!",
            "user_id": current_user.id,
            "filename": resume_record.filename,
            "analysis": resume_record.analysis,
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        logger.exception("Resume analysis failed")

        raise HTTPException(
            status_code=502,
            detail="Resume analysis failed. Please try again later.",
        )


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

    result = db.scalars(statement).all()

    return result


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
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not found.",
        )

    return resume_analysis
