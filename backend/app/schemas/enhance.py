"""Pydantic schemas for resume enhancement data structures."""

import uuid

from pydantic import BaseModel, Field


class EnhanceRequest(BaseModel):
    """Request body for resume enhancement based on a prior analysis."""

    analysis_id: uuid.UUID | None = Field(
        None, description="ID of the analysis to base enhancements on (optional if in path)"
    )
    sections: list[str] = Field(
        default=["summary", "experience", "skills", "projects"],
        description="Which resume sections to enhance",
    )


class EnhancedSection(BaseModel):
    """A single enhanced resume section with before/after comparison."""

    section: str = Field(..., description="Section name, e.g. 'summary'")
    original: str = Field(..., description="Original section content")
    enhanced: str = Field(..., description="Enhanced section content")
    changes_made: list[str] = Field(
        default_factory=list, description="List of changes applied"
    )


class EnhanceResponse(BaseModel):
    """Full enhancement result containing all enhanced sections."""

    sections: list[EnhancedSection] = Field(default_factory=list)
    ats_tips: list[str] = Field(
        default_factory=list,
        description="ATS optimization tips",
    )
    keywords_added: list[str] = Field(
        default_factory=list,
        description="New keywords injected into the resume",
    )
