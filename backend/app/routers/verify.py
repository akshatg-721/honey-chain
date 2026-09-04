from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..blockchain import verify_chain
from ..database import get_db
from ..models import Batch
from ..schemas import VerifyResponse
from .batches import format_batch_response

router = APIRouter(prefix="/verify", tags=["verify"])


@router.get("/{batch_id}", response_model=VerifyResponse)
def verify_batch(batch_id: str, db: Session = Depends(get_db)):
    """
    Public consumer verification endpoint.
    Retrieves the entire ledger chain for a batch, recomputes SHA-256 hashes live,
    and returns whether the provenance chain is authentic and untampered.
    """
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found")

    # Format stored chain blocks for the verification engine
    chain = [
        {
            "data": block.data,
            "previous_hash": block.previous_hash,
            "timestamp": block.timestamp,
            "hash": block.hash,
        }
        for block in batch.ledger_blocks
    ]

    # Cryptographically recompute all hashes and validate linkages
    verification = verify_chain(chain)

    return VerifyResponse(
        batch=format_batch_response(batch),
        chain_valid=verification["valid"],
        hive_id=batch.hive_id,
    )
