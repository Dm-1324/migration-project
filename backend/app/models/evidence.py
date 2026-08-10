from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

SEVERITY_LEVELS = ("INFO", "WARNING", "BLOCKING")
EXCEPTION_STATUSES = ("OPEN", "ACKNOWLEDGED", "RESOLVED")


class Evidence(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "evidence"
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("batches.id"), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(32), nullable=False)
    tool: Mapped[str] = mapped_column(String(128), nullable=False)
    operation_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    assessment_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    affected_resource: Mapped[str | None] = mapped_column(String(255), nullable=True)
    input_parameters: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(nullable=True)
    batch: Mapped["Batch"] = relationship("Batch")


class ExceptionRecord(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "exceptions"
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("batches.id"), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(32), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    severity: Mapped[str] = mapped_column(Enum(*SEVERITY_LEVELS, name="exception_severity"), nullable=False)
    status: Mapped[str] = mapped_column(Enum(*EXCEPTION_STATUSES, name="exception_status"), default="OPEN", nullable=False)
    evidence_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("evidence.id"), nullable=True)
    affected_resource: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    batch: Mapped["Batch"] = relationship("Batch")
    evidence: Mapped["Evidence | None"] = relationship("Evidence")
