from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class TenantCreate(BaseModel):
    display_name: str
    tenant_domain: str
    role: str = Field(pattern="^(SOURCE|TARGET)$")

class TenantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    display_name: str
    tenant_domain: str
    role: str

class MigrationProjectCreate(BaseModel):
    name: str
    description: str | None = None
    migration_code: str | None = Field(default=None, description="Optional; auto-generated like MASS053 if omitted.")
    source_tenant_id: str
    target_tenant_id: str

class MigrationProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    migration_code: str
    name: str
    description: str | None
    status: str
    source_tenant_id: str
    target_tenant_id: str
    created_at: datetime
    updated_at: datetime

class MigrationProjectDetail(MigrationProjectOut):
    wave_count: int = 0
    batch_count: int = 0

class MigrationWaveCreate(BaseModel):
    name: str
    sequence: int = 1

class MigrationWaveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    migration_project_id: str
    name: str
    sequence: int
    status: str
    created_at: datetime
    updated_at: datetime
