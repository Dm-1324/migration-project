from __future__ import annotations
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.assessment import AssessmentDetail, AssessmentOut, AssessmentStartRequest, AssessmentStartResponse, DomainResultOut, DomainResultSubmit
from app.services import assessment_service
from app.services.assessment_service import InvalidAssessmentInputError
from app.services.migration_service import NotFoundError

router = APIRouter(tags=["assessments"])

def _domain_result_to_out(result) -> DomainResultOut:
    return DomainResultOut(id=result.id, assessment_id=result.assessment_id, batch_id=result.batch_id, domain=result.domain, assessment_version=result.assessment_version, status=result.status, evaluated_resources=result.evaluated_resources, ready=result.ready, warning=result.warning, blocked=result.blocked, can_proceed=result.can_proceed, blockers=json.loads(result.blockers) if result.blockers else [], recommended_actions=json.loads(result.recommended_actions) if result.recommended_actions else [], error_code=result.error_code, created_at=result.created_at)

@router.post("/batches/{batch_id}/assessments", response_model=AssessmentStartResponse, status_code=201)
def start_assessment(batch_id: str, payload: AssessmentStartRequest, db: Session = Depends(get_db)):
    try:
        assessment = assessment_service.start_assessment(db, batch_id, payload)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except InvalidAssessmentInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return AssessmentStartResponse(run_id=assessment.run_id, status=assessment.run_status, batch_id=batch_id)

@router.get("/batches/{batch_id}/assessments", response_model=list[AssessmentOut])
def list_assessments(batch_id: str, db: Session = Depends(get_db)):
    try:
        return assessment_service.list_assessments_for_batch(db, batch_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("/assessments/{assessment_id}", response_model=AssessmentDetail)
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    try:
        assessment = assessment_service.get_assessment(db, assessment_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return AssessmentDetail(**AssessmentOut.model_validate(assessment).model_dump(), results=[_domain_result_to_out(r) for r in assessment.results])

@router.post("/assessments/{assessment_id}/domains/result", response_model=DomainResultOut, status_code=201)
def submit_domain_result(assessment_id: str, payload: DomainResultSubmit, db: Session = Depends(get_db)):
    try:
        result = assessment_service.submit_domain_result(db, assessment_id, payload)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except InvalidAssessmentInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _domain_result_to_out(result)

@router.get("/batches/{batch_id}/assessments/{domain}", response_model=DomainResultOut)
def get_latest_domain_assessment(batch_id: str, domain: str, db: Session = Depends(get_db)):
    try:
        result = assessment_service.get_latest_domain_result(db, batch_id, domain)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    if result is None:
        raise HTTPException(status_code=404, detail=f"No assessment result yet for domain '{domain}'.")
    return _domain_result_to_out(result)
