from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.migration import Tenant
from app.schemas.migration import MigrationProjectCreate, MigrationProjectDetail, MigrationProjectOut, TenantCreate, TenantOut
from app.services import migration_service
from app.services.migration_service import NotFoundError

router = APIRouter(tags=["migrations"])

@router.post("/tenants", response_model=TenantOut, status_code=201)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)) -> Tenant:
    tenant = Tenant(**payload.model_dump())
    db.add(tenant); db.commit(); db.refresh(tenant)
    return tenant

@router.get("/tenants", response_model=list[TenantOut])
def list_tenants(db: Session = Depends(get_db)) -> list[Tenant]:
    return db.query(Tenant).order_by(Tenant.created_at.desc()).all()

@router.post("/migrations", response_model=MigrationProjectOut, status_code=201)
def create_migration(payload: MigrationProjectCreate, db: Session = Depends(get_db)):
    try: return migration_service.create_migration(db, payload)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("/migrations", response_model=list[MigrationProjectOut])
def list_migrations(status: str | None = None, db: Session = Depends(get_db)):
    return migration_service.list_migrations(db, status=status)

@router.get("/migrations/{migration_id}", response_model=MigrationProjectDetail)
def get_migration(migration_id: str, db: Session = Depends(get_db)):
    try: project = migration_service.get_migration(db, migration_id)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e
    wave_count, batch_count = migration_service.get_migration_counts(db, migration_id)
    return MigrationProjectDetail(**MigrationProjectOut.model_validate(project).model_dump(), wave_count=wave_count, batch_count=batch_count)

@router.get("/migrations/{migration_id}/lifecycle")
def get_migration_lifecycle(migration_id: str, db: Session = Depends(get_db)):
    try: project = migration_service.get_migration(db, migration_id)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e
    return {"migrationId": project.id, "migrationCode": project.migration_code, "status": project.status}
