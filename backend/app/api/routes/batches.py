from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.batch import BatchCreate, BatchDetail, BatchOut
from app.services import batch_service
from app.services.migration_service import NotFoundError
router = APIRouter(tags=["batches"])

@router.post("/waves/{wave_id}/batches", response_model=BatchOut, status_code=201)
def create_batch(wave_id: str, payload: BatchCreate, db: Session = Depends(get_db)):
    try: return batch_service.create_batch(db, wave_id, payload)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("/waves/{wave_id}/batches", response_model=list[BatchOut])
def list_batches(wave_id: str, db: Session = Depends(get_db)):
    try: return batch_service.list_batches(db, wave_id)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("/batches/{batch_id}", response_model=BatchDetail)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    try: batch = batch_service.get_batch(db, batch_id)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e
    return BatchDetail(**BatchOut.model_validate(batch).model_dump(), resource_count=batch_service.get_resource_count(db, batch_id))
