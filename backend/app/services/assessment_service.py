from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assessment import REQUIRED_DOMAINS, Assessment, AssessmentResult
from app.policies.readiness import calculate_readiness
from app.schemas.assessment import AssessmentStartRequest, DomainResultSubmit
from app.services import audit_service
from app.services.batch_service import get_batch
from app.services.migration_service import NotFoundError


class InvalidAssessmentInputError(Exception):
    pass


def _new_run_id() -> str:
    return f"run-{uuid.uuid4().hex[:8]}"


def start_assessment(db: Session, batch_id: str, payload: AssessmentStartRequest) -> Assessment:
    batch = get_batch(db, batch_id)
    domains = payload.domains or list(REQUIRED_DOMAINS)
    unknown = [d for d in domains if d not in REQUIRED_DOMAINS]
    if unknown:
        raise InvalidAssessmentInputError(f"Unknown domain(s): {', '.join(unknown)}")
    assessment = Assessment(run_id=_new_run_id(), batch_id=batch_id, requested_domains=json.dumps(domains), force_refresh=payload.force_refresh, run_status="RUNNING")
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    audit_service.log_event(db, "ASSESSMENT_STARTED", "Assessment", assessment.id, batch_id=batch_id, run_id=assessment.run_id, detail={"domains": domains, "forceRefresh": payload.force_refresh})
    return assessment


def get_assessment(db: Session, assessment_id: str) -> Assessment:
    assessment = db.get(Assessment, assessment_id)
    if not assessment:
        raise NotFoundError(f"Assessment {assessment_id} not found")
    return assessment


def get_assessment_by_run_id(db: Session, run_id: str) -> Assessment:
    assessment = db.scalar(select(Assessment).where(Assessment.run_id == run_id))
    if not assessment:
        raise NotFoundError(f"Run {run_id} not found")
    return assessment


def list_assessments_for_batch(db: Session, batch_id: str) -> list[Assessment]:
    get_batch(db, batch_id)
    return list(db.scalars(select(Assessment).where(Assessment.batch_id == batch_id).order_by(Assessment.created_at.desc())))


def submit_domain_result(db: Session, assessment_id: str, payload: DomainResultSubmit) -> AssessmentResult:
    assessment = get_assessment(db, assessment_id)
    requested = json.loads(assessment.requested_domains)
    if payload.domain not in requested:
        raise InvalidAssessmentInputError(f"Domain '{payload.domain}' was not requested for run {assessment.run_id} (requested: {', '.join(requested)}).")
    result = AssessmentResult(assessment_id=assessment.id, batch_id=assessment.batch_id, domain=payload.domain, assessment_version=payload.assessment_version, status=payload.status, evaluated_resources=payload.evaluated_resources, ready=payload.ready, warning=payload.warning, blocked=payload.blocked, can_proceed=payload.can_proceed, blockers=json.dumps([b.model_dump() for b in payload.blockers]), recommended_actions=json.dumps([a.model_dump() for a in payload.recommended_actions]), error_code=payload.error_code)
    db.add(result)
    db.commit()
    db.refresh(result)
    audit_service.log_event(db, "DOMAIN_RESULT_SUBMITTED", "AssessmentResult", result.id, batch_id=assessment.batch_id, run_id=assessment.run_id, detail={"domain": payload.domain, "status": payload.status, "blockerCount": len(payload.blockers)})
    _maybe_finalize_assessment(db, assessment, requested)
    return result


def _latest_results_by_domain(db: Session, assessment_id: str) -> dict[str, AssessmentResult]:
    latest: dict[str, AssessmentResult] = {}
    for result in db.scalars(select(AssessmentResult).where(AssessmentResult.assessment_id == assessment_id).order_by(AssessmentResult.created_at.asc())):
        latest[result.domain] = result
    return latest


def _maybe_finalize_assessment(db: Session, assessment: Assessment, requested: list[str]) -> None:
    latest = _latest_results_by_domain(db, assessment.id)
    if not all(domain in latest for domain in requested):
        return
    domain_statuses = {domain: latest[domain].status for domain in requested}
    verdict = calculate_readiness(domain_statuses, requested)
    assessment.run_status = "COMPLETED"
    assessment.overall_status = verdict.overall_status
    assessment.can_proceed = verdict.can_proceed
    assessment.blocker_count = sum(result.blocked for result in latest.values())
    assessment.warning_count = sum(result.warning for result in latest.values())
    assessment.completed_at = datetime.now(timezone.utc).isoformat()
    assessment.batch.readiness_status = verdict.overall_status if verdict.overall_status in ("READY", "WARNING", "BLOCKED") else "BLOCKED"
    db.commit()
    audit_service.log_event(db, "ASSESSMENT_COMPLETED", "Assessment", assessment.id, batch_id=assessment.batch_id, run_id=assessment.run_id, detail={"overallStatus": verdict.overall_status, "canProceed": verdict.can_proceed, "reason": verdict.reason})


def get_latest_domain_result(db: Session, batch_id: str, domain: str) -> AssessmentResult | None:
    get_batch(db, batch_id)
    return db.scalar(select(AssessmentResult).where(AssessmentResult.batch_id == batch_id, AssessmentResult.domain == domain).order_by(AssessmentResult.created_at.desc()).limit(1))
