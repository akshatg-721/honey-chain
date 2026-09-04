import type { CheckpointStatus } from "@/lib/types";
import { Leaf, FlaskConical, Package, Truck } from "lucide-react";

const STATUS_CONFIG: Record<
  CheckpointStatus,
  { label: string; icon: React.ReactNode; color: string; bg: string; border: string }
> = {
  harvested: {
    label: "Harvested",
    icon: <Leaf className="h-4 w-4" />,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
  },
  processed: {
    label: "Processed",
    icon: <FlaskConical className="h-4 w-4" />,
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/30",
  },
  packaged: {
    label: "Packaged",
    icon: <Package className="h-4 w-4" />,
    color: "text-sky-400",
    bg: "bg-sky-500/10",
    border: "border-sky-500/30",
  },
  shipped: {
    label: "Shipped",
    icon: <Truck className="h-4 w-4" />,
    color: "text-violet-400",
    bg: "bg-violet-500/10",
    border: "border-violet-500/30",
  },
};

interface CheckpointTimelineProps {
  checkpoints: {
    status: CheckpointStatus;
    timestamp: string;
    hash: string;
    previous_hash: string;
  }[];
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function CheckpointTimeline({ checkpoints }: CheckpointTimelineProps) {
  if (checkpoints.length === 0) {
    return (
      <p className="text-stone-500 text-sm italic py-4">No checkpoints recorded yet.</p>
    );
  }

  return (
    <ol className="relative space-y-0">
      {checkpoints.map((cp, idx) => {
        const cfg = STATUS_CONFIG[cp.status];
        const isLast = idx === checkpoints.length - 1;
        return (
          <li key={idx} className="relative flex gap-4">
            {/* Connector line */}
            {!isLast && (
              <div className="absolute left-5 top-10 bottom-0 w-px bg-stone-700" />
            )}

            {/* Icon dot */}
            <div
              className={`relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border ${cfg.border} ${cfg.bg} ${cfg.color}`}
            >
              {cfg.icon}
            </div>

            {/* Content */}
            <div className={`pb-8 ${isLast ? "pb-0" : ""}`}>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className={`text-sm font-semibold ${cfg.color}`}>{cfg.label}</span>
                <span className="text-xs text-stone-500">{formatDate(cp.timestamp)}</span>
              </div>
              <div className="rounded-lg border border-stone-800 bg-stone-900/50 px-3 py-2 space-y-1">
                <div className="flex gap-2 items-start">
                  <span className="text-xs font-mono text-stone-500 shrink-0 pt-0.5">HASH</span>
                  <span className="text-xs font-mono text-stone-400 break-all">{cp.hash}</span>
                </div>
                <div className="flex gap-2 items-start">
                  <span className="text-xs font-mono text-stone-500 shrink-0 pt-0.5">PREV</span>
                  <span className="text-xs font-mono text-stone-600 break-all">{cp.previous_hash}</span>
                </div>
              </div>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
