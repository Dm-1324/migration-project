from __future__ import annotations
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.batch import Batch
from app.models.migration import MigrationProject, MigrationWave, Tenant
from app.schemas.migration import MigrationProjectCreate, MigrationWaveCreate

class NotFoundError(Exception):
    pass

def _next_migration_code(db: Session, name: str) -> str:
    prefix = "".join(ch for ch in name.upper() if ch.isalpha())[:4] or "PROJ"
    count = db.scalar(select(func.count()).select_from(MigrationProject)) or 0
    return f"{prefix}{count + 1:03d}"

def create_migration(db: Session, payload: MigrationProjectCreate) -> MigrationProject:
    for tenant_id in (payload.source_tenant_id, payload.target_tenant_id):
        if not db.get(Tenant, tenant_id):
            raise NotFoundError(f"Tenant {tenant_id} not found")
    code = payload.migration_code or _next_migration_code(db, payload.name)
    project = MigrationProject(migration_code=code, name=payload.name, description=payload.description, source_tenant_id=payload.source_tenant_id, target_tenant_id=payload.target_tenant_id)
    db.add(project); db.commit(); db.refresh(project)
    return project

def list_migrations(db: Session, status: str | None = None) -> list[MigrationProject]:
    stmt = select(MigrationProject)
    if status: stmt = stmt.where(MigrationProject.status == status)
    return list(db.scalars(stmt.order_by(MigrationProject.created_at.desc())))

def get_migration(db: Session, migration_id: str) -> MigrationProject:
    project = db.get(MigrationProject, migration_id)
    if not project: raise NotFoundError(f"Migration {migration_id} not found")
    return project

def get_migration_counts(db: Session, migration_id: str) -> tuple[int, int]:
    wave_count = db.scalar(select(func.count()).select_from(MigrationWave).where(MigrationWave.migration_project_id == migration_id)) or 0
    batch_count = db.scalar(select(func.count()).select_from(Batch).join(MigrationWave, Batch.wave_id == MigrationWave.id).where(MigrationWave.migration_project_id == migration_id)) or 0
    return wave_count, batch_count

def create_wave(db: Session, migration_id: str, payload: MigrationWaveCreate) -> MigrationWave:
    get_migration(db, migration_id)
    wave = MigrationWave(migration_project_id=migration_id, name=payload.name, sequence=payload.sequence)
    db.add(wave); db.commit(); db.refresh(wave)
    return wave

def list_waves(db: Session, migration_id: str) -> list[MigrationWave]:
    get_migration(db, migration_id)
    stmt = select(MigrationWave).where(MigrationWave.migration_project_id == migration_id).order_by(MigrationWave.sequence)
    return list(db.scalars(stmt))

def get_wave(db: Session, wave_id: str) -> MigrationWave:
    wave = db.get(MigrationWave, wave_id)
    if not wave: raise NotFoundError(f"Wave {wave_id} not found")
    return wave
