from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.batch import Batch
from app.models.migration import MigrationProject, MigrationWave
from app.schemas.tools import CodeResolverOut

router = APIRouter(prefix="/resolve", tags=["resolve"])


@router.get("/migrations/{migration_code}", response_model=CodeResolverOut)
def resolve_migration(migration_code: str, db: Session = Depends(get_db)):
    migration = db.scalar(select(MigrationProject).where(MigrationProject.migration_code == migration_code))
    if not migration:
        raise HTTPException(status_code=404, detail=f"Migration {migration_code} not found")
    return CodeResolverOut(id=migration.id, code=migration.migration_code, type="migration")


@router.get("/batches/{batch_code}", response_model=CodeResolverOut)
def resolve_batch(batch_code: str, migration_code: str | None = Query(default=None), db: Session = Depends(get_db)):
    stmt = (
        select(Batch)
        .join(MigrationWave, Batch.wave_id == MigrationWave.id)
        .join(MigrationProject, MigrationWave.migration_project_id == MigrationProject.id)
        .where(Batch.batch_code == batch_code)
    )
    if migration_code:
        stmt = stmt.where(MigrationProject.migration_code == migration_code)
    matches = list(db.scalars(stmt))
    if not matches:
        raise HTTPException(status_code=404, detail=f"Batch {batch_code} not found")
    if len(matches) > 1:
        raise HTTPException(status_code=409, detail=f"Batch code {batch_code} is ambiguous; provide migration_code.")
    batch = matches[0]
    return CodeResolverOut(id=batch.id, code=batch.batch_code, type="batch")
