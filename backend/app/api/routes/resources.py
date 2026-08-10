from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.batch import ResourceCreate, ResourceOut
from app.services import batch_service
from app.services.migration_service import NotFoundError
router = APIRouter(tags=["resources"])

@router.post("/batches/{batch_id}/resources", response_model=ResourceOut, status_code=201)
def add_resource(batch_id: str, payload: ResourceCreate, db: Session = Depends(get_db)):
    try: return batch_service.add_resource(db, batch_id, payload)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("/batches/{batch_id}/resources", response_model=list[ResourceOut])
def list_resources(batch_id: str, db: Session = Depends(get_db)):
    try: return batch_service.list_resources(db, batch_id)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e
