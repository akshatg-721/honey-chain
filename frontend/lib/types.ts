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
  checkpoints: Checkpoint[];
}

export interface VerifyResponse {
  batch: Batch;
  chain_valid: boolean;
}

export interface CreateBatchInput {
  beekeeper_name: string;
  farm_location: string;
  harvest_date: string;
  quantity_kg: number;
}

export interface AddCheckpointInput {
  batch_id: string;
  status: CheckpointStatus;
}
