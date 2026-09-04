"use client";

import { useEffect, useState, useCallback } from "react";
import type { Batch, CreateBatchInput, CheckpointStatus, Telemetry, HiveSummary } from "@/lib/types";
import { getBatches, createBatch, addCheckpoint, getLatestTelemetry, getTelemetryHistory, getHives, API_BASE_URL } from "@/lib/api";
import BatchCard from "@/components/BatchCard";
import { LoadingSpinner, ErrorState } from "@/components/States";
import { Plus, X, QrCode, Radio, RefreshCw, Thermometer, Droplets, Scale, Activity, ChevronDown, ChevronUp } from "lucide-react";
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

  // ── IoT Telemetry State ──
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);
  const [telemetryHistory, setTelemetryHistory] = useState<Telemetry[]>([]);
  const [telemetryLoading, setTelemetryLoading] = useState(true);
  const [telemetryError, setTelemetryError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [showHistory, setShowHistory] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // ── Hive list state ──
  const [hives, setHives] = useState<HiveSummary[]>([]);

  // ── New batch form state ──
  const [form, setForm] = useState<CreateBatchInput>({
    beekeeper_name: "",
    farm_location: "",
    harvest_date: "",
    quantity_kg: 0,
    hive_id: undefined,
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

  const loadTelemetry = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [latest, history] = await Promise.all([
        getLatestTelemetry("HIVE-01"),
        getTelemetryHistory("HIVE-01", 10),
      ]);
      setTelemetry(latest);
      setTelemetryHistory(history);
      setTelemetryError(null);
    } catch (e) {
      setTelemetryError(e instanceof Error ? e.message : "Failed to load telemetry.");
    } finally {
      setTelemetryLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  const loadHives = useCallback(async () => {
    try {
      const data = await getHives();
      setHives(data);
    } catch {
      // Non-blocking
    }
  }, []);

  useEffect(() => {
    loadBatches();
    loadHives();
  }, [loadBatches, loadHives]);

  useEffect(() => {
    loadTelemetry();
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      loadTelemetry();
    }, 5000);
    return () => clearInterval(interval);
  }, [loadTelemetry, autoRefresh]);

  async function handleCreateBatch(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const newBatch = await createBatch(form);
      setBatches((prev) => [...prev, newBatch]);
      setModal({ type: "show-qr", batch: newBatch });
      setForm({ beekeeper_name: "", farm_location: "", harvest_date: "", quantity_kg: 0, hive_id: undefined });
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

      {/* ── REAL-TIME IOT TELEMETRY SECTION ───────────────────────────────────── */}
      <section className="mb-10 rounded-2xl border border-stone-800 bg-stone-900/90 p-6 shadow-xl backdrop-blur-sm">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-stone-800 pb-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Radio className="h-5 w-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white">Smart Hive Telemetry</h2>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-xs font-semibold text-emerald-400 border border-emerald-500/30">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping" />
                  Live (HIVE-01)
                </span>
              </div>
              <p className="text-xs text-stone-400 mt-0.5 font-mono">
                Source: {telemetry?.device_id ?? "ESP32-HIVE-01"} • Frequency: 5s
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-xs text-stone-400 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-stone-700 bg-stone-800 text-amber-500 focus:ring-amber-500/20"
              />
              Auto-sync (5s)
            </label>
            <button
              onClick={loadTelemetry}
              disabled={isRefreshing}
              className="inline-flex items-center gap-1.5 rounded-lg border border-stone-700 bg-stone-800 px-3 py-1.5 text-xs font-medium text-stone-200 hover:bg-stone-700 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>
        </div>

        {telemetryLoading && !telemetry ? (
          <div className="py-8 text-center text-stone-400 text-sm">
            <LoadingSpinner message="Connecting to IoT telemetry feed…" />
          </div>
        ) : telemetryError && !telemetry ? (
          <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-center">
            <p className="text-sm text-red-400">{telemetryError}</p>
            <p className="text-xs text-stone-500 mt-1">Make sure the FastAPI backend and ESP32 device are running.</p>
          </div>
        ) : telemetry ? (
          <div className="space-y-6">
            {/* Status & Health Header */}
            <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-stone-800 bg-stone-950/60 p-4">
              <div className="flex items-center gap-4">
                <div>
                  <p className="text-xs uppercase tracking-wider text-stone-500 font-mono">Colony Health Score</p>
                  <p className="text-2xl font-bold text-white font-mono">{telemetry.health_score}%</p>
                </div>
                <div className="h-8 w-px bg-stone-800" />
                <div>
                  <p className="text-xs uppercase tracking-wider text-stone-500 font-mono">Status</p>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider ${
                      telemetry.status === "HEALTHY"
                        ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                        : telemetry.status === "WARNING"
                        ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                        : "bg-red-500/15 text-red-400 border border-red-500/30"
                    }`}
                  >
                    {telemetry.status}
                  </span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-stone-500 font-mono">Last Reading #{telemetry.reading_id}</p>
                <p className="text-xs text-stone-400 font-mono">
                  {new Date(telemetry.server_timestamp).toLocaleTimeString("en-IN", {
                    hour12: true,
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                  })}
                </p>
              </div>
            </div>

            {/* Metrics Cards */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {/* Internal Temp */}
              <div className="rounded-xl border border-stone-800 bg-stone-950/50 p-4">
                <div className="flex items-center justify-between text-stone-400 mb-1">
                  <span className="text-xs">Internal Temp</span>
                  <Thermometer className="h-4 w-4 text-amber-400" />
                </div>
                <p className="text-xl font-bold text-white font-mono">
                  {telemetry.internal_temperature.toFixed(1)} <span className="text-xs font-normal text-stone-400">°C</span>
                </p>
                <p className="text-[10px] text-stone-500 mt-1">Optimum: 34.5 - 35.5°C</p>
              </div>

              {/* Humidity */}
              <div className="rounded-xl border border-stone-800 bg-stone-950/50 p-4">
                <div className="flex items-center justify-between text-stone-400 mb-1">
                  <span className="text-xs">Hive Humidity</span>
                  <Droplets className="h-4 w-4 text-sky-400" />
                </div>
                <p className="text-xl font-bold text-white font-mono">
                  {telemetry.humidity.toFixed(1)} <span className="text-xs font-normal text-stone-400">%</span>
                </p>
                <p className="text-[10px] text-stone-500 mt-1">Optimum: 50 - 60%</p>
              </div>

              {/* Hive Weight */}
              <div className="rounded-xl border border-stone-800 bg-stone-950/50 p-4">
                <div className="flex items-center justify-between text-stone-400 mb-1">
                  <span className="text-xs">Hive Weight</span>
                  <Scale className="h-4 w-4 text-emerald-400" />
                </div>
                <p className="text-xl font-bold text-white font-mono">
                  {telemetry.hive_weight.toFixed(1)} <span className="text-xs font-normal text-stone-400">kg</span>
                </p>
                <p className="text-[10px] text-stone-500 mt-1">Honey storage index</p>
              </div>

              {/* Ambient & Delta */}
              <div className="rounded-xl border border-stone-800 bg-stone-950/50 p-4">
                <div className="flex items-center justify-between text-stone-400 mb-1">
                  <span className="text-xs">Ambient / Δ</span>
                  <Activity className="h-4 w-4 text-purple-400" />
                </div>
                <p className="text-xl font-bold text-white font-mono">
                  {telemetry.external_temperature.toFixed(1)} <span className="text-xs font-normal text-stone-400">°C</span>
                </p>
                <p className="text-[10px] text-stone-500 mt-1">
                  Delta: <span className="text-stone-300 font-mono">+{telemetry.temperature_delta.toFixed(1)}°C</span>
                </p>
              </div>
            </div>

            {/* Expandable History Table */}
            <div className="border-t border-stone-800 pt-4">
              <button
                onClick={() => setShowHistory((prev) => !prev)}
                className="flex items-center gap-2 text-xs font-semibold text-stone-400 hover:text-amber-400 transition-colors"
              >
                <span>{showHistory ? "Hide Sensor History Log" : "Show Recent Sensor History Log (Last 10)"}</span>
                {showHistory ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
              </button>

              {showHistory && (
                <div className="mt-4 overflow-x-auto rounded-xl border border-stone-800 bg-stone-950/80">
                  <table className="w-full text-left text-xs text-stone-300">
                    <thead className="bg-stone-900 text-[10px] uppercase text-stone-400">
                      <tr>
                        <th className="px-3 py-2">ID</th>
                        <th className="px-3 py-2">Timestamp</th>
                        <th className="px-3 py-2">Internal</th>
                        <th className="px-3 py-2">External</th>
                        <th className="px-3 py-2">Δ Temp</th>
                        <th className="px-3 py-2">Humidity</th>
                        <th className="px-3 py-2">Weight</th>
                        <th className="px-3 py-2">Health</th>
                        <th className="px-3 py-2">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-stone-800/60 font-mono">
                      {telemetryHistory.map((row) => (
                        <tr key={row.reading_id} className="hover:bg-stone-900/50 transition-colors">
                          <td className="px-3 py-2 text-stone-500">#{row.reading_id}</td>
                          <td className="px-3 py-2 text-stone-400">
                            {new Date(row.server_timestamp).toLocaleTimeString()}
                          </td>
                          <td className="px-3 py-2 text-amber-300">{row.internal_temperature.toFixed(1)}°C</td>
                          <td className="px-3 py-2 text-stone-400">{row.external_temperature.toFixed(1)}°C</td>
                          <td className="px-3 py-2 text-purple-300">+{row.temperature_delta.toFixed(1)}°C</td>
                          <td className="px-3 py-2 text-sky-300">{row.humidity.toFixed(1)}%</td>
                          <td className="px-3 py-2 text-emerald-300">{row.hive_weight.toFixed(1)}kg</td>
                          <td className="px-3 py-2 font-bold text-white">{row.health_score}%</td>
                          <td className="px-3 py-2">
                            <span
                              className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                                row.status === "HEALTHY"
                                  ? "bg-emerald-500/20 text-emerald-400"
                                  : row.status === "WARNING"
                                  ? "bg-amber-500/20 text-amber-400"
                                  : "bg-red-500/20 text-red-400"
                              }`}
                            >
                              {row.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        ) : null}
      </section>

      {/* ── BATCH MANAGEMENT SECTION ────────────────────────────────────────── */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-bold text-white">Supply-Chain Batches</h2>
        <span className="text-xs text-stone-500 font-mono">{batches.length} Registered</span>
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
                  <div>
                    <label className="mb-1.5 block text-xs font-medium text-stone-400">
                      Source Hive (Optional)
                    </label>
                    <select
                      value={form.hive_id ?? ""}
                      onChange={(e) =>
                        setForm((prev) => ({
                          ...prev,
                          hive_id: e.target.value ? e.target.value : undefined,
                        }))
                      }
                      className="w-full rounded-lg border border-stone-700 bg-stone-800 px-3 py-2.5 text-sm text-white focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition"
                    >
                      <option value="">None (Not linked to a smart hive)</option>
                      {hives.map((h) => (
                        <option key={h.hive_id} value={h.hive_id}>
                          {h.hive_id} {h.name ? `— ${h.name}` : `(${h.device_id})`}
                        </option>
                      ))}
                    </select>
                    <p className="mt-1 text-[11px] text-stone-500">
                      Links this honey harvest directly to its IoT monitored apiary.
                    </p>
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
                    <img
                      src={`${API_BASE_URL}/batches/${modal.batch.batch_id}/qr`}
                      alt="Batch QR code"
                      className="h-40 w-40 object-contain"
                    />
                  </div>
                </div>
                <p className="mb-2 font-mono text-sm font-bold text-amber-400">
                  {modal.batch.batch_id}
                </p>
                {modal.batch.qr_code_url && (
                  <div className="mb-5">
                    <a
                      href={modal.batch.qr_code_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-400 hover:text-amber-300 underline underline-offset-2 transition-colors"
                    >
                      Open Verification
                    </a>
                  </div>
                )}
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
