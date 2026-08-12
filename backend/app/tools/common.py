from __future__ import annotations

import json
import time
import uuid
from typing import Callable

from sqlalchemy.orm import Session

from app.adapters.base import ResourceCheckResult
from app.models.batch import Batch, Resource
from app.schemas.assessment import BlockerItem, DomainResultSubmit, RecommendedActionItem
from app.schemas.evidence import EvidenceCreate, ExceptionCreate
from app.services import evidence_service

SIMULATABLE_ERRORS = ("M365_TIMEOUT", "M365_THROTTLED", "AUTH_FAILED", "RESOURCE_NOT_FOUND", "UNKNOWN")


def _new_operation_id() -> str:
    return f"op-{uuid.uuid4().hex[:8]}"


def run_domain_assessment(
    db: Session,
    batch: Batch,
    resources: list[Resource],
    domain: str,
    check_fn: Callable[[Resource], ResourceCheckResult],
    simulate_error: str | None = None,
) -> DomainResultSubmit:
    if simulate_error:
        return _simulate_domain_failure(db, batch, domain, simulate_error)

    ready = warning = blocked = 0
    blockers: list[BlockerItem] = []
    recommended_actions: list[RecommendedActionItem] = []

    for resource in resources:
        start = time.perf_counter()
        result = check_fn(resource)
        duration_ms = max(1, int((time.perf_counter() - start) * 1000))
        affected = resource.target_identifier or resource.source_identifier

        evidence = evidence_service.record_evidence(
            db,
            EvidenceCreate(
                batch_id=batch.id,
                domain=domain,
                tool=result.tool,
                operation_id=_new_operation_id(),
                affected_resource=affected,
                normalized_result=json.dumps({"status": result.status, "code": result.code, "message": result.message}),
                raw_output=result.raw_output,
                status="SUCCEEDED",
                duration_ms=duration_ms,
            ),
        )

        if result.status == "READY":
            ready += 1
            continue
        if result.status == "WARNING":
            warning += 1
        else:
            blocked += 1

        blockers.append(BlockerItem(code=result.code, severity=result.severity, evidence_ref=evidence.id))
        evidence_service.record_exception(
            db,
            ExceptionCreate(
                batch_id=batch.id,
                domain=domain,
                code=result.code,
                description=result.message,
                severity=result.severity,
                evidence_id=evidence.id,
                affected_resource=affected,
            ),
        )
        if result.status == "BLOCKED":
            recommended_actions.append(RecommendedActionItem(action=f"REQUEST_{domain.upper()}_REMEDIATION", risk="AMBER"))

    overall_status = "BLOCKED" if blocked else ("WARNING" if warning else "READY")
    return DomainResultSubmit(
        domain=domain,
        status=overall_status,
        evaluated_resources=len(resources),
        ready=ready,
        warning=warning,
        blocked=blocked,
        can_proceed=overall_status == "READY",
        blockers=blockers,
        recommended_actions=recommended_actions,
    )


def _simulate_domain_failure(db: Session, batch: Batch, domain: str, error_code: str) -> DomainResultSubmit:
    evidence_service.record_evidence(
        db,
        EvidenceCreate(
            batch_id=batch.id,
            domain=domain,
            tool="mock-adapter",
            operation_id=_new_operation_id(),
            normalized_result=json.dumps({"error": error_code}),
            raw_output=f"Simulated failure: {error_code}. No resources were evaluated for domain '{domain}'.",
            status="FAILED",
            duration_ms=None,
        ),
    )
    return DomainResultSubmit(
        domain=domain,
        status="UNAVAILABLE",
        evaluated_resources=0,
        ready=0,
        warning=0,
        blocked=0,
        can_proceed=False,
        blockers=[],
        recommended_actions=[RecommendedActionItem(action="RETRY_ASSESSMENT", risk="AMBER")],
        error_code=error_code,
    )
