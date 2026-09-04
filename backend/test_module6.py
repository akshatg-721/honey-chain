import json
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app, init_db
from app.database import SessionLocal, engine, Base

client = TestClient(app)

print("================================================================")
print("=== HoneyChain Module 6 — 10-Point Verification Test Suite ===")
print("================================================================\n")

# Ensure tables are ready and migrated
init_db()

# Ensure HIVE-01 exists in database
db = SessionLocal()
hive = db.execute(text("SELECT hive_id FROM hives WHERE hive_id = 'HIVE-01'")).first()
if not hive:
    db.execute(text("INSERT INTO hives (hive_id, device_id, location, name) VALUES ('HIVE-01', 'ESP32-HIVE-01', 'Coorg Sector 4', 'Apiary Alpha')"))
    db.commit()
db.close()

# -----------------------------------------------------------------------------
# Test 1: GET /api/hives/ - Admin Hive List
# -----------------------------------------------------------------------------
print("--- TEST 1: GET /api/hives/ ---")
r1 = client.get("/api/hives/")
assert r1.status_code == 200, f"Expected 200, got {r1.status_code}: {r1.text}"
hives = r1.json()
print("Test 1: [PASS] GET /api/hives/ returned hives:", [h["hive_id"] for h in hives])
assert any(h["hive_id"] == "HIVE-01" for h in hives)

# -----------------------------------------------------------------------------
# Test 2: POST /batches/ with nonexistent hive_id (HIVE-99) -> expect 404
# -----------------------------------------------------------------------------
print("\n--- TEST 2: POST /batches/ with invalid hive_id (HIVE-99) ---")
batch_count_before = SessionLocal().execute(text("SELECT COUNT(*) FROM batches")).scalar()
r_invalid = client.post("/batches/", json={
    "beekeeper_name": "Ramesh Kumar",
    "farm_location": "Rohtak",
    "harvest_date": "2026-09-01",
    "quantity_kg": 50,
    "hive_id": "HIVE-99"
})
assert r_invalid.status_code == 404, f"Expected 404 for HIVE-99, got {r_invalid.status_code}"
print("Test 2: [PASS] Nonexistent hive rejected with 404:", r_invalid.json()["detail"])

# -----------------------------------------------------------------------------
# Test 3: Direct DB check - Confirm NO row was created for rejected batch
# -----------------------------------------------------------------------------
print("\n--- TEST 3: DB Verification for Rejected Batch ---")
batch_count_after = SessionLocal().execute(text("SELECT COUNT(*) FROM batches")).scalar()
assert batch_count_before == batch_count_after, "No batch row should be created for rejected hive"
print(f"Test 3: [PASS] Batch table count remained exactly {batch_count_after} (0 rows leaked)")

# -----------------------------------------------------------------------------
# Test 4: POST /batches/ without hive_id (Old batch contract simulation)
# -----------------------------------------------------------------------------
print("\n--- TEST 4: POST /batches/ without hive_id (Old batch format) ---")
r_old = client.post("/batches/", json={
    "beekeeper_name": "Arjun Sharma",
    "farm_location": "Coorg, Karnataka",
    "harvest_date": "2026-08-15",
    "quantity_kg": 120,
    "hive_id": None
})
assert r_old.status_code == 201, f"Expected 201, got {r_old.status_code}"
old_batch = r_old.json()
old_batch_id = old_batch["batch_id"]
print(f"Test 4: [PASS] Created batch WITHOUT hive_id: {old_batch_id}")
print(f"         hive_id: {old_batch.get('hive_id')}")
assert old_batch.get("hive_id") is None

# -----------------------------------------------------------------------------
# Test 5: POST /batches/ WITH valid hive_id (New batch contract)
# -----------------------------------------------------------------------------
print("\n--- TEST 5: POST /batches/ WITH valid hive_id (HIVE-01) ---")
r_new = client.post("/batches/", json={
    "beekeeper_name": "Priya Nair",
    "farm_location": "Wayanad, Kerala",
    "harvest_date": "2026-09-02",
    "quantity_kg": 85,
    "hive_id": "HIVE-01"
})
assert r_new.status_code == 201, f"Expected 201, got {r_new.status_code}"
new_batch = r_new.json()
new_batch_id = new_batch["batch_id"]
print(f"Test 5: [PASS] Created batch WITH hive_id: {new_batch_id}")
print(f"         hive_id: {new_batch.get('hive_id')}")
assert new_batch.get("hive_id") == "HIVE-01"

# -----------------------------------------------------------------------------
# Test 6: Append Checkpoints to both chains
# -----------------------------------------------------------------------------
print("\n--- TEST 6: Appending Checkpoint Blocks to Both Batches ---")
for s in ["processed", "packaged", "shipped"]:
    cp_old = client.post(f"/batches/{old_batch_id}/checkpoints", json={"status": s})
    assert cp_old.status_code == 200
    cp_new = client.post(f"/batches/{new_batch_id}/checkpoints", json={"status": s})
    assert cp_new.status_code == 200
print(f"Test 6: [PASS] Successfully appended processed -> packaged -> shipped to both {old_batch_id} and {new_batch_id}")

# -----------------------------------------------------------------------------
# Test 7: Verify Old Batch (without hive_id) - Hash Contract Preserved
# -----------------------------------------------------------------------------
print("\n--- TEST 7: Verification of Old Batch (hive_id: None) ---")
r_verify_old = client.get(f"/verify/{old_batch_id}")
assert r_verify_old.status_code == 200
v_old = r_verify_old.json()
print(f"Test 7: [PASS] Verification for {old_batch_id}:")
print(f"  Batch ID:          {v_old['batch']['batch_id']}")
print(f"  hive_id:           {v_old['hive_id']}")
print(f"  chain_valid:       {v_old['chain_valid']}")
print(f"  Checkpoints count: {len(v_old['batch']['checkpoints'])}")
print(f"  Genesis Hash:      {v_old['batch']['checkpoints'][0]['hash']}")
print(f"  Terminal Hash:     {v_old['batch']['checkpoints'][-1]['hash']}")
assert v_old["chain_valid"] is True
assert v_old["hive_id"] is None

# -----------------------------------------------------------------------------
# Test 8: Verify New Batch (with hive_id: HIVE-01) - Hash Contract Clean
# -----------------------------------------------------------------------------
print("\n--- TEST 8: Verification of New Batch (hive_id: HIVE-01) ---")
r_verify_new = client.get(f"/verify/{new_batch_id}")
assert r_verify_new.status_code == 200
v_new = r_verify_new.json()
print(f"Test 8: [PASS] Verification for {new_batch_id}:")
print(f"  Batch ID:          {v_new['batch']['batch_id']}")
print(f"  hive_id:           {v_new['hive_id']}")
print(f"  chain_valid:       {v_new['chain_valid']}")
print(f"  Checkpoints count: {len(v_new['batch']['checkpoints'])}")
print(f"  Genesis Hash:      {v_new['batch']['checkpoints'][0]['hash']}")
print(f"  Terminal Hash:     {v_new['batch']['checkpoints'][-1]['hash']}")
assert v_new["chain_valid"] is True
assert v_new["hive_id"] == "HIVE-01"

# -----------------------------------------------------------------------------
# Test 9: ESP32 Telemetry Ingestion Untouched
# -----------------------------------------------------------------------------
print("\n--- TEST 9: ESP32 Telemetry Ingestion (POST /api/hives/telemetry) ---")
esp32_payload = {
    "deviceId": "ESP32-HIVE-01",
    "hiveId": "HIVE-01",
    "internalTemperature": 35.1,
    "humidity": 58.2,
    "hiveWeight": 24.6,
    "externalTemperature": 28.3,
    "temperatureDelta": 6.8,
    "healthScore": 96,
    "status": "HEALTHY",
    "deviceTimestamp": 1725510000
}
r_telemetry = client.post("/api/hives/telemetry", json=esp32_payload)
assert r_telemetry.status_code == 200, f"Expected 200, got {r_telemetry.status_code}: {r_telemetry.text}"
t_resp = r_telemetry.json()
print(f"Test 9: [PASS] Telemetry ingested successfully: reading_id={t_resp['reading_id']}, hive_id={t_resp['hive_id']}")

# -----------------------------------------------------------------------------
# Test 10: Admin Telemetry Queries Untouched
# -----------------------------------------------------------------------------
print("\n--- TEST 10: Latest Telemetry & History Queries ---")
r_latest = client.get("/api/hives/HIVE-01/telemetry/latest")
assert r_latest.status_code == 200
latest_data = r_latest.json()
print(f"Test 10: [PASS] Latest telemetry: Temp={latest_data['internal_temperature']}C, Weight={latest_data['hive_weight']}kg, Health={latest_data['health_score']}%")

r_hist = client.get("/api/hives/HIVE-01/telemetry?limit=5")
assert r_hist.status_code == 200
hist_data = r_hist.json()
print(f"         [PASS] History retrieved {len(hist_data)} readings successfully")

print("\n================================================================")
print("=== ALL 10 MODULE 6 TESTS COMPLETED AND PASSED WITH 100% SUCCESS ===")
print("================================================================")
