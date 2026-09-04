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
    hive_id: Optional[str] = None


class BatchResponse(BaseModel):
    """Read schema — serialised directly from BatchModel ORM row."""
    batch_id: str
    beekeeper_name: str
    farm_location: str
    harvest_date: str
    quantity_kg: float
    created_at: datetime
    qr_code_url: Optional[str] = None
    hive_id: Optional[str] = None
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


# ─── IoT Telemetry ────────────────────────────────────────────────────────────
# Appended from review-iot — does not touch existing schemas above.

class TelemetryInput(BaseModel):
    """
    Incoming telemetry payload from IoT hardware (ESP32).
    Accepts camelCase JSON keys from firmware; maps to snake_case internally.
    """
    model_config = ConfigDict(populate_by_name=True)

    device_id: str = Field(alias="deviceId")
    hive_id: str = Field(alias="hiveId")
    internal_temperature: float = Field(alias="internalTemperature")
    humidity: float
    hive_weight: float = Field(alias="hiveWeight")
    external_temperature: float = Field(alias="externalTemperature")
    temperature_delta: float = Field(alias="temperatureDelta")
    health_score: int = Field(alias="healthScore")
    status: str
    device_timestamp: Optional[int] = Field(default=None, alias="deviceTimestamp")


class TelemetryResponse(BaseModel):
    """Minimal response after persisting a telemetry reading."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    reading_id: int = Field(validation_alias="id")
    hive_id: str
    server_timestamp: datetime


class TelemetryDetail(BaseModel):
    """Full telemetry reading — used by dashboard and history endpoints."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    reading_id: int = Field(validation_alias="id")
    hive_id: str
    device_id: str
    internal_temperature: float
    humidity: float
    hive_weight: float
    external_temperature: float
    temperature_delta: float
    health_score: int
    status: str
    device_timestamp: Optional[int] = None
    server_timestamp: datetime


class HiveSummary(BaseModel):
    """Lightweight hive record for dropdowns and list views."""
    model_config = ConfigDict(from_attributes=True)

    hive_id: str
    device_id: str
    name: Optional[str] = None
    location: Optional[str] = None
