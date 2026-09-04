from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.blockchain import verify_chain
from app.database import get_db
from app.models import BatchModel
from app.schemas import VerifyResponse

# NOTE: prefix is defined here, so do NOT pass prefix="/verify" again in main.py.
# Just use: app.include_router(verify.router)
router = APIRouter(prefix="/verify", tags=["Verify"])


@router.get("/{batch_id}", response_model=VerifyResponse)
def verify_batch(batch_id: str, db: Session = Depends(get_db)):
    """
    Public consumer endpoint — verify the integrity of a honey batch's hash chain.

    Returns the full batch (with all checkpoints) plus a `chain_valid` boolean.
    `chain_valid: true`  → every block is intact and correctly linked, batch is authentic.
    `chain_valid: false` → the chain has been tampered with, do not trust this batch.
    """
    batch = db.query(BatchModel).filter(BatchModel.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found.")

    # batch.checkpoints is already ordered by timestamp ASC (defined in the relationship)
    chain_valid = verify_chain(batch.checkpoints)

    return {"batch": batch, "chain_valid": chain_valid}
