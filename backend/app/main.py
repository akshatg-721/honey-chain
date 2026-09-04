from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import batches, verify

app = FastAPI(
    title="Honey Chain API",
    description="Core ledger backend for KVIC Honey Mission",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(batches.router)
app.include_router(verify.router)


@app.get("/", tags=["Health"])
def health_check():
    """Simple liveness probe — confirm the API is up."""
    return {"status": "online", "system": "Honey Chain API"}
