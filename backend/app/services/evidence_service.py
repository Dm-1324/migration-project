from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.batch import Batch
from app.models.evidence import Evidence, ExceptionRecord
from app.models.migration import MigrationWave
from app.schemas.evidence import EvidenceCreate, ExceptionCreate
from app.services.batch_service import get_batch
from app.services.migration_service import NotFoundError

def record_evidence(db: Session, payload: EvidenceCreate) -> Evidence:
    get_batch(db, payload.batch_id)
    evidence = Evidence(**payload.model_dump())
    db.add(evidence); db.commit(); db.refresh(evidence)
    return evidence

def get_evidence(db: Session, evidence_id: str) -> Evidence:
    ev = db.get(Evidence, evidence_id)
    if not ev: raise NotFoundError(f"Evidence {evidence_id} not found")
    return ev

def list_evidence_for_batch(db: Session, batch_id: str) -> list[Evidence]:
    get_batch(db, batch_id)
    return list(db.scalars(select(Evidence).where(Evidence.batch_id == batch_id).order_by(Evidence.created_at.desc())))

def record_exception(db: Session, payload: ExceptionCreate) -> ExceptionRecord:
    get_batch(db, payload.batch_id)
    if payload.evidence_id and not db.get(Evidence, payload.evidence_id): raise NotFoundError(f"Evidence {payload.evidence_id} not found")
    exception = ExceptionRecord(**payload.model_dump())
    db.add(exception); db.commit(); db.refresh(exception)
    return exception

def list_exceptions(db: Session, migration_id: str | None = None, batch_id: str | None = None, domain: str | None = None, severity: str | None = None, status: str | None = None) -> list[ExceptionRecord]:
    stmt = select(ExceptionRecord)
    if batch_id: stmt = stmt.where(ExceptionRecord.batch_id == batch_id)
    if migration_id: stmt = stmt.join(Batch, ExceptionRecord.batch_id == Batch.id).join(MigrationWave, Batch.wave_id == MigrationWave.id).where(MigrationWave.migration_project_id == migration_id)
    if domain: stmt = stmt.where(ExceptionRecord.domain == domain)
    if severity: stmt = stmt.where(ExceptionRecord.severity == severity)
    if status: stmt = stmt.where(ExceptionRecord.status == status)
    return list(db.scalars(stmt.order_by(ExceptionRecord.created_at.desc())))

def get_exception(db: Session, exception_id: str) -> ExceptionRecord:
    exc = db.get(ExceptionRecord, exception_id)
    if not exc: raise NotFoundError(f"Exception {exception_id} not found")
    return exc

def update_exception_status(db: Session, exception_id: str, status: str) -> ExceptionRecord:
    exc = get_exception(db, exception_id)
    exc.status = status; db.commit(); db.refresh(exc)
    return exc
