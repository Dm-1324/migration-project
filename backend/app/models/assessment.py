"""Assessment models for Phase 2 readiness runs and domain results."""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

REQUIRED_DOMAINS = ("Entra", "ExchangeOnline", "OneDrive")
DOMAIN_STATUSES = ("READY", "WARNING", "BLOCKED", "UNAVAILABLE")
ASSESSMENT_RUN_STATUSES = ("STARTED", "RUNNING", "COMPLETED", "FAILED")
OVERALL_READINESS_STATUSES = ("READY", "WARNING", "BLOCKED", "NOT_READY")


class Assessment(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "assessments"

    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("batches.id"), nullable=False, index=True)
    requested_domains: Mapped[str] = mapped_column(Text, nullable=False)
    force_refresh: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    run_status: Mapped[str] = mapped_column(String(16), default="STARTED", nullable=False)
    overall_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    can_proceed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    blocker_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warning_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[str | None] = mapped_column(String(64), nullable=True)

    batch: Mapped["Batch"] = relationship("Batch")
    results: Mapped[list["AssessmentResult"]] = relationship(
        "AssessmentResult", back_populates="assessment", cascade="all, delete-orphan"
    )


class AssessmentResult(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "assessment_results"

    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessments.id"), nullable=False, index=True)
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("batches.id"), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(32), nullable=False)
    assessment_version: Mapped[str] = mapped_column(String(16), default="1.0", nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    evaluated_resources: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ready: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warning: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    can_proceed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blockers: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_actions: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="results")
    batch: Mapped["Batch"] = relationship("Batch")
