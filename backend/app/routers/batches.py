from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..blockchain import create_checkpoint_block, create_genesis_block
from ..database import get_db
from ..models import Batch, Hive, LedgerBlock
from ..qr import generate_qr_image, get_verification_url
from ..schemas import AddCheckpointInput, BatchResponse, CheckpointResponse, CreateBatchInput

router = APIRouter(prefix="/batches", tags=["batches"])


def format_batch_response(batch: Batch) -> BatchResponse:
    """Format SQLAlchemy Batch model and its ledger checkpoints into BatchResponse."""
    checkpoints = [
        CheckpointResponse(
            status=block.status,
            timestamp=block.timestamp,
            hash=block.hash,
            previous_hash=block.previous_hash,
        )
        for block in batch.ledger_blocks
    ]
    created_at_str = (
        batch.created_at.isoformat()
        if hasattr(batch.created_at, "isoformat")
        else str(batch.created_at)
    )
    return BatchResponse(
        batch_id=batch.batch_id,
        beekeeper_name=batch.beekeeper_name,
        farm_location=batch.farm_location,
        harvest_date=batch.harvest_date,
        quantity_kg=batch.quantity_kg,
        created_at=created_at_str,
        qr_code_url=batch.qr_code_url,
        hive_id=batch.hive_id,
        checkpoints=checkpoints,
    )


@router.get("/", response_model=List[BatchResponse])
def list_batches(db: Session = Depends(get_db)):
    """List all registered honey batches along with their checkpoint timeline."""
    batches = db.query(Batch).order_by(Batch.created_at.desc()).all()
    return [format_batch_response(b) for b in batches]


@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    """Retrieve details and full ledger timeline for a specific batch."""
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found")
    return format_batch_response(batch)


@router.get("/{batch_id}/qr")
def get_batch_qr(batch_id: str, db: Session = Depends(get_db)):
    """
    Generate and serve a real-time PNG QR code encoding the batch verification URL.
    Computed purely in-memory without filesystem exposure or static file mount.
    """
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found")

    image_bytes = generate_qr_image(batch_id)
    return Response(content=image_bytes, media_type="image/png")


@router.post("/", response_model=BatchResponse, status_code=201)
def create_batch(payload: CreateBatchInput, db: Session = Depends(get_db)):
    """
    Register a new honey batch and initialize block 0 (genesis block) in its ledger.
    Optionally links the batch to a validated smart hive.
    """
    # 1. Hive validation: If hive_id is specified, ensure it exists in the database
    if payload.hive_id is not None:
        hive = db.query(Hive).filter(Hive.hive_id == payload.hive_id).first()
        if hive is None:
            raise HTTPException(
                status_code=404,
                detail=f"Hive '{payload.hive_id}' not found. Cannot link batch to nonexistent hive.",
            )

    # 2. Generate unique batch ID: e.g. HCB-2026-001
    year = datetime.now(timezone.utc).year
    count = db.query(Batch).count()
    batch_id = f"HCB-{year}-{count + 1:03d}"

    # 3. Construct genesis payload (only include hive_id if provided)
    genesis_data = {
        "batch_id": batch_id,
        "beekeeper_name": payload.beekeeper_name,
        "farm_location": payload.farm_location,
        "harvest_date": payload.harvest_date,
        "quantity_kg": payload.quantity_kg,
    }
    if payload.hive_id is not None:
        genesis_data["hive_id"] = payload.hive_id

    # 4. Cryptographic Genesis Block creation via blockchain engine
    genesis_block = create_genesis_block(batch_data=genesis_data)

    # 5. Generate verification web URL
    qr_url = get_verification_url(batch_id)

    # 6. Persist Batch and Genesis LedgerBlock atomically
    new_batch = Batch(
        batch_id=batch_id,
        beekeeper_name=payload.beekeeper_name,
        farm_location=payload.farm_location,
        harvest_date=payload.harvest_date,
        quantity_kg=payload.quantity_kg,
        created_at=datetime.now(timezone.utc),
        qr_code_url=qr_url,
        hive_id=payload.hive_id,
    )
    db.add(new_batch)

    first_block = LedgerBlock(
        batch_id=batch_id,
        status=genesis_block["data"]["status"],
        timestamp=genesis_block["timestamp"],
        previous_hash=genesis_block["previous_hash"],
        hash=genesis_block["hash"],
        data=genesis_block["data"],
    )
    db.add(first_block)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to register batch and genesis block")

    db.refresh(new_batch)
    return format_batch_response(new_batch)


@router.post("/{batch_id}/checkpoints", response_model=BatchResponse)
def add_checkpoint(batch_id: str, payload: AddCheckpointInput, db: Session = Depends(get_db)):
    """
    Append a supply-chain checkpoint (e.g. processed, packaged, shipped) to a batch's hash chain.
    """
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found")

    # Get the last block in this batch's chain to link to
    last_block = (
        db.query(LedgerBlock)
        .filter(LedgerBlock.batch_id == batch_id)
        .order_by(LedgerBlock.id.desc())
        .first()
    )
    if last_block is None:
        raise HTTPException(status_code=500, detail="Batch has no prior blocks to chain to")

    # Cryptographically create next block linked to previous hash
    checkpoint_block = create_checkpoint_block(
        status=payload.status,
        previous_hash=last_block.hash,
    )

    new_block = LedgerBlock(
        batch_id=batch_id,
        status=checkpoint_block["data"]["status"],
        timestamp=checkpoint_block["timestamp"],
        previous_hash=checkpoint_block["previous_hash"],
        hash=checkpoint_block["hash"],
        data=checkpoint_block["data"],
    )
    db.add(new_block)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record checkpoint to ledger")

    db.refresh(batch)
    return format_batch_response(batch)
