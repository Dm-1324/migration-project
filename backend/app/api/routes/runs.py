from __future__ import annotations
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.assessment import RunStatusOut, RunStepOut
from app.services import assessment_service
from app.services.migration_service import NotFoundError

router = APIRouter(tags=["runs"])

def _build_run_status(assessment) -> RunStatusOut:
    requested = json.loads(assessment.requested_domains)
    completed_domains = {r.domain for r in assessment.results}
    steps = [RunStepOut(name=domain, status="COMPLETED" if domain in completed_domains else "PENDING") for domain in requested]
    if assessment.run_status == "RUNNING":
        for step in steps:
            if step.status == "PENDING":
                step.status = "RUNNING"
                break
    return RunStatusOut(run_id=assessment.run_id, status=assessment.run_status, steps=steps)

@router.get("/runs/{run_id}", response_model=RunStatusOut)
def get_run(run_id: str, db: Session = Depends(get_db)):
    try:
        assessment = assessment_service.get_assessment_by_run_id(db, run_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return _build_run_status(assessment)

@router.get("/runs/{run_id}/status", response_model=RunStatusOut)
def get_run_status(run_id: str, db: Session = Depends(get_db)):
    try:
        assessment = assessment_service.get_assessment_by_run_id(db, run_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return _build_run_status(assessment)
