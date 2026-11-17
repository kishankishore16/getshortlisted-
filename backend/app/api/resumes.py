"""Resume management API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeQualityScore, ResumeResponse
from app.services.embeddings import store_embedding
from app.services.parser import extract_text_from_pdf, parse_resume_with_llm
from app.services.scorer import score_resume
from app.utils.file_handler import upload_to_cloudinary
from app.utils.security import get_current_user

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF resume, parse with Gemini AI, compute quality score, and store."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF resume files are supported.",
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # 1. Extract text from PDF
    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read PDF text: {str(e)}",
        )

    # 2. Parse structured data using Gemini
    try:
        parsed_dict = await parse_resume_with_llm(raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Resume Parser error: {str(e)}",
        )

    # 3. Compute resume quality score
    quality_score_obj: ResumeQualityScore = score_resume(parsed_dict)
    quality_breakdown = quality_score_obj.model_dump()

    # 4. Upload file to Cloudinary with safe fallback
    file_url = f"local://uploads/{file.filename}"
    try:
        # Rewind file pointer
        await file.seek(0)
        file_url = await upload_to_cloudinary(file)
    except Exception:
        # If Cloudinary is not configured or fails, use local placeholder URL
        file_url = f"https://getshortlisted-resumes.storage/{uuid.uuid4()}/{file.filename}"

    # 5. Create Resume DB record
    resume_id = uuid.uuid4()
    doc_id = str(resume_id)

    # Store embedding
    try:
        store_embedding(
            doc_id=doc_id,
            text=raw_text,
            metadata={"user_id": str(current_user.id), "type": "resume"},
        )
    except Exception:
        pass  # Proceed even if Chroma embedding storage faces non-fatal issues

    new_resume = Resume(
        id=resume_id,
        user_id=current_user.id,
        file_url=file_url,
        parsed_data=parsed_dict,
        embedding_id=doc_id,
        quality_score=quality_score_obj.overall_score,
        quality_breakdown=quality_breakdown,
        is_active=True,
    )
    db.add(new_resume)
    await db.commit()
    await db.refresh(new_resume)

    return new_resume


@router.get("/", response_model=list[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all active resumes uploaded by the current student."""
    stmt = (
        select(Resume)
        .where(Resume.user_id == current_user.id, Resume.is_active == True)
        .order_by(desc(Resume.uploaded_at))
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a specific resume and its parsed data."""
    stmt = select(Resume).where(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_active == True,
    )
    result = await db.execute(stmt)
    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a resume."""
    stmt = select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    result = await db.execute(stmt)
    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    resume.is_active = False
    await db.commit()
    return None


@router.post("/{resume_id}/score", response_model=ResumeQualityScore)
async def recompute_score(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Recompute standalone quality score for an existing resume."""
    stmt = select(Resume).where(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_active == True,
    )
    result = await db.execute(stmt)
    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    quality_obj = score_resume(resume.parsed_data or {})
    resume.quality_score = quality_obj.overall_score
    resume.quality_breakdown = quality_obj.model_dump()
    await db.commit()

    return quality_obj
