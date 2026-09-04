# 🍯 KVIC Honey Chain
### Enterprise Blockchain-Verified Traceability & IoT Telemetry Platform

---

## 1. Executive Summary
The **KVIC Honey Chain** is a state-of-the-art, enterprise-grade traceability platform designed to revolutionize the honey supply chain by bringing absolute transparency to consumers. By seamlessly integrating a cryptographically verifiable blockchain ledger with real-time IoT edge telemetry, the platform guarantees that every jar of honey can be traced back to its precise origin, under verified environmental conditions.

This platform bridges the gap between the physical apiary and the digital ledger, ensuring authenticity, combating counterfeiting, and building unparalleled consumer trust.

---

## 2. Core Value Proposition

### 🛡️ Consumer Trust & Transparency
*   **Scan-to-Verify:** Consumers simply scan a unique QR code on their jar to view the complete, immutable journey of their honey, from the specific apiary to the store shelf.
*   **Proven Origin:** Eliminates doubt regarding sourcing by cryptographically proving exactly which hive produced the batch.

### 📡 Real-Time Quality Assurance (IoT)
*   **Live Environmental Monitoring:** Smart hives equipped with ESP32 edge devices actively monitor internal temperature, ambient conditions, humidity, and hive weight.
*   **Dynamic Health Scoring:** Telemetry data is instantly aggregated into a real-time health score (🟢 Healthy, 🟡 Warning, 🔴 Critical), allowing beekeepers and administrators to proactively manage apiary health.

### 🔒 Anti-Fraud Security
*   **Immutable Checkpoints:** A sealed cryptographic core utilizing SHA-256 hash chaining guarantees that once a supply chain checkpoint is recorded, it is permanently locked.
*   **Zero-Trust Validation:** Any attempt to manipulate historical data instantly breaks the hash chain and flags the batch as invalid.

---

## 3. Platform Architecture

The architecture is highly decoupled, ensuring security, scalability, and resilience across three distinct layers:

### Layer 1: IoT Telemetry Edge (Hardware)
*   **Microcontrollers:** ESP32 devices deployed directly in the field.
*   **Sensor Suite:** High-precision monitoring of internal/external temperature, humidity, and hive weight.
*   **Security Protocol:** Features zero-touch auto-registration locked to unique hardware MAC/Device IDs. Employs strict anti-spoofing measures (HTTP 409 Conflict rejection) to ensure data integrity directly at the source.

### Layer 2: Cryptographic Ledger (Cloud Backend)
*   **Core Stack:** High-performance FastAPI (Python), SQLAlchemy ORM, and PostgreSQL (optimized via Neon Serverless Postgres).
*   **Ledger Mechanics:** Supply chain lifecycle events (`Harvested` → `Processed` → `Packaged` → `Shipped`) are appended as chained blocks. Every block contains the hash of the preceding block.
*   **Decoupled Engine:** The `blockchain.py` hashing engine operates entirely independent of the application logic, providing pure cryptographic validation without side effects.

### Layer 3: Command Center & Consumer Portal (Frontend)
*   **Core Stack:** Next.js (React), TypeScript, Tailwind CSS, Lucide Icons.
*   **Admin Dashboard:** A centralized, real-time command center that polls live telemetry data, allowing administrators to oversee fleet health and register new honey batches.
*   **Consumer Verification Portal:** A mobile-optimized verification page dynamically generated for each batch, accessed via Base64 PNG QR codes.

---

## 4. Technical Deployment & Setup

The system is designed for modern cloud environments, targeting Vercel (Frontend) and Render/Railway (Backend).

### 4.1. Backend Configuration (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Variables (`backend/.env`):**
```ini
DATABASE_URL=postgresql://user:password@host/dbname
SECRET_KEY=your-secure-secret
FRONTEND_URL=http://localhost:3000
```

**Launch Server:**
```bash
uvicorn app.main:app --reload --port 8000
```
*(Interactive API documentation available at `http://localhost:8000/docs`)*

### 4.2. Frontend Configuration (Next.js)

```bash
cd frontend
npm install
```

**Environment Variables (`frontend/.env.local`):**
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Launch Application:**
```bash
npm run dev
```

---

## 5. Security & Integrity Invariants

To maintain the absolute integrity of the platform, the following architectural invariants are strictly enforced:
1.  **Decoupled Cryptography:** The hashing engine operates completely outside the database ORM to prevent tampering from within the application layer.
2.  **Strict Data Bounds:** IoT telemetry undergoes rigid bounds checking at the API gateway to prevent malicious data injection.
3.  **Graceful Degradation:** The Traceability Ledger and the IoT Telemetry system operate asynchronously. If an IoT sensor goes offline, the supply chain ledger continues to function unimpeded, ensuring zero downtime for supply chain operations.

---

*Developed for the KVIC Honey Mission to revolutionize supply chain transparency and establish the gold standard for agricultural traceability.*