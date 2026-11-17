"""Pydantic schemas for job-fit analysis data structures."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request body for starting a new resume-JD analysis."""

    resume_id: uuid.UUID | None = Field(
        None, description="Optional resume ID in body if not provided as query parameter"
    )
    jd_text: str = Field(
        ..., min_length=50, description="Full job description text to analyze against"
    )
    jd_source_hint: str | None = Field(
        None, description="Optional source hint, e.g. 'LinkedIn', 'Naukri'"
    )
    source_hint: str | None = Field(
        None, description="Alias for jd_source_hint"
    )


class SkillGap(BaseModel):
    """A single missing skill with learning guidance."""

    skill_name: str
    priority: str = Field(..., description="'required' or 'preferred'")
    reason: str
    estimated_learning_time: str
    resources: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of the fit score components."""

    semantic_similarity: float = Field(..., ge=0, le=100)
    skill_match: float = Field(..., ge=0, le=100)
    experience_alignment: float = Field(..., ge=0, le=100)
    education_fit: float = Field(..., ge=0, le=100)
    overall: float = Field(..., ge=0, le=100)


class AnalysisResponse(BaseModel):
    """Full analysis result returned from the analysis endpoint."""

    id: uuid.UUID
    fit_score: float
    score_breakdown: dict | None = None
    fit_explanation: str
    missing_skills: list[dict] | None = None
    matched_skills: list[dict] | None = None
    keyword_analysis: dict | None = None
    enhancement_suggestions: dict | None = None
    jd_parsed: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListResponse(BaseModel):
    """Compact analysis entry for listing past analyses."""

    id: uuid.UUID
    jd_source_hint: str | None = None
    fit_score: float
    jd_title: str | None = None
    jd_company: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
