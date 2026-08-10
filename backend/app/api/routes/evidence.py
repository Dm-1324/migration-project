from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.evidence import EvidenceCreate, EvidenceOut
from app.services import evidence_service
from app.services.migration_service import NotFoundError
router = APIRouter(tags=["evidence"])

@router.post("/evidence", response_model=EvidenceOut, status_code=201)
def record_evidence(payload: EvidenceCreate, db: Session = Depends(get_db)):
    try: return evidence_service.record_evidence(db, payload)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("/evidence/{evidence_id}", response_model=EvidenceOut)
def get_evidence(evidence_id: str, db: Session = Depends(get_db)):
    try: return evidence_service.get_evidence(db, evidence_id)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("/batches/{batch_id}/evidence", response_model=list[EvidenceOut])
def list_batch_evidence(batch_id: str, db: Session = Depends(get_db)):
    try: return evidence_service.list_evidence_for_batch(db, batch_id)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e
