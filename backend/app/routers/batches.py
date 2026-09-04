from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.blockchain import generate_hash
from app.database import get_db
from app.models import BatchModel, CheckpointModel
from app.qr import generate_qr_code
from app.schemas import AddCheckpointInput, BatchResponse, CreateBatchInput

# NOTE: prefix is defined here, so do NOT pass prefix="/batches" again in main.py.
# Just use: app.include_router(batches.router)
router = APIRouter(prefix="/batches", tags=["Batches"])

# Genesis sentinel — must match the value checked in blockchain.verify_chain()
GENESIS_PREVIOUS_HASH = "0"


def _make_batch_id(db: Session) -> str:
    """
    Generate a human-readable batch ID: HCB-<YYYY>-<NNN>
    Counts existing batches whose batch_id starts with the current year
    and increments. Falls back to a 6-char UUID suffix if DB count fails.
    """
    year = datetime.utcnow().year
    prefix = f"HCB-{year}-"
    count = db.query(BatchModel).filter(BatchModel.batch_id.like(f"{prefix}%")).count()
    return f"{prefix}{str(count + 1).zfill(3)}"


# ─── GET /batches/ ────────────────────────────────────────────────────────────

@router.get("/", response_model=list[BatchResponse])
def list_batches(db: Session = Depends(get_db)):
    """Return all batches, newest first."""
    batches = db.query(BatchModel).order_by(BatchModel.created_at.desc()).all()
    return batches


# ─── GET /batches/{batch_id} ──────────────────────────────────────────────────

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    """Return a single batch by its ID."""
    batch = db.query(BatchModel).filter(BatchModel.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found.")
    return batch


# ─── POST /batches/ ───────────────────────────────────────────────────────────

@router.post("/", response_model=BatchResponse, status_code=201)
def create_batch(payload: CreateBatchInput, db: Session = Depends(get_db)):
    """
    Register a new honey batch and record its genesis checkpoint (harvested).

    Steps:
      1. Generate a readable batch_id (HCB-YYYY-NNN).
      2. Generate a QR code URL for the consumer verify page.
      3. Persist the BatchModel row.
      4. Create the genesis CheckpointModel (status=harvested, previous_hash=GENESIS sentinel).
      5. Compute and store the block hash.
    """
    batch_id = _make_batch_id(db)
    qr_code_url = generate_qr_code(batch_id)
    now = datetime.utcnow()

    # 1. Create the batch row
    batch = BatchModel(
        batch_id=batch_id,
        beekeeper_name=payload.beekeeper_name,
        farm_location=payload.farm_location,
        harvest_date=payload.harvest_date,
        quantity_kg=payload.quantity_kg,
        created_at=now,
        qr_code_url=qr_code_url,
    )
    db.add(batch)
    db.flush()  # flush so FK is satisfied before checkpoint insert

    # 2. Create the genesis checkpoint
    genesis_timestamp = datetime.utcnow()
    genesis_hash = generate_hash(
        batch_id=batch_id,
        status="harvested",
        timestamp=genesis_timestamp,
        previous_hash=GENESIS_PREVIOUS_HASH,
    )
    genesis_checkpoint = CheckpointModel(
        batch_id=batch_id,
        status="harvested",
        timestamp=genesis_timestamp,
        hash=genesis_hash,
        previous_hash=GENESIS_PREVIOUS_HASH,
    )
    db.add(genesis_checkpoint)

    db.commit()
    db.refresh(batch)
    return batch


# ─── POST /batches/{batch_id}/checkpoints ────────────────────────────────────

@router.post("/{batch_id}/checkpoints", response_model=BatchResponse)
def add_checkpoint(
    batch_id: str,
    payload: AddCheckpointInput,
    db: Session = Depends(get_db),
):
    """
    Append a new supply-chain checkpoint to an existing batch.

    Steps:
      1. Verify the batch exists (404 if not).
      2. Get the most recent checkpoint's hash — this becomes the new block's previous_hash.
      3. Compute the new block's hash.
      4. Persist the CheckpointModel row.
    """
    # 1. Fetch the batch
    batch = db.query(BatchModel).filter(BatchModel.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found.")

    # 2. Get the latest checkpoint's hash to use as previous_hash
    latest = (
        db.query(CheckpointModel)
        .filter(CheckpointModel.batch_id == batch_id)
        .order_by(CheckpointModel.timestamp.desc())
        .first()
    )
    previous_hash = latest.hash if latest else GENESIS_PREVIOUS_HASH

    # 3. Compute the new block's hash
    new_timestamp = datetime.utcnow()
    new_hash = generate_hash(
        batch_id=batch_id,
        status=payload.status,
        timestamp=new_timestamp,
        previous_hash=previous_hash,
    )

    # 4. Persist the new checkpoint
    checkpoint = CheckpointModel(
        batch_id=batch_id,
        status=payload.status,
        timestamp=new_timestamp,
        hash=new_hash,
        previous_hash=previous_hash,
    )
    db.add(checkpoint)
    db.commit()
    db.refresh(batch)
    return batch
