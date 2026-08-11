from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.assessment import REQUIRED_DOMAINS

class AssessmentStartRequest(BaseModel):
    domains: list[str] = Field(default_factory=lambda: list(REQUIRED_DOMAINS))
    force_refresh: bool = False

class AssessmentStartResponse(BaseModel):
    run_id: str
    status: str
    batch_id: str

class BlockerItem(BaseModel):
    code: str
    severity: str = Field(pattern="^(INFO|WARNING|BLOCKING)$")
    evidence_ref: str | None = None

class RecommendedActionItem(BaseModel):
    action: str
    risk: str = Field(pattern="^(GREEN|AMBER|RED)$")

class DomainResultSubmit(BaseModel):
    domain: str = Field(pattern="^(Entra|ExchangeOnline|OneDrive)$")
    assessment_version: str = "1.0"
    status: str = Field(pattern="^(READY|WARNING|BLOCKED|UNAVAILABLE)$")
    evaluated_resources: int = Field(ge=0)
    ready: int = Field(ge=0, default=0)
    warning: int = Field(ge=0, default=0)
    blocked: int = Field(ge=0, default=0)
    can_proceed: bool
    blockers: list[BlockerItem] = Field(default_factory=list)
    recommended_actions: list[RecommendedActionItem] = Field(default_factory=list)
    error_code: str | None = None

class DomainResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    assessment_id: str
    batch_id: str
    domain: str
    assessment_version: str
    status: str
    evaluated_resources: int
    ready: int
    warning: int
    blocked: int
    can_proceed: bool
    blockers: list[BlockerItem] = Field(default_factory=list)
    recommended_actions: list[RecommendedActionItem] = Field(default_factory=list)
    error_code: str | None
    created_at: datetime

class AssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    run_id: str
    batch_id: str
    run_status: str
    overall_status: str | None
    can_proceed: bool | None
    blocker_count: int
    warning_count: int
    created_at: datetime
    completed_at: str | None

class AssessmentDetail(AssessmentOut):
    results: list[DomainResultOut] = Field(default_factory=list)

class ReadinessOut(BaseModel):
    batch_id: str
    status: str
    can_proceed: bool
    reason: str
    domains: dict[str, str | None]
    blockers: int
    warnings: int
    assessment_run_id: str | None = None

class RunStepOut(BaseModel):
    name: str
    status: str

class RunStatusOut(BaseModel):
    run_id: str
    status: str
    steps: list[RunStepOut]

class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    event_type: str
    entity_type: str
    entity_id: str
    migration_id: str | None
    batch_id: str | None
    run_id: str | None
    operation_id: str | None
    detail: str | None
    created_at: datetime

class LifecycleTransitionRequest(BaseModel):
    target_state: str

class LifecycleTransitionOut(BaseModel):
    batch_id: str
    previous_state: str
    current_state: str
    allowed: bool
    reason: str
