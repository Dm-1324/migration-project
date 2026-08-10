from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin
from app.models.migration import LIFECYCLE_STATES

READINESS_STATES = ("READY", "WARNING", "BLOCKED", "NOT_ASSESSED")


class Batch(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "batches"
    batch_code: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    wave_id: Mapped[str] = mapped_column(String(36), ForeignKey("migration_waves.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(Enum(*LIFECYCLE_STATES, name="batch_lifecycle_state"), default="RECEIVED", nullable=False)
    readiness_status: Mapped[str] = mapped_column(Enum(*READINESS_STATES, name="batch_readiness_state"), default="NOT_ASSESSED", nullable=False)
    wave: Mapped["MigrationWave"] = relationship("MigrationWave", back_populates="batches")
    resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="batch", cascade="all, delete-orphan")


class Resource(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "resources"
    batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("batches.id"), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    target_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    batch: Mapped["Batch"] = relationship("Batch", back_populates="resources")
