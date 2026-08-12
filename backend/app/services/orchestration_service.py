from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.assessment import REQUIRED_DOMAINS, Assessment
from app.schemas.assessment import AssessmentStartRequest
from app.services import assessment_service, batch_service
from app.tools.entra import assess as entra_tool
from app.tools.exchange import assess as exchange_tool
from app.tools.onedrive import assess as onedrive_tool

_TOOL_BY_DOMAIN = {"Entra": entra_tool.run, "ExchangeOnline": exchange_tool.run, "OneDrive": onedrive_tool.run}


def run_batch_assessment(
    db: Session,
    batch_id: str,
    domains: list[str] | None = None,
    force_refresh: bool = False,
    simulate_errors: dict[str, str] | None = None,
) -> Assessment:
    domains = domains or list(REQUIRED_DOMAINS)
    simulate_errors = simulate_errors or {}
    batch = batch_service.get_batch(db, batch_id)
    resources = batch_service.list_resources(db, batch_id)
    assessment = assessment_service.start_assessment(
        db, batch_id, AssessmentStartRequest(domains=domains, force_refresh=force_refresh)
    )
    for domain in domains:
        tool_fn = _TOOL_BY_DOMAIN[domain]
        result_payload = tool_fn(db, batch, resources, simulate_error=simulate_errors.get(domain))
        assessment_service.submit_domain_result(db, assessment.id, result_payload)
    return assessment_service.get_assessment(db, assessment.id)
