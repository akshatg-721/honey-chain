from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid() -> str:
    """Generate a short 8-char hex ID (first segment of a UUID4)."""
    return uuid4().hex[:8]


def _uuid_full() -> str:
    """Generate a full UUID4 hex string for checkpoint PKs."""
    return uuid4().hex


class BatchModel(Base):
    __tablename__ = "batches"

    batch_id = Column(String, primary_key=True, default=_uuid, index=True)
    beekeeper_name = Column(String, nullable=False)
    farm_location = Column(String, nullable=False)
    harvest_date = Column(String, nullable=False)          # stored as ISO date string, e.g. "2024-08-15"
    quantity_kg = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    qr_code_url = Column(String, nullable=True)
    hive_id = Column(String, ForeignKey("hives.hive_id"), nullable=True, index=True)

    checkpoints = relationship(
        "CheckpointModel",
        back_populates="batch",
        order_by="CheckpointModel.timestamp.asc()",
        cascade="all, delete-orphan",
    )


class CheckpointModel(Base):
    __tablename__ = "checkpoints"

    id = Column(String, primary_key=True, default=_uuid_full, index=True)
    batch_id = Column(
        String,
        ForeignKey("batches.batch_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String, nullable=False)                # one of: harvested | processed | packaged | shipped
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    hash = Column(String(64), nullable=False)
    previous_hash = Column(String(64), nullable=False)

    batch = relationship("BatchModel", back_populates="checkpoints")


# ─── IoT Telemetry ────────────────────────────────────────────────────────────
# Appended from review-iot — these classes are ADDITIVE and do not
# modify BatchModel or CheckpointModel in any way.

class Hive(Base):
    __tablename__ = "hives"

    hive_id   = Column(String, primary_key=True, index=True)
    device_id = Column(String, nullable=False)
    location  = Column(String, nullable=True)
    name      = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    readings = relationship(
        "TelemetryReading",
        back_populates="hive",
        cascade="all, delete-orphan",
        order_by="TelemetryReading.id.desc()",
    )


class TelemetryReading(Base):
    __tablename__ = "telemetry_readings"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    hive_id     = Column(String, ForeignKey("hives.hive_id"), nullable=False, index=True)
    device_id   = Column(String, nullable=False)

    internal_temperature  = Column(Float, nullable=True)
    humidity              = Column(Float, nullable=True)
    hive_weight           = Column(Float, nullable=True)
    external_temperature  = Column(Float, nullable=True)
    temperature_delta     = Column(Float, nullable=True)

    health_score      = Column(Integer, nullable=True)
    status            = Column(String,  nullable=True)
    device_timestamp  = Column(BigInteger, nullable=True)
    server_timestamp  = Column(DateTime, default=datetime.utcnow)

    hive = relationship("Hive", back_populates="readings")
