"""Pydantic schemas for resume data structures."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Education(BaseModel):
    """Schema for a single education entry."""

    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""
    description: str = ""


class Experience(BaseModel):
    """Schema for a single work experience entry."""

    company: str = ""
    title: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    bullets: list[str] = Field(default_factory=list)


class Project(BaseModel):
    """Schema for a single project entry."""

    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    url: str = ""
    bullets: list[str] = Field(default_factory=list)


class Certification(BaseModel):
    """Schema for a single certification entry."""

    name: str = ""
    issuer: str = ""
    date: str = ""
    url: str = ""


class ParsedResume(BaseModel):
    """Full parsed resume data structure extracted by the LLM parser."""

    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    summary: str = ""
    education: list[Education] = Field(default_factory=list)
    skills: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Skills grouped by category, e.g. {'Programming Languages': ['Python', 'Java']}",
    )
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)


class ResumeQualityScore(BaseModel):
    """Resume quality scoring breakdown with actionable tips."""

    overall_score: float = Field(..., ge=0, le=100)
    completeness: float = Field(..., ge=0, le=100)
    impact_language: float = Field(..., ge=0, le=100)
    keyword_richness: float = Field(..., ge=0, le=100)
    structure: float = Field(..., ge=0, le=100)
    specificity: float = Field(..., ge=0, le=100)
    tips: list[str] = Field(default_factory=list)


class ResumeResponse(BaseModel):
    """Schema for resume data in API responses."""

    id: uuid.UUID
    file_url: str
    parsed_data: dict | None = None
    quality_score: float | None = None
    quality_breakdown: dict | None = None
    is_active: bool = True
    uploaded_at: datetime

    model_config = {"from_attributes": True}
