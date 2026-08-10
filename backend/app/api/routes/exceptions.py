from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.evidence import ExceptionCreate, ExceptionOut, ExceptionStatusUpdate
from app.services import evidence_service
from app.services.migration_service import NotFoundError
router = APIRouter(tags=["exceptions"])

@router.post("/exceptions", response_model=ExceptionOut, status_code=201)
def record_exception(payload: ExceptionCreate, db: Session = Depends(get_db)):
    try: return evidence_service.record_exception(db, payload)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("/exceptions", response_model=list[ExceptionOut])
def list_exceptions(migration_id: str | None = None, batch_id: str | None = None, domain: str | None = None, severity: str | None = None, status: str | None = None, db: Session = Depends(get_db)):
    return evidence_service.list_exceptions(db, migration_id=migration_id, batch_id=batch_id, domain=domain, severity=severity, status=status)

@router.get("/exceptions/{exception_id}", response_model=ExceptionOut)
def get_exception(exception_id: str, db: Session = Depends(get_db)):
    try: return evidence_service.get_exception(db, exception_id)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e

@router.patch("/exceptions/{exception_id}", response_model=ExceptionOut)
def update_exception(exception_id: str, payload: ExceptionStatusUpdate, db: Session = Depends(get_db)):
    try: return evidence_service.update_exception_status(db, exception_id, payload.status)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e
