from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit import AuditEvent


def log_event(db: Session, event_type: str, entity_type: str, entity_id: str, migration_id: str | None = None, batch_id: str | None = None, run_id: str | None = None, operation_id: str | None = None, detail: dict | None = None) -> AuditEvent:
    event = AuditEvent(event_type=event_type, entity_type=entity_type, entity_id=entity_id, migration_id=migration_id, batch_id=batch_id, run_id=run_id, operation_id=operation_id, detail=json.dumps(detail) if detail is not None else None)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_events(db: Session, batch_id: str | None = None, run_id: str | None = None, entity_type: str | None = None, limit: int = 100) -> list[AuditEvent]:
    stmt = select(AuditEvent)
    if batch_id:
        stmt = stmt.where(AuditEvent.batch_id == batch_id)
    if run_id:
        stmt = stmt.where(AuditEvent.run_id == run_id)
    if entity_type:
        stmt = stmt.where(AuditEvent.entity_type == entity_type)
    stmt = stmt.order_by(AuditEvent.created_at.desc()).limit(limit)
    return list(db.scalars(stmt))
