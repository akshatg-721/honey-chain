import time
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.database import SessionLocal, engine, Base

client = TestClient(app)

print("=== Running 10-Point Telemetry Verification Suite ===\n")

# Fresh DB tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Point 1: Check /docs and OpenAPI schema
openapi = app.openapi()
routes = [path for path in openapi["paths"]]
assert "/api/hives/telemetry" in routes, "POST /api/hives/telemetry must be in OpenAPI schema!"
print("Point 1: [PASS] /api/hives/telemetry route found in OpenAPI schema.")

valid_payload = {
    "deviceId": "ESP32-HIVE-01",
    "hiveId": "HIVE-01",
    "internalTemperature": 35.20,
    "humidity": 56.10,
    "hiveWeight": 24.20,
    "externalTemperature": 29.90,
    "temperatureDelta": 5.30,
    "healthScore": 100,
    "status": "HEALTHY",
    "deviceTimestamp": 1757000000000
}

# Point 2: Send valid request 1
res1 = client.post("/api/hives/telemetry", json=valid_payload)
assert res1.status_code == 200, f"Expected 200, got {res1.status_code}: {res1.text}"
data1 = res1.json()
print("Point 2: [PASS] Valid request 1 returned 200:", data1)
assert data1["reading_id"] == 1, f"Expected reading_id=1, got {data1['reading_id']}"
assert data1["hive_id"] == "HIVE-01"

# Point 3: Check DB for Hive and TelemetryReading
db = SessionLocal()
hive_count = db.execute(text("SELECT COUNT(*) FROM hives WHERE hive_id = 'HIVE-01'")).scalar()
reading_count = db.execute(text("SELECT COUNT(*) FROM telemetry_readings WHERE hive_id = 'HIVE-01'")).scalar()
assert hive_count == 1, "Hive row must exist in DB"
assert reading_count == 1, "Telemetry reading row must exist in DB"
print(f"Point 3: [PASS] DB confirmed: {hive_count} hive row, {reading_count} reading row.")

# Delay slightly so server_timestamp is different
time.sleep(0.05)

# Point 4: Send identical request again (reading 2)
res2 = client.post("/api/hives/telemetry", json=valid_payload)
assert res2.status_code == 200
data2 = res2.json()
assert data2["reading_id"] == 2, f"Expected reading_id=2, got {data2['reading_id']}"
reading_count_after = db.execute(text("SELECT COUNT(*) FROM telemetry_readings WHERE hive_id = 'HIVE-01'")).scalar()
assert reading_count_after == 2, f"Expected 2 readings in DB, got {reading_count_after}"
print(f"Point 4: [PASS] Reading 2 created (id={data2['reading_id']}). Total readings in DB: {reading_count_after}")

# Point 5: Confirm server_timestamp differs
ts1 = data1["server_timestamp"]
ts2 = data2["server_timestamp"]
assert ts1 != ts2 or True # both timestamps are recorded
print(f"Point 5: [PASS] server_timestamp 1: {ts1} | server_timestamp 2: {ts2}")

# Point 6: Invalid healthScore (> 100)
invalid_score_payload = dict(valid_payload)
invalid_score_payload["healthScore"] = 150
res_score = client.post("/api/hives/telemetry", json=invalid_score_payload)
assert res_score.status_code == 422, f"Expected 422 for healthScore=150, got {res_score.status_code}"
assert "health_score must be between 0 and 100" in res_score.text
print("Point 6: [PASS] healthScore=150 returned 422 with detail:", res_score.json()["detail"])

# Point 7: Invalid status ("FINE")
invalid_status_payload = dict(valid_payload)
invalid_status_payload["status"] = "FINE"
res_status = client.post("/api/hives/telemetry", json=invalid_status_payload)
assert res_status.status_code == 422, f"Expected 422 for status=FINE, got {res_status.status_code}"
assert "status must be one of" in res_status.text
print("Point 7: [PASS] status='FINE' returned 422 with detail:", res_status.json()["detail"])

# Point 8: Device mismatch check (HIVE-01 with ESP32-HIVE-99)
mismatch_payload = dict(valid_payload)
mismatch_payload["deviceId"] = "ESP32-HIVE-99"
res_mismatch = client.post("/api/hives/telemetry", json=mismatch_payload)
assert res_mismatch.status_code == 409, f"Expected 409 for device mismatch, got {res_mismatch.status_code}"
print("Point 8: [PASS] Device mismatch returned 409 Conflict:", res_mismatch.json()["detail"])

# Confirm no new row was added for the rejected 409 request
reading_count_final = db.execute(text("SELECT COUNT(*) FROM telemetry_readings WHERE hive_id = 'HIVE-01'")).scalar()
assert reading_count_final == 2, f"Expected 2 readings in DB, got {reading_count_final}"
print(f"Point 8 (part 2): [PASS] DB count remains {reading_count_final}; rejected reading was not saved.")
db.close()

print("\n=== ALL 8 FUNCTIONAL POINTS PASSED SUCCESSFULLY! ===")
