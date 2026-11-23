"""SQLAlchemy ORM model for job-fit analysis results."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Analysis(Base):
    """Analysis model.

    Stores the results of a resume vs. job description matching analysis,
    including scores, breakdowns, skill gaps, and enhancement suggestions.
    """

    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=str(uuid.uuid4()),
        default=uuid.uuid4,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jd_raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    jd_parsed: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    jd_source_hint: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fit_score: Mapped[float] = mapped_column(Float, nullable=False)
    score_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    fit_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    missing_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    matched_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    keyword_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    enhancement_suggestions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    resume: Mapped["Resume"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Resume", back_populates="analyses"
    )

    def __repr__(self) -> str:
        return f"<Analysis {self.id} resume={self.resume_id} score={self.fit_score}>"
