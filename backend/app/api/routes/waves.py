from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.migration import MigrationWaveCreate, MigrationWaveOut
from app.services import migration_service
from app.services.migration_service import NotFoundError
router = APIRouter(tags=["waves"])

@router.post("/migrations/{migration_id}/waves", response_model=MigrationWaveOut, status_code=201)
def create_wave(migration_id: str, payload: MigrationWaveCreate, db: Session = Depends(get_db)):
    try: return migration_service.create_wave(db, migration_id, payload)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("/migrations/{migration_id}/waves", response_model=list[MigrationWaveOut])
def list_waves(migration_id: str, db: Session = Depends(get_db)):
    try: return migration_service.list_waves(db, migration_id)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e

@router.get("/waves/{wave_id}", response_model=MigrationWaveOut)
def get_wave(wave_id: str, db: Session = Depends(get_db)):
    try: return migration_service.get_wave(db, wave_id)
    except NotFoundError as e: raise HTTPException(status_code=404, detail=str(e)) from e
