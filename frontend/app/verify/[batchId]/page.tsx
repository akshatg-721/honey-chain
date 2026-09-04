"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import type { VerifyResponse } from "@/lib/types";
import { verifyBatch } from "@/lib/api";
import CheckpointTimeline from "@/components/CheckpointTimeline";
import Badge from "@/components/Badge";
import { LoadingSpinner, ErrorState } from "@/components/States";
import { MapPin, Scale, Calendar, User, Hash, ArrowLeft, Radio } from "lucide-react";
import Link from "next/link";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-IN", { dateStyle: "long" });
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}

export default function VerifyPage() {
  const { batchId } = useParams<{ batchId: string }>();
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await verifyBatch(batchId);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not verify batch.");
    } finally {
      setLoading(false);
    }
  }, [batchId]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      {/* Back link */}
      <Link
        href="/"
        className="mb-8 inline-flex items-center gap-1.5 text-sm text-stone-500 hover:text-amber-400 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </Link>

      {loading ? (
        <LoadingSpinner message="Verifying batch on-chain…" />
      ) : error ? (
        <ErrorState
          title="Batch not found"
          message={error}
          onRetry={load}
        />
      ) : result ? (
        <div className="space-y-8">
          {/* ── Verification Status Card ──────────────────────────────────────── */}
          <div
            className={`rounded-2xl border p-6 text-center ${
              result.chain_valid
                ? "border-emerald-500/30 bg-emerald-500/5"
                : "border-red-500/30 bg-red-500/5"
            }`}
          >
            <div className="mb-4 flex justify-center">
              <span className="text-5xl">{result.chain_valid ? "✅" : "❌"}</span>
            </div>
            <h1 className="mb-3 text-xl font-bold text-white sm:text-2xl">
              {result.chain_valid
                ? "This batch is verified authentic."
                : "Verification failed — chain integrity broken."}
            </h1>
            <Badge
              variant={result.chain_valid ? "verified" : "unverified"}
              large
            />
            <p className="mt-3 text-xs text-stone-400 font-mono tracking-wide">
              {result.chain_valid ? "Blockchain-Verified Provenance Record" : "Integrity Verification Failed"}
            </p>
            <p className="mt-1 text-xs text-stone-500">
              {result.chain_valid
                ? "The recorded harvest, processing, and shipping history is cryptographically tamper-evident."
                : "One or more ledger blocks do not match their cryptographic hashes."}
            </p>
            {!result.chain_valid && (
              <p className="mt-4 text-sm text-red-400">
                One or more records in this batch&apos;s ledger have been tampered with. Do not
                purchase this product.
              </p>
            )}
          </div>

          {/* ── Batch Identity ────────────────────────────────────────────────── */}
          <div className="rounded-2xl border border-stone-800 bg-stone-900 p-6">
            <div className="mb-5 flex items-start justify-between gap-4 flex-wrap">
              <div>
                <p className="text-xs text-stone-500 mb-1 font-mono tracking-wider uppercase">Batch ID</p>
                <p className="text-lg font-bold text-amber-400 font-mono">
                  {result.batch.batch_id}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-stone-500 mb-1">Registered on</p>
                <p className="text-xs text-stone-300">{formatDateTime(result.batch.created_at)}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                {
                  icon: <User className="h-4 w-4" />,
                  label: "Beekeeper",
                  value: result.batch.beekeeper_name,
                },
                {
                  icon: <MapPin className="h-4 w-4" />,
                  label: "Farm Location",
                  value: result.batch.farm_location,
                },
                {
                  icon: <Calendar className="h-4 w-4" />,
                  label: "Harvest Date",
                  value: formatDate(result.batch.harvest_date),
                },
                {
                  icon: <Scale className="h-4 w-4" />,
                  label: "Quantity",
                  value: `${result.batch.quantity_kg} kg`,
                },
              ].map((item) => (
                <div key={item.label} className="rounded-xl bg-stone-800/50 p-3">
                  <div className="flex items-center gap-1.5 text-stone-500 mb-1">
                    {item.icon}
                    <span className="text-xs">{item.label}</span>
                  </div>
                  <p className="text-sm font-semibold text-white">{item.value}</p>
                </div>
              ))}
            </div>

            {/* Source Hive Link */}
            {result.batch.hive_id && (
              <div className="mt-5 flex items-center justify-between rounded-xl border border-amber-500/20 bg-amber-500/5 px-4 py-3 flex-wrap gap-2">
                <div className="flex items-center gap-2.5">
                  <Radio className="h-4 w-4 text-amber-400 shrink-0" />
                  <div>
                    <p className="text-xs font-semibold text-white">Live Hive Monitoring: {result.batch.hive_id}</p>
                    <p className="text-[11px] text-stone-400">
                      Real-time environmental data from the source hive continuously recorded on-site.
                    </p>
                  </div>
                </div>
                <span className="rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/30">
                  IoT Monitored
                </span>
              </div>
            )}
          </div>

          {/* ── Supply Chain Timeline ─────────────────────────────────────────── */}
          <div className="rounded-2xl border border-stone-800 bg-stone-900 p-6">
            <div className="mb-6 flex items-center gap-2">
              <Hash className="h-4 w-4 text-stone-500" />
              <h2 className="text-base font-bold text-white">Supply Chain Ledger</h2>
              <span className="ml-auto rounded-full bg-stone-800 px-2.5 py-0.5 text-xs font-mono text-stone-400">
                {result.batch.checkpoints.length} block{result.batch.checkpoints.length !== 1 ? "s" : ""}
              </span>
            </div>

            <CheckpointTimeline checkpoints={result.batch.checkpoints} />
          </div>

          {/* ── What this means ───────────────────────────────────────────────── */}
          <div className="rounded-xl border border-stone-800 bg-stone-900/50 px-5 py-4 space-y-2">
            <p className="text-xs text-stone-400 leading-relaxed">
              <span className="font-semibold text-amber-400">Blockchain-Verified Provenance Record: </span>
              The recorded harvest, processing, and shipping history is cryptographically tamper-evident. Each supply-chain checkpoint seals a deterministic SHA-256 hash of its data and predecessor hash into an immutable ledger.
            </p>
            {result.batch.hive_id && (
              <p className="text-xs text-stone-400 leading-relaxed border-t border-stone-800/80 pt-2">
                <span className="font-semibold text-stone-300">Live Hive Monitoring: </span>
                Real-time environmental data from the source hive continuously recorded on-site.
              </p>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
