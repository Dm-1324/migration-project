from __future__ import annotations

from sqlalchemy.orm import Session

from app.adapters.sharepoint import check_site
from app.models.batch import Batch, Resource
from app.schemas.assessment import DomainResultSubmit
from app.tools.common import run_domain_assessment


def run(db: Session, batch: Batch, resources: list[Resource], simulate_error: str | None = None) -> DomainResultSubmit:
    return run_domain_assessment(db, batch, resources, domain="OneDrive", check_fn=check_site, simulate_error=simulate_error)
