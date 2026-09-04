from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


# ─── IOT & TELEMETRY SCHEMAS ──────────────────────────────────────────────────

class TelemetryInput(BaseModel):
    """
    Incoming telemetry payload from IoT hardware / ESP32.
    Translates wire camelCase JSON keys into Python snake_case attributes.
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
    """API response after persisting a telemetry reading."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    reading_id: int = Field(validation_alias="id")
    hive_id: str
    server_timestamp: datetime


class TelemetryDetail(BaseModel):
    """Full telemetry reading details for dashboard and analytics."""
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


class HiveCreate(BaseModel):
    """Payload to register a new physical hive."""
    hive_id: str
    device_id: str
    location: Optional[str] = None
    name: Optional[str] = None


class HiveResponse(BaseModel):
    """Details of a registered hive."""
    model_config = ConfigDict(from_attributes=True)

    hive_id: str
    device_id: str
    location: Optional[str] = None
    name: Optional[str] = None
    created_at: datetime


class HiveSummary(BaseModel):
    """Summary of a hive for selection dropdowns."""
    model_config = ConfigDict(from_attributes=True)

    hive_id: str
    device_id: str
    name: Optional[str] = None
    location: Optional[str] = None


# ─── BATCH & SUPPLY CHAIN SCHEMAS ─────────────────────────────────────────────

CheckpointStatus = Literal["harvested", "processed", "packaged", "shipped"]


class CheckpointResponse(BaseModel):
    """Public checkpoint representation in the blockchain timeline."""
    model_config = ConfigDict(from_attributes=True)

    status: str
    timestamp: str
    hash: str
    previous_hash: str


class CreateBatchInput(BaseModel):
    """Payload to register a new honey batch."""
    beekeeper_name: str
    farm_location: str
    harvest_date: str
    quantity_kg: float
    hive_id: Optional[str] = None


class AddCheckpointInput(BaseModel):
    """Payload to record a stage transition in the ledger."""
    status: CheckpointStatus


class BatchResponse(BaseModel):
    """Full batch representation matching frontend Batch interface."""
    model_config = ConfigDict(from_attributes=True)

    batch_id: str
    beekeeper_name: str
    farm_location: str
    harvest_date: str
    quantity_kg: float
    created_at: str
    qr_code_url: Optional[str] = None
    hive_id: Optional[str] = None
    checkpoints: List[CheckpointResponse] = []


class VerifyResponse(BaseModel):
    """Response returned by public verification endpoint."""
    batch: BatchResponse
    chain_valid: bool
    hive_id: Optional[str] = None
