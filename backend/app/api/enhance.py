"""Resume enhancement API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.analysis import Analysis
from app.models.resume import Resume
from app.models.user import User
from app.schemas.enhance import EnhanceRequest, EnhanceResponse
from app.services.enhancer import enhance_resume
from app.utils.security import get_current_user

router = APIRouter(prefix="/enhance", tags=["Enhance"])


@router.post("/", response_model=EnhanceResponse)
@router.post("/{analysis_id}", response_model=EnhanceResponse)
async def enhance_resume_for_job(
    payload: EnhanceRequest,
    analysis_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rewrite and optimize selected resume sections for the target job description.

    Produces before/after diffs, ATS-friendly phrasing with action verbs and metrics,
    and lists injected keywords.
    """
    target_analysis_id = analysis_id or payload.analysis_id
    if not target_analysis_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="analysis_id must be provided in URL or request body.",
        )

    stmt = (
        select(Analysis, Resume)
        .join(Resume, Analysis.resume_id == Resume.id)
        .where(Analysis.id == target_analysis_id, Resume.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or unauthorized.",
        )

    analysis, resume = row

    if not resume.parsed_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume has no parsed data available for enhancement.",
        )

    if not analysis.jd_parsed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description has no parsed data available for enhancement.",
        )

    try:
        response: EnhanceResponse = await enhance_resume(
            resume_parsed=resume.parsed_data,
            jd_parsed=analysis.jd_parsed,
            sections=payload.sections,
        )

        # Store suggestions back into analysis
        analysis.enhancement_suggestions = response.model_dump()
        await db.commit()

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enhance resume: {str(e)}",
        )
