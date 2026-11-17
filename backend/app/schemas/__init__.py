"""Schemas package — exports all Pydantic schemas."""

from app.schemas.analysis import (
    AnalysisListResponse,
    AnalysisResponse,
    AnalyzeRequest,
    ScoreBreakdown,
    SkillGap,
)
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from app.schemas.enhance import EnhancedSection, EnhanceRequest, EnhanceResponse
from app.schemas.resume import (
    ParsedResume,
    ResumeQualityScore,
    ResumeResponse,
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "ParsedResume",
    "ResumeResponse",
    "ResumeQualityScore",
    "AnalyzeRequest",
    "SkillGap",
    "ScoreBreakdown",
    "AnalysisResponse",
    "AnalysisListResponse",
    "EnhanceRequest",
    "EnhancedSection",
    "EnhanceResponse",
]
