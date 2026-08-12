from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.models.assessment import REQUIRED_DOMAINS

SIMULATABLE_ERROR_CODES = Literal["M365_TIMEOUT", "M365_THROTTLED", "AUTH_FAILED", "RESOURCE_NOT_FOUND", "UNKNOWN"]


class ToolAssessRequest(BaseModel):
    assessment_id: str
    simulate_error: SIMULATABLE_ERROR_CODES | None = Field(default=None)


class StartBatchAssessmentRequest(BaseModel):
    domains: list[str] = Field(default_factory=lambda: list(REQUIRED_DOMAINS))
    force_refresh: bool = False
    simulate_errors: dict[str, SIMULATABLE_ERROR_CODES] | None = Field(default=None)


class BlockerOut(BaseModel):
    id: str
    domain: str
    code: str
    description: str | None
    severity: str
    status: str
    affected_resource: str | None
    evidence_id: str | None


class CopilotBatchContext(BaseModel):
    batch_id: str
    batch_code: str
    migration_id: str
    migration_code: str
    lifecycle_state: str
    readiness_status: str
    domain_status: dict[str, str | None]
    blocker_count: int
    warning_count: int
    latest_run_id: str | None
    evidence_refs: list[str]


class CopilotMigrationContext(BaseModel):
    migration_id: str
    migration_code: str
    name: str
    status: str
    wave_count: int
    batch_count: int
    blocked_batch_count: int


class CodeResolverOut(BaseModel):
    id: str
    code: str
    type: str
