from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
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
