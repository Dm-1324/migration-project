from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.batch import Batch
from app.models.migration import MigrationWave
from app.schemas.tools import CopilotBatchContext, CopilotMigrationContext
from app.services import batch_service, evidence_service, migration_service, readiness_service
from app.services.migration_service import NotFoundError

router = APIRouter(prefix="/copilot", tags=["copilot-context"])


@router.get("/batches/{batch_id}/context", response_model=CopilotBatchContext)
def get_batch_context(batch_id: str, db: Session = Depends(get_db)):
    try:
        batch = batch_service.get_batch(db, batch_id)
        wave = migration_service.get_wave(db, batch.wave_id)
        migration = migration_service.get_migration(db, wave.migration_project_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    verdict, domain_statuses, run_id = readiness_service.get_current_readiness(db, batch_id)
    open_blockers = evidence_service.list_exceptions(db, batch_id=batch_id, severity="BLOCKING", status="OPEN")
    recent_evidence = evidence_service.list_evidence_for_batch(db, batch_id)[:10]
    return CopilotBatchContext(
        batch_id=batch.id,
        batch_code=batch.batch_code,
        migration_id=migration.id,
        migration_code=migration.migration_code,
        lifecycle_state=batch.lifecycle_state,
        readiness_status=verdict.overall_status,
        domain_status=domain_statuses,
        blocker_count=len(open_blockers),
        warning_count=len(verdict.warning_domains),
        latest_run_id=run_id,
        evidence_refs=[e.id for e in recent_evidence],
    )


@router.get("/migrations/{migration_id}/context", response_model=CopilotMigrationContext)
def get_migration_context(migration_id: str, db: Session = Depends(get_db)):
    try:
        migration = migration_service.get_migration(db, migration_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    wave_count, batch_count = migration_service.get_migration_counts(db, migration_id)
    blocked_batch_count = (
        db.query(Batch)
        .join(MigrationWave, Batch.wave_id == MigrationWave.id)
        .filter(MigrationWave.migration_project_id == migration_id, Batch.readiness_status == "BLOCKED")
        .count()
    )
    return CopilotMigrationContext(
        migration_id=migration.id,
        migration_code=migration.migration_code,
        name=migration.name,
        status=migration.status,
        wave_count=wave_count,
        batch_count=batch_count,
        blocked_batch_count=blocked_batch_count,
    )
