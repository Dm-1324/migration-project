from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.assessment import AuditEventOut
from app.services import audit_service

router = APIRouter(tags=["audit"])

@router.get("/audit", response_model=list[AuditEventOut])
def list_audit_events(batch_id: str | None = None, run_id: str | None = None, entity_type: str | None = None, limit: int = 100, db: Session = Depends(get_db)):
    return audit_service.list_events(db, batch_id=batch_id, run_id=run_id, entity_type=entity_type, limit=limit)
