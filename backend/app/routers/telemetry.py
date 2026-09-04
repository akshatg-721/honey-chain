from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Hive, TelemetryReading
from app.schemas import HiveSummary, TelemetryDetail, TelemetryInput, TelemetryResponse

router = APIRouter(prefix="/api/hives", tags=["Telemetry"])

ALLOWED_STATUSES = {"HEALTHY", "WARNING", "CRITICAL"}


@router.post("/telemetry", response_model=TelemetryResponse, status_code=200)
def ingest_telemetry(payload: TelemetryInput, db: Session = Depends(get_db)):
    """
    Ingest a sensor telemetry reading from an IoT device (ESP32).
    - Auto-registers the Hive on first reading.
    - Rejects device_id mismatch (HTTP 409).
    - Validates health_score (0–100) and allowed statuses.
    - Single atomic commit.
    """
    if not (0 <= payload.health_score <= 100):
        raise HTTPException(status_code=422, detail="health_score must be between 0 and 100")

    if payload.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"status must be one of {sorted(ALLOWED_STATUSES)}",
        )

    hive = db.query(Hive).filter(Hive.hive_id == payload.hive_id).first()
    if hive is None:
        hive = Hive(hive_id=payload.hive_id, device_id=payload.device_id)
        db.add(hive)
    elif hive.device_id != payload.device_id:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Hive '{payload.hive_id}' is registered to device "
                f"'{hive.device_id}', but this reading came from '{payload.device_id}'"
            ),
        )

    reading = TelemetryReading(
        hive_id=payload.hive_id,
        device_id=payload.device_id,
        internal_temperature=payload.internal_temperature,
        humidity=payload.humidity,
        hive_weight=payload.hive_weight,
        external_temperature=payload.external_temperature,
        temperature_delta=payload.temperature_delta,
        health_score=payload.health_score,
        status=payload.status,
        device_timestamp=payload.device_timestamp,
    )
    db.add(reading)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to store telemetry reading")

    db.refresh(reading)
    return reading


@router.get("/{hive_id}/telemetry/latest", response_model=TelemetryDetail)
def get_latest_telemetry(hive_id: str, db: Session = Depends(get_db)):
    """Most recent sensor reading for a hive — used by admin dashboard live metrics."""
    hive = db.query(Hive).filter(Hive.hive_id == hive_id).first()
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive '{hive_id}' not found")

    reading = (
        db.query(TelemetryReading)
        .filter(TelemetryReading.hive_id == hive_id)
        .order_by(TelemetryReading.id.desc())
        .first()
    )
    if reading is None:
        raise HTTPException(status_code=404, detail=f"No telemetry yet for hive '{hive_id}'")

    return reading


@router.get("/{hive_id}/telemetry", response_model=List[TelemetryDetail])
def get_telemetry_history(
    hive_id: str,
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Historical telemetry for a hive, newest first."""
    hive = db.query(Hive).filter(Hive.hive_id == hive_id).first()
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive '{hive_id}' not found")

    return (
        db.query(TelemetryReading)
        .filter(TelemetryReading.hive_id == hive_id)
        .order_by(TelemetryReading.id.desc())
        .limit(limit)
        .all()
    )


@router.get("/", response_model=List[HiveSummary])
@router.get("", response_model=List[HiveSummary], include_in_schema=False)
def list_hives(db: Session = Depends(get_db)):
    """List all registered smart hives."""
    return db.query(Hive).order_by(Hive.hive_id).all()
