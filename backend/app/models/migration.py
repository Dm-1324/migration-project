from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPKMixin

LIFECYCLE_STATES = ("RECEIVED", "DISCOVERED", "ASSESSED", "PREPARED", "PREFLIGHT_PASS", "READY", "PRESTAGED", "APPROVAL_PENDING", "CUTOVER_RUNNING", "VALIDATING", "HYPERCARE", "CLOSED")


class Tenant(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "tenants"
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)


class MigrationProject(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "migration_projects"
    migration_code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    source_tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False)
    target_tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id"), nullable=False)
    status: Mapped[str] = mapped_column(Enum(*LIFECYCLE_STATES, name="lifecycle_state"), default="RECEIVED", nullable=False)
    source_tenant: Mapped["Tenant"] = relationship("Tenant", foreign_keys=[source_tenant_id])
    target_tenant: Mapped["Tenant"] = relationship("Tenant", foreign_keys=[target_tenant_id])
    waves: Mapped[list["MigrationWave"]] = relationship("MigrationWave", back_populates="migration_project", cascade="all, delete-orphan")


class MigrationWave(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "migration_waves"
    migration_project_id: Mapped[str] = mapped_column(String(36), ForeignKey("migration_projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(Enum(*LIFECYCLE_STATES, name="wave_lifecycle_state"), default="RECEIVED", nullable=False)
    migration_project: Mapped["MigrationProject"] = relationship("MigrationProject", back_populates="waves")
    batches: Mapped[list["Batch"]] = relationship("Batch", back_populates="wave", cascade="all, delete-orphan")
