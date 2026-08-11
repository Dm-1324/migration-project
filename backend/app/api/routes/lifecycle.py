from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.assessment import LifecycleTransitionOut, LifecycleTransitionRequest
from app.services import batch_service
from app.services.migration_service import NotFoundError

router = APIRouter(tags=["lifecycle"])

@router.post("/batches/{batch_id}/lifecycle/transition", response_model=LifecycleTransitionOut)
def transition_batch_lifecycle(batch_id: str, payload: LifecycleTransitionRequest, db: Session = Depends(get_db)):
    try:
        previous_state = batch_service.get_batch(db, batch_id).lifecycle_state
        batch, decision = batch_service.advance_lifecycle(db, batch_id, payload.target_state)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return LifecycleTransitionOut(batch_id=batch.id, previous_state=previous_state, current_state=batch.lifecycle_state, allowed=decision.allowed, reason=decision.reason)
