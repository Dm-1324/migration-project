from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class EvidenceCreate(BaseModel):
    batch_id: str
    domain: str = Field(pattern="^(Entra|ExchangeOnline|OneDrive)$")
    tool: str
    operation_id: str
    assessment_id: str | None = None
    affected_resource: str | None = None
    input_parameters: str | None = None
    normalized_result: str | None = None
    raw_output: str | None = None
    status: str = Field(pattern="^(SUCCEEDED|FAILED)$")
    duration_ms: int | None = None

class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    batch_id: str
    domain: str
    tool: str
    operation_id: str
    assessment_id: str | None
    affected_resource: str | None
    normalized_result: str | None
    raw_output: str | None
    status: str
    duration_ms: int | None
    created_at: datetime

class ExceptionCreate(BaseModel):
    batch_id: str
    domain: str = Field(pattern="^(Entra|ExchangeOnline|OneDrive)$")
    code: str
    description: str | None = None
    severity: str = Field(pattern="^(INFO|WARNING|BLOCKING)$")
    evidence_id: str | None = None
    affected_resource: str | None = None
    owner: str | None = None

class ExceptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    batch_id: str
    domain: str
    code: str
    description: str | None
    severity: str
    status: str
    evidence_id: str | None
    affected_resource: str | None
    owner: str | None
    created_at: datetime

class ExceptionStatusUpdate(BaseModel):
    status: str = Field(pattern="^(OPEN|ACKNOWLEDGED|RESOLVED)$")
