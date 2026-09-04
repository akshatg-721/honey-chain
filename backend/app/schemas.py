from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# Valid supply-chain statuses — must match frontend CheckpointStatus union
VALID_STATUSES = {"harvested", "processed", "packaged", "shipped"}


# ─── Checkpoint ───────────────────────────────────────────────────────────────

class CheckpointBase(BaseModel):
    status: str
    timestamp: datetime
    hash: str
    previous_hash: str


class CheckpointResponse(CheckpointBase):
    """Read schema — serialised directly from CheckpointModel ORM row."""
    model_config = ConfigDict(from_attributes=True)


# ─── Batch ────────────────────────────────────────────────────────────────────

class CreateBatchInput(BaseModel):
    beekeeper_name: str
    farm_location: str
    harvest_date: str       # ISO date string, e.g. "2024-08-15"
    quantity_kg: float


class BatchResponse(BaseModel):
    """Read schema — serialised directly from BatchModel ORM row."""
    batch_id: str
    beekeeper_name: str
    farm_location: str
    harvest_date: str
    quantity_kg: float
    created_at: datetime
    qr_code_url: Optional[str] = None
    checkpoints: List[CheckpointResponse]

    model_config = ConfigDict(from_attributes=True)


# ─── Verify ───────────────────────────────────────────────────────────────────

class VerifyResponse(BaseModel):
    batch: BatchResponse
    chain_valid: bool


# ─── Checkpoint input ─────────────────────────────────────────────────────────

class AddCheckpointInput(BaseModel):
    status: str = Field(
        ...,
        description="Supply-chain stage. Must be one of: harvested, processed, packaged, shipped.",
    )

    def model_post_init(self, __context: object) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{self.status}'. Must be one of: {sorted(VALID_STATUSES)}"
            )
