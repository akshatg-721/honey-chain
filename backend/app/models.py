from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .database import Base


# ─── BATCH & LEDGER MODELS ───────────────────────────────────────────────────

class Batch(Base):
    __tablename__ = "batches"

    batch_id = Column(String, primary_key=True, index=True)
    beekeeper_name = Column(String, nullable=False)
    farm_location = Column(String, nullable=False)
    harvest_date = Column(String, nullable=False)
    quantity_kg = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    qr_code_url = Column(String, nullable=True)
    hive_id = Column(String, ForeignKey("hives.hive_id"), nullable=True, index=True)

    # 1:N relationship with ledger checkpoint blocks
    ledger_blocks = relationship("LedgerBlock", back_populates="batch", cascade="all, delete-orphan", order_by="LedgerBlock.id")
    hive = relationship("Hive", back_populates="batches")


class LedgerBlock(Base):
    __tablename__ = "ledger_blocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, ForeignKey("batches.batch_id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    hash = Column(String(64), nullable=False)
    data = Column(JSON, nullable=False)

    batch = relationship("Batch", back_populates="ledger_blocks")


# ─── IOT & TELEMETRY MODELS ──────────────────────────────────────────────────

class Hive(Base):
    __tablename__ = "hives"

    hive_id = Column(String, primary_key=True, index=True)
    device_id = Column(String, nullable=False)
    location = Column(String, nullable=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # 1:N relationship with telemetry readings
    readings = relationship("TelemetryReading", back_populates="hive", cascade="all, delete-orphan", order_by="TelemetryReading.id.desc()")
    batches = relationship("Batch", back_populates="hive")


class TelemetryReading(Base):
    __tablename__ = "telemetry_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hive_id = Column(String, ForeignKey("hives.hive_id"), nullable=False, index=True)
    device_id = Column(String, nullable=False)

    internal_temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    hive_weight = Column(Float, nullable=True)
    external_temperature = Column(Float, nullable=True)
    temperature_delta = Column(Float, nullable=True)

    health_score = Column(Integer, nullable=True)
    status = Column(String, nullable=True)

    device_timestamp = Column(BigInteger, nullable=True)
    server_timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    hive = relationship("Hive", back_populates="readings")
