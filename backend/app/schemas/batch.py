from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ResourceCreate(BaseModel):
    resource_type: str = Field(pattern="^(USER|MAILBOX|SITE|GROUP)$")
    display_name: str
    source_identifier: str
    target_identifier: str | None = None

class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    batch_id: str
    resource_type: str
    display_name: str
    source_identifier: str
    target_identifier: str | None
    created_at: datetime

class BatchCreate(BaseModel):
    name: str
    batch_code: str | None = Field(default=None, description="Optional; auto-generated like BATCH-001 if omitted.")

class BatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    batch_code: str
    wave_id: str
    name: str
    lifecycle_state: str
    readiness_status: str
    created_at: datetime
    updated_at: datetime

class BatchDetail(BatchOut):
    resource_count: int = 0
