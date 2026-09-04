import type { Batch } from "@/lib/types";
import { MapPin, Scale, Calendar, ChevronRight } from "lucide-react";
import Link from "next/link";

const CHECKPOINT_COLORS: Record<string, string> = {
  harvested: "bg-emerald-500",
  processed: "bg-amber-500",
  packaged: "bg-sky-500",
  shipped: "bg-violet-500",
};

interface BatchCardProps {
  batch: Batch;
  onAddCheckpoint?: (batchId: string) => void;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-IN", { dateStyle: "medium" });
}

export default function BatchCard({ batch, onAddCheckpoint }: BatchCardProps) {
  const latest = batch.checkpoints.at(-1);

  return (
    <div className="group rounded-xl border border-stone-800 bg-stone-900 hover:border-amber-500/40 hover:bg-stone-800/80 transition-all duration-200">
      <div className="p-5">
        {/* Header row */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-xs text-amber-400 font-semibold tracking-wider">
                {batch.batch_id}
              </span>
              {latest && (
                <span
                  className={`inline-block h-2 w-2 rounded-full ${CHECKPOINT_COLORS[latest.status] ?? "bg-stone-500"}`}
                  title={latest.status}
                />
              )}
            </div>
            <h3 className="text-base font-semibold text-white">{batch.beekeeper_name}</h3>
          </div>
          <Link
            href={`/verify/${batch.batch_id}`}
            className="text-stone-500 hover:text-amber-400 transition-colors"
            title="View verification page"
          >
            <ChevronRight className="h-5 w-5" />
          </Link>
        </div>

        {/* Meta row */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-1 text-stone-500">
              <MapPin className="h-3 w-3" />
              <span className="text-xs">Location</span>
            </div>
            <span className="text-xs font-medium text-stone-300 truncate">{batch.farm_location}</span>
          </div>
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-1 text-stone-500">
              <Calendar className="h-3 w-3" />
              <span className="text-xs">Harvested</span>
            </div>
            <span className="text-xs font-medium text-stone-300">{formatDate(batch.harvest_date)}</span>
          </div>
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-1 text-stone-500">
              <Scale className="h-3 w-3" />
              <span className="text-xs">Quantity</span>
            </div>
            <span className="text-xs font-medium text-stone-300">{batch.quantity_kg} kg</span>
          </div>
        </div>

        {/* Checkpoint progress strip */}
        <div className="flex gap-1 mb-4">
          {(["harvested", "processed", "packaged", "shipped"] as const).map((s) => {
            const done = batch.checkpoints.some((c) => c.status === s);
            return (
              <div
                key={s}
                className={`h-1.5 flex-1 rounded-full transition-colors ${done ? CHECKPOINT_COLORS[s] : "bg-stone-700"}`}
                title={s}
              />
            );
          })}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Link
            href={`/verify/${batch.batch_id}`}
            className="flex-1 rounded-lg border border-stone-700 px-3 py-1.5 text-center text-xs font-medium text-stone-400 hover:border-amber-500/50 hover:text-amber-400 transition-colors"
          >
            View Details
          </Link>
          {onAddCheckpoint && (
            <button
              onClick={() => onAddCheckpoint(batch.batch_id)}
              className="flex-1 rounded-lg bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 text-xs font-semibold text-amber-400 hover:bg-amber-500/20 transition-colors"
            >
              + Checkpoint
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
