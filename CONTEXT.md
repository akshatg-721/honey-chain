# Honey Chain — Complete Project Context

> **For any LLM reading this:** This document is the single source of truth for the entire Honey Chain project. Read it fully before making any code changes. It covers project purpose, architecture, current implementation status, API contract, data models, and the exact "next steps" that have not been built yet.

---

## 1. What Is Honey Chain?

Honey Chain is a **blockchain-based honey traceability and smart beekeeping system** built for the Smart India Hackathon (SIH) internal selection round.

**Core problem it solves:** Honey adulteration and supply-chain opacity. Consumers cannot verify whether the honey they buy is pure, who produced it, or what happened to it between the hive and the shelf.

**How it solves it:** Every honey batch gets registered on a hash-chain ledger. Each stage of the supply chain (harvest → processing → packaging → shipping) is recorded as a cryptographically linked block. Consumers scan a QR code on the jar to see the complete, tamper-evident history of that specific batch.

**Two user roles:**
- **Admin (Beekeeper/Producer):** Registers batches, adds supply-chain checkpoints, downloads QR codes for jars.
- **Consumer (Public):** Scans QR code or enters batch ID to verify authenticity and see the full journey.

---

## 2. Repository Structure

```
honey-chain/                        ← Git root (GitHub: akshatg-721/honey-chain)
├── .gitignore                      ← Covers Python + Node + env files
├── README.md                       ← Minimal placeholder
├── CONTEXT.md                      ← This file
│
├── backend/                        ← FastAPI (Python) — NOT YET IMPLEMENTED
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── __init__.py
│       ├── main.py                 ← TODO: FastAPI entrypoint
│       ├── database.py             ← TODO: SQLAlchemy + Neon/Postgres setup
│       ├── models.py               ← TODO: ORM models (Batch, LedgerBlock)
│       ├── schemas.py              ← TODO: Pydantic schemas
│       ├── blockchain.py           ← TODO: Hash-chain logic
│       ├── qr.py                   ← TODO: QR code generation
│       └── routers/
│           ├── __init__.py
│           ├── batches.py          ← TODO: POST /batches/, POST /batches/{id}/checkpoints
│           └── verify.py           ← TODO: GET /verify/{batch_id}
│
└── frontend/                       ← Next.js 14 (TypeScript, Tailwind) — FULLY BUILT
    ├── app/
    │   ├── layout.tsx              ← Root layout, metadata, Navbar
    │   ├── page.tsx                ← Landing page
    │   ├── globals.css
    │   ├── admin/
    │   │   └── page.tsx            ← Admin dashboard
    │   └── verify/[batchId]/
    │       └── page.tsx            ← Consumer verification page
    ├── components/
    │   ├── Navbar.tsx
    │   ├── BatchCard.tsx
    │   ├── CheckpointTimeline.tsx
    │   ├── Badge.tsx
    │   └── States.tsx              ← LoadingSpinner, ErrorState
    └── lib/
        ├── types.ts                ← Locked API contract (TypeScript interfaces)
        ├── api.ts                  ← Mock + real API layer
        └── utils.ts                ← cn() utility
```

---

## 3. Implementation Status

| Layer | Status | Notes |
|---|---|---|
| Frontend — Landing page | ✅ Complete | Hero, batch lookup, feature section |
| Frontend — Admin dashboard | ✅ Complete | Batch list, create batch modal, add checkpoint modal, QR reveal |
| Frontend — Consumer verify | ✅ Complete | Chain status badge, batch details, checkpoint timeline |
| Frontend — Shared components | ✅ Complete | Navbar, BatchCard, CheckpointTimeline, Badge, States |
| Frontend — API layer (mock) | ✅ Complete | 3 sample batches with realistic data, simulated delay |
| Frontend — API layer (real) | ✅ Wired, not active | Set USE_MOCK=false to activate |
| Backend — All files | ⬜ Skeleton only | All .py files contain TODO comments, no logic written |
| Database | ⬜ Not started | Neon/Postgres, schema not created |
| QR code generation | ⬜ Not started | Will use qrcode[pil] Python library |
| Hash-chain logic | ⬜ Not started | SHA-256 based, described in Section 7 |
| Deployment | ⬜ Not started | Frontend → Vercel, Backend → TBD |

---

## 4. Frontend — Technology Stack

| Item | Value |
|---|---|
| Framework | Next.js 14.2.35, App Router |
| Language | TypeScript (strict mode) |
| Styling | Tailwind CSS 3.4 |
| Icons | lucide-react 1.40.0 |
| Fonts | Geist Sans + Geist Mono (local, from app/fonts/) |
| Design theme | Dark — stone-950 bg, amber-400/500 accent |
| State | React useState + useEffect (no Redux/Zustand/Jotai) |
| Routing | File-system based (Next.js App Router) |
| No extra UI lib | No shadcn, no MUI, no Radix — pure Tailwind + lucide |

### Frontend Routes

| URL | File | Description |
|---|---|---|
| `/` | `app/page.tsx` | Landing page — hero, batch ID lookup form, feature cards |
| `/admin` | `app/admin/page.tsx` | Admin dashboard |
| `/verify/[batchId]` | `app/verify/[batchId]/page.tsx` | Public consumer verification |

### Running Frontend

```bash
cd frontend
npm install
npm run dev          # → http://localhost:3000
```

### Mock Batch IDs (for testing)

- `HCB-2024-001` — Arjun Sharma, Coorg Karnataka, 120kg, all 4 checkpoints complete
- `HCB-2024-002` — Priya Nair, Wayanad Kerala, 85kg, 2 checkpoints (harvested + processed)
- `HCB-2024-003` — Ramesh Patel, Saurashtra Gujarat, 200kg, 1 checkpoint (just harvested)

---

## 5. Locked API Contract

These TypeScript types in `frontend/lib/types.ts` define the **exact JSON shapes** the FastAPI backend must return. **Do not change these types** — the frontend is built against them.

```typescript
export type CheckpointStatus = "harvested" | "processed" | "packaged" | "shipped";

export interface Checkpoint {
  status: CheckpointStatus;
  timestamp: string;        // ISO 8601 UTC, e.g. "2024-08-15T06:30:00Z"
  hash: string;             // hex string, 64 chars (SHA-256)
  previous_hash: string;    // hex string, 64 chars; "000...0" for genesis block
}

export interface Batch {
  batch_id: string;         // format: "HCB-YYYY-NNN", e.g. "HCB-2024-001"
  beekeeper_name: string;
  farm_location: string;
  harvest_date: string;     // ISO date, e.g. "2024-08-15"
  quantity_kg: number;
  created_at: string;       // ISO 8601 UTC timestamp
  qr_code_url: string;      // publicly accessible URL to QR image
  checkpoints: Checkpoint[]; // ordered oldest → newest
}

export interface VerifyResponse {
  batch: Batch;
  chain_valid: boolean;     // true if all hashes chain correctly
}

export interface CreateBatchInput {
  beekeeper_name: string;
  farm_location: string;
  harvest_date: string;     // ISO date
  quantity_kg: number;
}

export interface AddCheckpointInput {
  batch_id: string;
  status: CheckpointStatus;
}
```

---

## 6. API Endpoints (Backend Must Implement)

All endpoints run at `http://localhost:8000` in dev. CORS must allow `http://localhost:3000`.

### `GET /batches/`
Returns all batches.
- **Response:** `Batch[]`

### `GET /batches/{batch_id}`
Returns a single batch by ID.
- **Response:** `Batch`
- **Error:** `404` if not found

### `POST /batches/`
Creates a new batch. Auto-generates `batch_id`, `created_at`, `qr_code_url`.
- **Request body:** `CreateBatchInput`
- **Response:** `Batch` (with empty `checkpoints: []`)

### `POST /batches/{batch_id}/checkpoints`
Adds a supply-chain checkpoint to a batch.
- **Request body:** `{ "status": CheckpointStatus }`
- **Response:** `Batch` (full updated batch with new checkpoint appended)
- The backend must compute `hash` and `previous_hash` using the blockchain logic.

### `GET /verify/{batch_id}`
Public endpoint — returns the batch with a `chain_valid` flag.
- **Response:** `VerifyResponse`
- `chain_valid` is `true` only if every `checkpoint[i].previous_hash === checkpoint[i-1].hash`

---

## 7. Backend — What Needs to Be Built

### `app/database.py` — DB connection

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `app/models.py` — SQLAlchemy ORM models

Two tables needed:

**`batches` table:**
- `id` (int, PK, auto-increment)
- `batch_id` (str, unique, indexed) — e.g. "HCB-2024-001"
- `beekeeper_name` (str)
- `farm_location` (str)
- `harvest_date` (date)
- `quantity_kg` (float)
- `created_at` (datetime, default=utcnow)
- `qr_code_url` (str)

**`ledger_blocks` table:**
- `id` (int, PK, auto-increment)
- `batch_id` (FK → batches.batch_id)
- `status` (str — one of the 4 CheckpointStatus values)
- `timestamp` (datetime, default=utcnow)
- `hash` (str, 64 chars)
- `previous_hash` (str, 64 chars)
- `block_index` (int) — position in the chain for this batch

### `app/schemas.py` — Pydantic schemas

Mirror the TypeScript types exactly:
- `CheckpointOut` → matches `Checkpoint` interface
- `BatchOut` → matches `Batch` interface (includes `checkpoints: list[CheckpointOut]`)
- `BatchCreate` → matches `CreateBatchInput`
- `CheckpointCreate` → `{ status: str }`
- `VerifyOut` → `{ batch: BatchOut, chain_valid: bool }`

### `app/blockchain.py` — Hash-chain logic

```python
import hashlib, json

def compute_hash(block_index: int, batch_id: str, status: str,
                 timestamp: str, previous_hash: str) -> str:
    """
    SHA-256 hash of the block's canonical data.
    Field order must be stable (sort_keys=True).
    """
    data = json.dumps({
        "block_index": block_index,
        "batch_id": batch_id,
        "status": status,
        "timestamp": timestamp,
        "previous_hash": previous_hash,
    }, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()

GENESIS_HASH = "0" * 64

def validate_chain(checkpoints: list) -> bool:
    """
    Returns True if every block's previous_hash matches the prior block's hash.
    Genesis block must have previous_hash = "0" * 64.
    """
    for i, cp in enumerate(checkpoints):
        if i == 0:
            if cp.previous_hash != GENESIS_HASH:
                return False
        else:
            if cp.previous_hash != checkpoints[i - 1].hash:
                return False
    return True
```

### `app/qr.py` — QR code generation

```python
import os

def generate_qr_url(batch_id: str) -> str:
    """
    Returns a publicly accessible QR code image URL encoding the verify page.
    Uses api.qrserver.com — no server-side storage needed for the hackathon.
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verify_url = f"{frontend_url}/verify/{batch_id}"
    return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={verify_url}"
```

### `app/main.py` — FastAPI app

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import batches, verify
from app.database import engine, Base

Base.metadata.create_all(bind=engine)  # auto-create tables on startup

app = FastAPI(title="Honey Chain API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(batches.router, prefix="/batches", tags=["batches"])
app.include_router(verify.router, prefix="/verify", tags=["verify"])
```

### `app/routers/batches.py` — batch_id generation logic

The `batch_id` format is `HCB-YYYY-NNN` where:
- `YYYY` = current year
- `NNN` = zero-padded count of batches created in that year (001, 002, ...)

Query the DB to count existing batches for the current year, increment by 1.

### Running Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # fill in DATABASE_URL
uvicorn app.main:app --reload --port 8000
```

API docs auto-generated at: `http://localhost:8000/docs`

---

## 8. Connecting Frontend to Real Backend

**One change only** in `frontend/lib/api.ts` line 11:

```typescript
// Change:
const USE_MOCK = true;
// To:
const USE_MOCK = false;
```

Also create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Zero component changes required — the API contract is fully locked.

---

## 9. Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | Neon/Postgres connection string | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | App secret (for future JWT auth) | Any 32+ char random string |
| `FRONTEND_URL` | Frontend origin for CORS + QR links | `http://localhost:3000` |

### Frontend (`frontend/.env.local`)

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | FastAPI base URL (no trailing slash) | `http://localhost:8000` |

---

## 10. Design System (Tailwind tokens in use)

| Token | Tailwind class | Usage |
|---|---|---|
| Page background | `bg-stone-950` | Root body |
| Card background | `bg-stone-900` | All cards and panels |
| Card border | `border-stone-800` | Default borders |
| Primary accent | `text-amber-400`, `bg-amber-500` | CTAs, batch IDs, branding |
| Hover | `hover:border-amber-500/40` | Card hover states |
| Verified/success | `text-emerald-400`, `bg-emerald-500/10` | Chain verified badge |
| Failed/danger | `text-red-400`, `bg-red-500/10` | Verification failed |
| Harvested | `text-emerald-400` | Timeline + progress strip |
| Processed | `text-amber-400` | Timeline + progress strip |
| Packaged | `text-sky-400` | Timeline + progress strip |
| Shipped | `text-violet-400` | Timeline + progress strip |

---

## 11. Key Design Decisions & Rationale

1. **Frontend-first, mock-then-real:** Frontend was built completely before the backend, using a `USE_MOCK` flag. The UI is always demo-able without a running server.

2. **Hash-chain in Postgres, not a blockchain network:** The "blockchain" is a linked list of SHA-256 hashes stored in Postgres. No distributed consensus, no smart contracts — the chain integrity is verified server-side.

3. **`batch_id` format `HCB-YYYY-NNN`:** Human-readable, URL-safe, scannable. Auto-incremented by year.

4. **QR via qrserver.com:** No file storage infra needed. The QR encodes the `/verify/{batch_id}` URL. The frontend allows this domain in `next.config.mjs` under `images.remotePatterns`.

5. **No auth on `/admin`:** Intentionally excluded for hackathon demo scope. The admin route is public.

6. **All frontend state in useState:** Simple enough that React local state suffices — no Redux/Zustand needed.

---

## 12. Git History

| Commit | Message | What changed |
|---|---|---|
| `703b126` | Initial commit | Original plain HTML/CSS/JS frontend |
| `5baad00` | Restructure project: FastAPI backend + Next.js frontend skeleton | Deleted old HTML, created all skeleton files |
| `86010b6` | Frontend Base | Full frontend implementation — all pages, components, lib |

**Remote:** `https://github.com/akshatg-721/honey-chain.git` · Branch: `main`

---

## 13. Prioritized Next Steps

1. `backend/app/database.py` — SQLAlchemy engine + session + Base + `get_db()`
2. `backend/app/models.py` — `Batch` and `LedgerBlock` ORM models
3. `backend/app/schemas.py` — Pydantic `BatchOut`, `CheckpointOut`, `VerifyOut`, `BatchCreate`
4. `backend/app/blockchain.py` — `compute_hash()` and `validate_chain()`
5. `backend/app/qr.py` — `generate_qr_url(batch_id)`
6. `backend/app/routers/batches.py` — `GET /batches/`, `GET /batches/{id}`, `POST /batches/`, `POST /batches/{id}/checkpoints`
7. `backend/app/routers/verify.py` — `GET /verify/{batch_id}`
8. `backend/app/main.py` — FastAPI app, CORS, router includes, `create_all()`
9. Flip `USE_MOCK = false` in `frontend/lib/api.ts` and test end-to-end
10. Deploy — frontend to Vercel, backend to Render / Railway / Fly.io
