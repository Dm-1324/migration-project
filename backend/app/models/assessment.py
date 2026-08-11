from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

REQUIRED_DOMAINS = ["Entra", "ExchangeOnline", "OneDrive"]


class Assessment(Base):
    __tablename__ = "assessments"

    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: f"run-{uuid.uuid4().hex[:12]}")
    batch_id: Mapped[str] = mapped_column(ForeignKey("batches.id"), index=True)
    requested_domains: Mapped[str] = mapped_column(Text, default=lambda: json.dumps(REQUIRED_DOMAINS))
    force_refresh: Mapped[bool] = mapped_column(Boolean, default=False)
    run_status: Mapped[str] = mapped_column(String(16), default="RUNNING")
    overall_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    can_proceed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    blocker_count: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[str | None] = mapped_column(String(64), nullable=True)

    batch = relationship("Batch")
    results = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.id"), index=True)
    batch_id: Mapped[str] = mapped_column(ForeignKey("batches.id"), index=True)
    domain: Mapped[str] = mapped_column(String(32))
    assessment_version: Mapped[str] = mapped_column(String(16), default="v1")
    status: Mapped[str] = mapped_column(String(16))
    evaluated_resources: Mapped[int] = mapped_column(Integer, default=0)
    ready: Mapped[int] = mapped_column(Integer, default=0)
    warning: Mapped[int] = mapped_column(Integer, default=0)
    blocked: Mapped[int] = mapped_column(Integer, default=0)
    can_proceed: Mapped[bool] = mapped_column(Boolean, default=False)
    blockers: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_actions: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)

    assessment = relationship("Assessment", back_populates="results")

    @property
    def blockers_list(self) -> list:
        return json.loads(self.blockers) if self.blockers else []

    @property
    def recommended_actions_list(self) -> list:
        return json.loads(self.recommended_actions) if self.recommended_actions else []
