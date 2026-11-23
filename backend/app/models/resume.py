"""SQLAlchemy ORM model for uploaded resumes."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Resume(Base):
    """Resume model.

    Stores uploaded resume metadata, parsed content, quality scores,
    and references to the Cloudinary file URL and ChromaDB embedding.
    """

    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=str(uuid.uuid4()),
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    embedding_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "User", back_populates="resumes"
    )
    analyses: Mapped[list["Analysis"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Analysis", back_populates="resume"
    )

    def __repr__(self) -> str:
        return f"<Resume {self.id} user={self.user_id}>"
