from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.assessment import ReadinessOut
from app.services import readiness_service
from app.services.migration_service import NotFoundError

router = APIRouter(tags=["readiness"])

def _out(batch_id, verdict, domain_statuses, run_id):
    return ReadinessOut(batch_id=batch_id, status=verdict.overall_status, can_proceed=verdict.can_proceed, reason=verdict.reason, domains=domain_statuses, blockers=len(verdict.blocked_domains), warnings=len(verdict.warning_domains), assessment_run_id=run_id)

@router.get("/readiness/{batch_id}", response_model=ReadinessOut)
def get_readiness(batch_id: str, db: Session = Depends(get_db)):
    try:
        verdict, domain_statuses, run_id = readiness_service.get_current_readiness(db, batch_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return _out(batch_id, verdict, domain_statuses, run_id)

@router.post("/readiness/{batch_id}/calculate", response_model=ReadinessOut)
def recalculate_readiness(batch_id: str, db: Session = Depends(get_db)):
    try:
        verdict, domain_statuses, run_id = readiness_service.get_current_readiness(db, batch_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return _out(batch_id, verdict, domain_statuses, run_id)
