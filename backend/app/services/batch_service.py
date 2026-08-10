from __future__ import annotations
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.batch import Batch, Resource
from app.schemas.batch import BatchCreate, ResourceCreate
from app.services.migration_service import NotFoundError, get_wave

def _next_batch_code(db: Session, wave_id: str) -> str:
    count = db.scalar(select(func.count()).select_from(Batch).where(Batch.wave_id == wave_id)) or 0
    return f"BATCH-{count + 1:03d}"

def create_batch(db: Session, wave_id: str, payload: BatchCreate) -> Batch:
    get_wave(db, wave_id)
    code = payload.batch_code or _next_batch_code(db, wave_id)
    batch = Batch(wave_id=wave_id, batch_code=code, name=payload.name)
    db.add(batch); db.commit(); db.refresh(batch)
    return batch

def list_batches(db: Session, wave_id: str) -> list[Batch]:
    get_wave(db, wave_id)
    return list(db.scalars(select(Batch).where(Batch.wave_id == wave_id).order_by(Batch.created_at)))

def get_batch(db: Session, batch_id: str) -> Batch:
    batch = db.get(Batch, batch_id)
    if not batch: raise NotFoundError(f"Batch {batch_id} not found")
    return batch

def get_resource_count(db: Session, batch_id: str) -> int:
    return db.scalar(select(func.count()).select_from(Resource).where(Resource.batch_id == batch_id)) or 0

def add_resource(db: Session, batch_id: str, payload: ResourceCreate) -> Resource:
    get_batch(db, batch_id)
    resource = Resource(batch_id=batch_id, resource_type=payload.resource_type, display_name=payload.display_name, source_identifier=payload.source_identifier, target_identifier=payload.target_identifier)
    db.add(resource); db.commit(); db.refresh(resource)
    return resource

def list_resources(db: Session, batch_id: str) -> list[Resource]:
    get_batch(db, batch_id)
    return list(db.scalars(select(Resource).where(Resource.batch_id == batch_id).order_by(Resource.created_at)))
