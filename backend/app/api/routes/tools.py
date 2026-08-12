from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.routes.assessments import _domain_result_to_out
from app.database import get_db
from app.schemas.assessment import AssessmentDetail, AssessmentOut, DomainResultOut
from app.schemas.tools import BlockerOut, StartBatchAssessmentRequest, ToolAssessRequest
from app.services import assessment_service, batch_service, evidence_service, orchestration_service
from app.services.assessment_service import InvalidAssessmentInputError
from app.services.migration_service import NotFoundError
from app.tools.entra import assess as entra_tool
from app.tools.exchange import assess as exchange_tool
from app.tools.onedrive import assess as onedrive_tool

router = APIRouter(prefix="/tools", tags=["tools"])


def _run_single_domain_tool(db: Session, tool_fn, payload: ToolAssessRequest):
    try:
        assessment = assessment_service.get_assessment(db, payload.assessment_id)
        batch = batch_service.get_batch(db, assessment.batch_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    resources = batch_service.list_resources(db, batch.id)
    result_payload = tool_fn(db, batch, resources, simulate_error=payload.simulate_error)
    try:
        result = assessment_service.submit_domain_result(db, assessment.id, result_payload)
    except InvalidAssessmentInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _domain_result_to_out(result)


@router.post("/assess_entra", response_model=DomainResultOut)
def assess_entra(payload: ToolAssessRequest, db: Session = Depends(get_db)):
    return _run_single_domain_tool(db, entra_tool.run, payload)


@router.post("/assess_exchange", response_model=DomainResultOut)
def assess_exchange(payload: ToolAssessRequest, db: Session = Depends(get_db)):
    return _run_single_domain_tool(db, exchange_tool.run, payload)


@router.post("/assess_onedrive", response_model=DomainResultOut)
def assess_onedrive(payload: ToolAssessRequest, db: Session = Depends(get_db)):
    return _run_single_domain_tool(db, onedrive_tool.run, payload)


@router.post("/start_batch_assessment/{batch_id}", response_model=AssessmentDetail)
def start_batch_assessment(batch_id: str, payload: StartBatchAssessmentRequest, db: Session = Depends(get_db)):
    try:
        assessment = orchestration_service.run_batch_assessment(
            db,
            batch_id,
            domains=payload.domains,
            force_refresh=payload.force_refresh,
            simulate_errors=payload.simulate_errors,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except InvalidAssessmentInputError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return AssessmentDetail(
        **AssessmentOut.model_validate(assessment).model_dump(),
        results=[_domain_result_to_out(r) for r in assessment.results],
    )


@router.get("/get_blockers/{batch_id}", response_model=list[BlockerOut])
def get_blockers(batch_id: str, db: Session = Depends(get_db)):
    exceptions = evidence_service.list_exceptions(db, batch_id=batch_id, severity="BLOCKING")
    return [
        BlockerOut(
            id=e.id,
            domain=e.domain,
            code=e.code,
            description=e.description,
            severity=e.severity,
            status=e.status,
            affected_resource=e.affected_resource,
            evidence_id=e.evidence_id,
        )
        for e in exceptions
    ]
