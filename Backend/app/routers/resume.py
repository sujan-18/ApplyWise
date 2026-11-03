
from typing import Annotated
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pypdf import PdfReader
from docx import Document

from app.dependencies import get_current_user
from app.models import User


router = APIRouter(prefix="/resume", tags=["Resume AI"])

MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


async def extract_resume_text(file: UploadFile) -> str:
    """
    Validate the uploaded resume and extract its text.
    Supports PDF and DOCX files.
    """

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed."
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Resume must be smaller than 5 MB."
        )

    try:
        if file.content_type == "application/pdf":
            pdf_reader = PdfReader(BytesIO(file_content))

            extracted_text = "\n".join(
                page.extract_text() or ""
                for page in pdf_reader.pages
            )

        else:
            document = Document(BytesIO(file_content))

            extracted_text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this resume. Please upload a valid PDF or DOCX file."
        )

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text was found. The resume may be a scanned image."
        )

    return extracted_text


@router.post("/upload")
async def upload_resume(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    extracted_text = await extract_resume_text(file)

    return {
        "message": "Resume uploaded and text extracted successfully.",
        "filename": file.filename,
        "user_id": current_user.id,
        "extracted_text": extracted_text,
    }
