export type CheckpointStatus = "harvested" | "processed" | "packaged" | "shipped";

export interface Checkpoint {
  status: CheckpointStatus;
  timestamp: string;
  hash: string;
  previous_hash: string;
}

export interface Batch {
  batch_id: string;
  beekeeper_name: string;
  farm_location: string;
  harvest_date: string;
  quantity_kg: number;
  created_at: string;
  qr_code_url: string;
  hive_id?: string | null;
  checkpoints: Checkpoint[];
}

export interface VerifyResponse {
  batch: Batch;
  chain_valid: boolean;
  hive_id?: string | null;
}

export interface CreateBatchInput {
  beekeeper_name: string;
  farm_location: string;
  harvest_date: string;
  quantity_kg: number;
  hive_id?: string | null;
}

export interface AddCheckpointInput {
  batch_id: string;
  status: CheckpointStatus;
}

export interface Telemetry {
  reading_id: number;
  hive_id: string;
  device_id: string;
  internal_temperature: number;
  humidity: number;
  hive_weight: number;
  external_temperature: number;
  temperature_delta: number;
  health_score: number;
  status: "HEALTHY" | "WARNING" | "CRITICAL";
  device_timestamp: number | null;
  server_timestamp: string;
}

export interface HiveSummary {
  hive_id: string;
  device_id: string;
  name: string | null;
  location: string | null;
}
