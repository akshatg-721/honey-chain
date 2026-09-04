import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import batches, telemetry, verify


from sqlalchemy import inspect, text

def init_db():
    # Ensure all database tables exist
    Base.metadata.create_all(bind=engine)
    # Check if batches table needs the nullable hive_id column migrated
    inspector = inspect(engine)
    if "batches" in inspector.get_table_names():
        cols = [c["name"] for c in inspector.get_columns("batches")]
        if "hive_id" not in cols:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE batches ADD COLUMN hive_id VARCHAR"))
                conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Honey Chain API",
    description="IoT Telemetry & Cryptographic Honey Traceability Ledger API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(telemetry.router)
app.include_router(batches.router)
app.include_router(verify.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "online", "system": "Honey Chain Backend"}
