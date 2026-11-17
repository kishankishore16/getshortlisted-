"""Job-fit analysis API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.analysis import Analysis
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import (
    AnalysisListResponse,
    AnalysisResponse,
    AnalyzeRequest,
)
from app.services.embeddings import store_embedding
from app.services.explainer import (
    generate_fit_explanation,
    generate_keyword_analysis,
    generate_missing_skills,
)
from app.services.jd_parser import parse_jd_with_llm
from app.services.matcher import compute_fit_score, compute_skill_match, extract_flat_skills
from app.utils.security import get_current_user

router = APIRouter(prefix="/analyze", tags=["Analyze"])


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_job_match(
    payload: AnalyzeRequest,
    resume_id: uuid.UUID | None = Query(None, description="Optional ID of the student resume"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze a pasted job description against the student's resume.

    Runs LLM JD parsing, semantic embedding matching, skill gap detection,
    and returns fit scores, reasons, and missing skills.
    """
    target_resume_id = resume_id or payload.resume_id
    if target_resume_id:
        stmt = select(Resume).where(
            Resume.id == target_resume_id,
            Resume.user_id == current_user.id,
            Resume.is_active == True,
        )
    else:
        # Default to latest active resume
        stmt = (
            select(Resume)
            .where(Resume.user_id == current_user.id, Resume.is_active == True)
            .order_by(desc(Resume.uploaded_at))
        )

    result = await db.execute(stmt)
    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active resume not found. Please upload a resume first.",
        )

    resume_parsed = resume.parsed_data or {}

    # 2. Parse JD with Gemini
    try:
        jd_parsed = await parse_jd_with_llm(payload.jd_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job description parsing failed: {str(e)}",
        )

    # 3. Store JD embedding
    jd_doc_id = str(uuid.uuid4())
    try:
        store_embedding(
            doc_id=jd_doc_id,
            text=payload.jd_text,
            metadata={"type": "jd", "title": jd_parsed.get("title", "")},
        )
    except Exception:
        pass

    # 4. Compute Match & Skill Overlap
    resume_skills = extract_flat_skills(resume_parsed.get("skills", {}))
    jd_req = jd_parsed.get("required_skills", [])
    jd_pref = jd_parsed.get("preferred_skills", [])
    skill_match_data = compute_skill_match(resume_skills, jd_req, jd_pref)

    score_breakdown_obj = compute_fit_score(
        resume_parsed=resume_parsed,
        jd_parsed=jd_parsed,
        resume_raw_text=str(resume_parsed),
        jd_raw_text=payload.jd_text,
    )
    score_breakdown_dict = score_breakdown_obj.model_dump()

    # 5. Explanations & Actionable Advice
    fit_explanation = await generate_fit_explanation(
        resume_parsed=resume_parsed,
        jd_parsed=jd_parsed,
        score_breakdown=score_breakdown_dict,
    )

    missing_skills_roadmap = await generate_missing_skills(
        resume_parsed=resume_parsed,
        jd_parsed=jd_parsed,
        skill_match=skill_match_data,
    )

    keyword_data = await generate_keyword_analysis(
        resume_text=str(resume_parsed),
        jd_text=payload.jd_text,
        jd_parsed=jd_parsed,
    )

    # 6. Save Analysis record in DB
    analysis_id = uuid.uuid4()
    analysis = Analysis(
        id=analysis_id,
        resume_id=resume.id,
        jd_raw_text=payload.jd_text,
        jd_parsed=jd_parsed,
        jd_source_hint=payload.jd_source_hint,
        fit_score=score_breakdown_obj.overall,
        score_breakdown=score_breakdown_dict,
        fit_explanation=fit_explanation,
        missing_skills=missing_skills_roadmap,
        matched_skills=skill_match_data.get("matched_required", []) + skill_match_data.get("matched_preferred", []),
        keyword_analysis=keyword_data,
        enhancement_suggestions=None,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return analysis


@router.get("/history", response_model=list[AnalysisListResponse])
async def list_analysis_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all previous analyses performed by the current user."""
    stmt = (
        select(Analysis)
        .join(Resume, Analysis.resume_id == Resume.id)
        .where(Resume.user_id == current_user.id)
        .order_by(desc(Analysis.created_at))
    )
    result = await db.execute(stmt)
    analyses = result.scalars().all()

    formatted: list[AnalysisListResponse] = []
    for a in analyses:
        jd_title = (a.jd_parsed or {}).get("title") if a.jd_parsed else "Job Analysis"
        jd_company = (a.jd_parsed or {}).get("company") if a.jd_parsed else "Company"
        formatted.append(
            AnalysisListResponse(
                id=a.id,
                jd_source_hint=a.jd_source_hint,
                fit_score=a.fit_score,
                jd_title=jd_title,
                jd_company=jd_company,
                created_at=a.created_at,
            )
        )
    return formatted


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_detail(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve complete breakdown and results for a specific analysis."""
    stmt = (
        select(Analysis)
        .join(Resume, Analysis.resume_id == Resume.id)
        .where(Analysis.id == analysis_id, Resume.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )
    return analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an analysis record."""
    stmt = (
        select(Analysis)
        .join(Resume, Analysis.resume_id == Resume.id)
        .where(Analysis.id == analysis_id, Resume.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    await db.delete(analysis)
    await db.commit()
    return None
