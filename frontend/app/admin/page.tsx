"use client";

import { useEffect, useState, useCallback } from "react";
import type { Batch, CreateBatchInput, CheckpointStatus } from "@/lib/types";
import { getBatches, createBatch, addCheckpoint } from "@/lib/api";
import BatchCard from "@/components/BatchCard";
import { LoadingSpinner, ErrorState } from "@/components/States";
import { Plus, X, QrCode } from "lucide-react";
import Image from "next/image";

type ModalState =
  | { type: "none" }
  | { type: "new-batch" }
  | { type: "add-checkpoint"; batchId: string }
  | { type: "show-qr"; batch: Batch };

const CHECKPOINT_STATUSES: CheckpointStatus[] = ["harvested", "processed", "packaged", "shipped"];

export default function AdminPage() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modal, setModal] = useState<ModalState>({ type: "none" });
  const [submitting, setSubmitting] = useState(false);

  // ── New batch form state ──
  const [form, setForm] = useState<CreateBatchInput>({
    beekeeper_name: "",
    farm_location: "",
    harvest_date: "",
    quantity_kg: 0,
  });

  // ── Add checkpoint form state ──
  const [cpStatus, setCpStatus] = useState<CheckpointStatus>("harvested");

  const loadBatches = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getBatches();
      setBatches(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load batches.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBatches();
  }, [loadBatches]);

  async function handleCreateBatch(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const newBatch = await createBatch(form);
      setBatches((prev) => [...prev, newBatch]);
      setModal({ type: "show-qr", batch: newBatch });
      setForm({ beekeeper_name: "", farm_location: "", harvest_date: "", quantity_kg: 0 });
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to create batch.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAddCheckpoint(e: React.FormEvent) {
    e.preventDefault();
    if (modal.type !== "add-checkpoint") return;
    setSubmitting(true);
    try {
      const updated = await addCheckpoint({ batch_id: modal.batchId, status: cpStatus });
      setBatches((prev) => prev.map((b) => (b.batch_id === updated.batch_id ? updated : b)));
      setModal({ type: "none" });
    } catch (e) {
      alert(e instanceof Error ? e.message : "Failed to add checkpoint.");
    } finally {
      setSubmitting(false);
    }
  }

  function closeModal() {
    setModal({ type: "none" });
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      {/* Page header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white sm:text-3xl">Admin Dashboard</h1>
          <p className="mt-1 text-sm text-stone-400">
            Manage honey batches and supply-chain checkpoints.
          </p>
        </div>
        <button
          onClick={() => setModal({ type: "new-batch" })}
          className="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-5 py-2.5 text-sm font-semibold text-stone-950 hover:bg-amber-400 active:scale-95 transition-all"
        >
          <Plus className="h-4 w-4" />
          New Batch
        </button>
      </div>

      {/* Batch grid */}
      {loading ? (
        <LoadingSpinner message="Loading batches…" />
      ) : error ? (
        <ErrorState title="Failed to load batches" message={error} onRetry={loadBatches} />
      ) : batches.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
          <span className="text-5xl">🍯</span>
          <p className="text-stone-400 text-sm">No batches yet. Create your first batch above.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {batches.map((batch) => (
            <BatchCard
              key={batch.batch_id}
              batch={batch}
              onAddCheckpoint={(id) => {
                setCpStatus("harvested");
                setModal({ type: "add-checkpoint", batchId: id });
              }}
            />
          ))}
        </div>
      )}

      {/* ── MODAL BACKDROP ──────────────────────────────────────────────────── */}
      {modal.type !== "none" && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
          onClick={closeModal}
        >
          <div
            className="relative w-full max-w-md rounded-2xl border border-stone-700 bg-stone-900 p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={closeModal}
              className="absolute right-4 top-4 text-stone-500 hover:text-stone-200 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>

            {/* ── New Batch Form ── */}
            {modal.type === "new-batch" && (
              <>
                <h2 className="mb-5 text-lg font-bold text-white">Register New Batch</h2>
                <form onSubmit={handleCreateBatch} className="space-y-4">
                  {[
                    {
                      id: "beekeeper_name",
                      label: "Beekeeper Name",
                      type: "text",
                      placeholder: "e.g. Arjun Sharma",
                    },
                    {
                      id: "farm_location",
                      label: "Farm Location",
                      type: "text",
                      placeholder: "e.g. Coorg, Karnataka",
                    },
                    {
                      id: "harvest_date",
                      label: "Harvest Date",
                      type: "date",
                      placeholder: "",
                    },
                  ].map((field) => (
                    <div key={field.id}>
                      <label className="mb-1.5 block text-xs font-medium text-stone-400">
                        {field.label}
                      </label>
                      <input
                        type={field.type}
                        required
                        placeholder={field.placeholder}
                        value={form[field.id as keyof CreateBatchInput] as string}
                        onChange={(e) =>
                          setForm((prev) => ({ ...prev, [field.id]: e.target.value }))
                        }
                        className="w-full rounded-lg border border-stone-700 bg-stone-800 px-3 py-2.5 text-sm text-white placeholder-stone-600 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition"
                      />
                    </div>
                  ))}
                  <div>
                    <label className="mb-1.5 block text-xs font-medium text-stone-400">
                      Quantity (kg)
                    </label>
                    <input
                      type="number"
                      required
                      min={1}
                      placeholder="e.g. 120"
                      value={form.quantity_kg || ""}
                      onChange={(e) =>
                        setForm((prev) => ({ ...prev, quantity_kg: Number(e.target.value) }))
                      }
                      className="w-full rounded-lg border border-stone-700 bg-stone-800 px-3 py-2.5 text-sm text-white placeholder-stone-600 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full rounded-xl bg-amber-500 py-2.5 text-sm font-semibold text-stone-950 hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {submitting ? "Creating…" : "Create Batch"}
                  </button>
                </form>
              </>
            )}

            {/* ── Add Checkpoint Form ── */}
            {modal.type === "add-checkpoint" && (
              <>
                <h2 className="mb-1 text-lg font-bold text-white">Add Checkpoint</h2>
                <p className="mb-5 text-xs text-stone-500 font-mono">{modal.batchId}</p>
                <form onSubmit={handleAddCheckpoint} className="space-y-4">
                  <div>
                    <label className="mb-1.5 block text-xs font-medium text-stone-400">
                      Supply Chain Status
                    </label>
                    <select
                      value={cpStatus}
                      onChange={(e) => setCpStatus(e.target.value as CheckpointStatus)}
                      className="w-full rounded-lg border border-stone-700 bg-stone-800 px-3 py-2.5 text-sm text-white focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition"
                    >
                      {CHECKPOINT_STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s.charAt(0).toUpperCase() + s.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full rounded-xl bg-amber-500 py-2.5 text-sm font-semibold text-stone-950 hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {submitting ? "Adding…" : "Add Checkpoint"}
                  </button>
                </form>
              </>
            )}

            {/* ── Show QR Code ── */}
            {modal.type === "show-qr" && (
              <div className="text-center">
                <div className="mb-4 flex justify-center">
                  <QrCode className="h-6 w-6 text-amber-400" />
                </div>
                <h2 className="mb-1 text-lg font-bold text-white">Batch Created!</h2>
                <p className="mb-5 text-xs text-stone-500">
                  Share this QR code on the jar for consumer verification.
                </p>
                <div className="mb-4 flex justify-center">
                  <div className="rounded-xl border border-stone-700 bg-white p-3">
                    <Image
                      src={modal.batch.qr_code_url}
                      alt={`QR code for ${modal.batch.batch_id}`}
                      width={160}
                      height={160}
                      unoptimized
                    />
                  </div>
                </div>
                <p className="mb-5 font-mono text-sm font-bold text-amber-400">
                  {modal.batch.batch_id}
                </p>
                <button
                  onClick={closeModal}
                  className="w-full rounded-xl bg-amber-500 py-2.5 text-sm font-semibold text-stone-950 hover:bg-amber-400 transition-colors"
                >
                  Done
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
