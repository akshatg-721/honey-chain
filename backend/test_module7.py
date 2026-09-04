import io
import os
import cv2
import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app, init_db
from app.database import SessionLocal, engine, Base
from app.models import Hive

client = TestClient(app)

print("==================================================================")
print("=== HoneyChain Module 7 — QR Generation & Verification Suite ===")
print("==================================================================\n")

# 1. Initialize database and ensure HIVE-01 exists
init_db()
db = SessionLocal()
hive = db.execute(text("SELECT hive_id FROM hives WHERE hive_id = 'HIVE-01'")).first()
if not hive:
    db.execute(text("INSERT INTO hives (hive_id, device_id, location, name) VALUES ('HIVE-01', 'ESP32-HIVE-01', 'Coorg Sector 4', 'Apiary Alpha')"))
    db.commit()
db.close()

# -----------------------------------------------------------------------------
# Test 1 & 2: Create a batch linked to HIVE-01 and check qr_code_url
# -----------------------------------------------------------------------------
print("--- TEST 1 & 2: Create batch linked to HIVE-01 & inspect qr_code_url ---")
payload = {
    "beekeeper_name": "Kavitha Menon",
    "farm_location": "Coorg Organic Estates",
    "harvest_date": "2026-09-05",
    "quantity_kg": 42.5,
    "hive_id": "HIVE-01"
}
res_create = client.post("/batches/", json=payload)
assert res_create.status_code == 201, f"Expected 201, got {res_create.status_code}: {res_create.text}"
batch_data = res_create.json()
batch_id = batch_data["batch_id"]
qr_code_url = batch_data.get("qr_code_url")

print(f"[PASS] Batch created: {batch_id}")
print(f"       hive_id: {batch_data.get('hive_id')}")
print(f"       qr_code_url: {qr_code_url}")
assert qr_code_url == f"http://localhost:3000/verify/{batch_id}", f"Unexpected qr_code_url: {qr_code_url}"

# -----------------------------------------------------------------------------
# Test 3: Fetch the QR image directly from GET /batches/{batch_id}/qr
# -----------------------------------------------------------------------------
print(f"\n--- TEST 3: Fetch QR image from GET /batches/{batch_id}/qr ---")
res_qr = client.get(f"/batches/{batch_id}/qr")
assert res_qr.status_code == 200, f"Expected 200, got {res_qr.status_code}"
assert res_qr.headers["content-type"] == "image/png", f"Expected image/png, got {res_qr.headers['content-type']}"

image_bytes = res_qr.content
assert len(image_bytes) > 100, "Image byte buffer too small"
assert image_bytes[:8] == b"\x89PNG\r\n\x1a\n", "Image does not start with standard PNG header"
print(f"[PASS] Successfully retrieved PNG image: {len(image_bytes)} bytes")

# Save to test_qr.png
test_qr_path = "test_qr.png"
with open(test_qr_path, "wb") as f:
    f.write(image_bytes)
print(f"       Saved QR image to {test_qr_path}")

# -----------------------------------------------------------------------------
# Test 4: Decode test_qr.png and confirm it encodes the exact verification URL
# -----------------------------------------------------------------------------
print("\n--- TEST 4: Decode test_qr.png with computer vision ---")
nparr = np.frombuffer(image_bytes, np.uint8)
cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
detector = cv2.QRCodeDetector()
decoded_url, points, _ = detector.detectAndDecode(cv_img)

print(f"[PASS] Decoded QR Content: '{decoded_url}'")
expected_url = f"http://localhost:3000/verify/{batch_id}"
assert decoded_url == expected_url, f"Expected '{expected_url}', got '{decoded_url}'"

# -----------------------------------------------------------------------------
# Test 5: Verify 404 behavior for unknown batch QR
# -----------------------------------------------------------------------------
print("\n--- TEST 5: GET /batches/HCB-NOT-FOUND/qr returns 404 ---")
res_qr_404 = client.get("/batches/HCB-NOT-FOUND/qr")
assert res_qr_404.status_code == 404, f"Expected 404, got {res_qr_404.status_code}"
print(f"[PASS] Unknown batch QR returns 404: {res_qr_404.json()['detail']}")

# -----------------------------------------------------------------------------
# Test 6: Verify public endpoint GET /verify/{batch_id}
# -----------------------------------------------------------------------------
print(f"\n--- TEST 6: Public Consumer Verification GET /verify/{batch_id} ---")
res_verify = client.get(f"/verify/{batch_id}")
assert res_verify.status_code == 200, f"Expected 200, got {res_verify.status_code}"
verify_data = res_verify.json()
print(f"[PASS] Verification payload:")
print(f"       Batch ID:    {verify_data['batch']['batch_id']}")
print(f"       Source Hive: {verify_data['batch']['hive_id']}")
print(f"       Chain Valid: {verify_data['chain_valid']}")
print(f"       Genesis Hash:{verify_data['batch']['checkpoints'][0]['hash']}")
assert verify_data["chain_valid"] is True
assert verify_data["batch"]["hive_id"] == "HIVE-01"

# -----------------------------------------------------------------------------
# Test 7: Verify 404 on GET /verify/HCB-NOT-FOUND
# -----------------------------------------------------------------------------
print("\n--- TEST 7: GET /verify/HCB-NOT-FOUND returns clean 404 ---")
res_verify_404 = client.get("/verify/HCB-NOT-FOUND")
assert res_verify_404.status_code == 404, f"Expected 404, got {res_verify_404.status_code}"
print(f"[PASS] Verify 404 returns clean detail: '{res_verify_404.json()['detail']}'")

# -----------------------------------------------------------------------------
# Test 8: Telemetry ingestion and query still fully intact
# -----------------------------------------------------------------------------
print("\n--- TEST 8: IoT Telemetry ingestion and Admin queries ---")
telemetry_data = {
    "deviceId": "ESP32-HIVE-01",
    "hiveId": "HIVE-01",
    "internalTemperature": 35.2,
    "humidity": 55.4,
    "hiveWeight": 25.1,
    "externalTemperature": 27.8,
    "temperatureDelta": 7.4,
    "healthScore": 98,
    "status": "HEALTHY",
    "deviceTimestamp": 1725514000
}
res_tel = client.post("/api/hives/telemetry", json=telemetry_data)
assert res_tel.status_code == 200
print(f"[PASS] Ingested telemetry reading #{res_tel.json()['reading_id']}")

res_latest = client.get("/api/hives/HIVE-01/telemetry/latest")
assert res_latest.status_code == 200
print(f"[PASS] Latest telemetry confirmed: Temp={res_latest.json()['internal_temperature']}C, Health={res_latest.json()['health_score']}%")

print("\n==================================================================")
print("=== ALL MODULE 7 BACKEND TESTS COMPLETED AND PASSED (100%) ===")
print("==================================================================")
