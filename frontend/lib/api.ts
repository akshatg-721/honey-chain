/**
 * API layer for Honey Chain.
 *
 * Toggle USE_MOCK to switch between mock data and the real FastAPI backend.
 * When USE_MOCK is false, only this file needs changes — zero component rework.
 */

import type { Batch, VerifyResponse, CreateBatchInput, AddCheckpointInput, Telemetry, HiveSummary } from "./types";

// ─── TOGGLE THIS TO CONNECT TO REAL BACKEND ──────────────────────────────────
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_BASE = API_BASE_URL;
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";
// ─────────────────────────────────────────────────────────────────────────────

/** Simulated network delay (ms) — makes loading states visible during dev/demo */
const delay = (ms = 600) => new Promise((r) => setTimeout(r, ms));

// ─── MOCK DATA ────────────────────────────────────────────────────────────────

const MOCK_BATCHES: Batch[] = [
  {
    batch_id: "HCB-2024-001",
    beekeeper_name: "Arjun Sharma",
    farm_location: "Coorg, Karnataka",
    harvest_date: "2024-08-15",
    quantity_kg: 120,
    created_at: "2024-08-15T06:30:00Z",
    qr_code_url: "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=HCB-2024-001",
    checkpoints: [
      {
        status: "harvested",
        timestamp: "2024-08-15T06:30:00Z",
        hash: "a3f8c2d1e4b5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1",
        previous_hash: "0000000000000000000000000000000000000000000000000000000000000000",
      },
      {
        status: "processed",
        timestamp: "2024-08-18T10:00:00Z",
        hash: "b4c9d3e2f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2",
        previous_hash: "a3f8c2d1e4b5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1",
      },
      {
        status: "packaged",
        timestamp: "2024-08-20T14:00:00Z",
        hash: "c5d0e4f3a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3",
        previous_hash: "b4c9d3e2f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2",
      },
      {
        status: "shipped",
        timestamp: "2024-08-22T08:00:00Z",
        hash: "d6e1f5a4b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4",
        previous_hash: "c5d0e4f3a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3",
      },
    ],
  },
  {
    batch_id: "HCB-2024-002",
    beekeeper_name: "Priya Nair",
    farm_location: "Wayanad, Kerala",
    harvest_date: "2024-09-01",
    quantity_kg: 85,
    created_at: "2024-09-01T07:00:00Z",
    qr_code_url: "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=HCB-2024-002",
    checkpoints: [
      {
        status: "harvested",
        timestamp: "2024-09-01T07:00:00Z",
        hash: "e7f2a6b5c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5",
        previous_hash: "0000000000000000000000000000000000000000000000000000000000000000",
      },
      {
        status: "processed",
        timestamp: "2024-09-04T09:00:00Z",
        hash: "f8a3b7c6d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6",
        previous_hash: "e7f2a6b5c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5",
      },
    ],
  },
  {
    batch_id: "HCB-2024-003",
    beekeeper_name: "Ramesh Patel",
    farm_location: "Saurashtra, Gujarat",
    harvest_date: "2024-09-10",
    quantity_kg: 200,
    created_at: "2024-09-10T05:00:00Z",
    qr_code_url: "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=HCB-2024-003",
    checkpoints: [
      {
        status: "harvested",
        timestamp: "2024-09-10T05:00:00Z",
        hash: "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
        previous_hash: "0000000000000000000000000000000000000000000000000000000000000000",
      },
    ],
  },
];

// ─── MOCK API FUNCTIONS ───────────────────────────────────────────────────────

async function mockGetBatches(): Promise<Batch[]> {
  await delay();
  return structuredClone(MOCK_BATCHES);
}

async function mockGetBatch(batchId: string): Promise<Batch | null> {
  await delay();
  return structuredClone(MOCK_BATCHES.find((b) => b.batch_id === batchId) ?? null);
}

async function mockCreateBatch(input: CreateBatchInput): Promise<Batch> {
  await delay(800);
  const newBatch: Batch = {
    batch_id: `HCB-2024-${String(MOCK_BATCHES.length + 1).padStart(3, "0")}`,
    ...input,
    created_at: new Date().toISOString(),
    qr_code_url: `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=HCB-2024-${String(MOCK_BATCHES.length + 1).padStart(3, "0")}`,
    checkpoints: [],
  };
  MOCK_BATCHES.push(newBatch);
  return structuredClone(newBatch);
}

async function mockAddCheckpoint(input: AddCheckpointInput): Promise<Batch> {
  await delay(600);
  const batch = MOCK_BATCHES.find((b) => b.batch_id === input.batch_id);
  if (!batch) throw new Error(`Batch ${input.batch_id} not found`);
  const prev = batch.checkpoints.at(-1);
  const prevHash = prev?.hash ?? "0".repeat(64);
  const fakeHash = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join("");
  batch.checkpoints.push({
    status: input.status,
    timestamp: new Date().toISOString(),
    hash: fakeHash,
    previous_hash: prevHash,
  });
  return structuredClone(batch);
}

async function mockVerifyBatch(batchId: string): Promise<VerifyResponse> {
  await delay(700);
  const batch = MOCK_BATCHES.find((b) => b.batch_id === batchId);
  if (!batch) throw new Error(`Batch ${batchId} not found`);
  return { batch: structuredClone(batch), chain_valid: true };
}

// ─── REAL API FUNCTIONS ───────────────────────────────────────────────────────

async function realRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const errJson = await res.json();
      if (errJson && typeof errJson.detail === "string") {
        message = errJson.detail;
      }
    } catch {
      try {
        const text = await res.text();
        if (text) message = text;
      } catch {
        // ignore
      }
    }
    const error = new Error(message);
    (error as any).status = res.status;
    throw error;
  }
  return res.json() as Promise<T>;
}

async function realGetBatches(): Promise<Batch[]> {
  return realRequest<Batch[]>("/batches/");
}

async function realGetBatch(batchId: string): Promise<Batch | null> {
  return realRequest<Batch>(`/batches/${batchId}`);
}

async function realCreateBatch(input: CreateBatchInput): Promise<Batch> {
  return realRequest<Batch>("/batches/", { method: "POST", body: JSON.stringify(input) });
}

async function realAddCheckpoint(input: AddCheckpointInput): Promise<Batch> {
  return realRequest<Batch>(`/batches/${input.batch_id}/checkpoints`, {
    method: "POST",
    body: JSON.stringify({ status: input.status }),
  });
}

async function realVerifyBatch(batchId: string): Promise<VerifyResponse> {
  return realRequest<VerifyResponse>(`/verify/${batchId}`);
}

// ─── PUBLIC API ───────────────────────────────────────────────────────────────

export const getBatches = (): Promise<Batch[]> =>
  USE_MOCK ? mockGetBatches() : realGetBatches();

export const getBatch = (batchId: string): Promise<Batch | null> =>
  USE_MOCK ? mockGetBatch(batchId) : realGetBatch(batchId);

export const createBatch = (input: CreateBatchInput): Promise<Batch> =>
  USE_MOCK ? mockCreateBatch(input) : realCreateBatch(input);

export const addCheckpoint = (input: AddCheckpointInput): Promise<Batch> =>
  USE_MOCK ? mockAddCheckpoint(input) : realAddCheckpoint(input);

export const verifyBatch = (batchId: string): Promise<VerifyResponse> =>
  USE_MOCK ? mockVerifyBatch(batchId) : realVerifyBatch(batchId);

// ─── IOT TELEMETRY API (LIVE BACKEND) ─────────────────────────────────────────

export async function getLatestTelemetry(hiveId: string): Promise<Telemetry> {
  const res = await fetch(`${API_BASE}/api/hives/${hiveId}/telemetry/latest`);
  if (!res.ok) {
    throw new Error(`Failed to fetch latest telemetry (${res.status})`);
  }
  return res.json();
}

export async function getTelemetryHistory(hiveId: string, limit = 20): Promise<Telemetry[]> {
  const res = await fetch(`${API_BASE}/api/hives/${hiveId}/telemetry?limit=${limit}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch telemetry history (${res.status})`);
  }
  return res.json();
}

export async function getHives(): Promise<HiveSummary[]> {
  const res = await fetch(`${API_BASE}/api/hives/`);
  if (!res.ok) throw new Error(`Failed to fetch hives (${res.status})`);
  return res.json();
}
