from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.assessment import REQUIRED_DOMAINS
from app.policies.readiness import ReadinessVerdict, calculate_readiness
from app.services.assessment_service import get_latest_domain_result
from app.services.batch_service import get_batch

FRESHNESS_WINDOW_HOURS = 24


def _is_stale(created_at: datetime) -> bool:
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - created_at > timedelta(hours=FRESHNESS_WINDOW_HOURS)


def get_current_readiness(db: Session, batch_id: str, required_domains: list[str] | None = None) -> tuple[ReadinessVerdict, dict[str, str | None], str | None]:
    get_batch(db, batch_id)
    required = required_domains or list(REQUIRED_DOMAINS)
    domain_statuses: dict[str, str | None] = {}
    latest_run_id: str | None = None
    for domain in required:
        result = get_latest_domain_result(db, batch_id, domain)
        if result is None or _is_stale(result.created_at):
            domain_statuses[domain] = None
            continue
        domain_statuses[domain] = result.status
        latest_run_id = result.assessment.run_id
    verdict = calculate_readiness(domain_statuses, required)
    return verdict, domain_statuses, latest_run_id
