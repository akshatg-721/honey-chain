"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Search, ShieldCheck, ArrowRight, Hexagon } from "lucide-react";
import type { Metadata } from "next";

// NOTE: metadata must be in a server component — kept here as a comment for reference.
// Export from layout.tsx instead. Title is set via layout metadata template.

const FEATURES = [
  {
    icon: "🔗",
    title: "Immutable Ledger",
    desc: "Every stage of your honey's journey is recorded on a tamper-proof hash-chain — permanently and transparently.",
  },
  {
    icon: "📍",
    title: "Full Traceability",
    desc: "Track from hive harvest through processing, packaging, and dispatch — pinpointed to the exact farm and beekeeper.",
  },
  {
    icon: "✅",
    title: "Instant Verification",
    desc: "Scan a QR code or enter a batch ID to receive a cryptographic proof of authenticity in seconds.",
  },
];

export default function LandingPage() {
  const router = useRouter();
  const [batchId, setBatchId] = useState("");
  const [error, setError] = useState("");

  function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = batchId.trim().toUpperCase();
    if (!trimmed) {
      setError("Please enter a batch ID.");
      return;
    }
    router.push(`/verify/${trimmed}`);
  }

  return (
    <div className="flex flex-col">
      {/* ── Hero ─────────────────────────────────────────────────────────────── */}
      <section className="relative isolate overflow-hidden px-4 pt-20 pb-28 sm:pt-28 sm:pb-36">
        {/* Background gradient glow */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 -z-10"
          style={{
            background:
              "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(245,158,11,0.15), transparent)",
          }}
        />

        <div className="mx-auto max-w-3xl text-center">
          {/* Eyebrow */}
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-4 py-1.5">
            <Hexagon className="h-3.5 w-3.5 text-amber-400" />
            <span className="text-xs font-semibold tracking-widest text-amber-400 uppercase">
              Blockchain Traceability
            </span>
          </div>

          {/* Headline */}
          <h1 className="mb-5 text-4xl font-extrabold tracking-tight text-white sm:text-6xl">
            From Hive to Shelf,{" "}
            <span className="bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
              Nothing Hidden.
            </span>
          </h1>

          {/* Subtext */}
          <p className="mx-auto mb-10 max-w-xl text-base leading-relaxed text-stone-400 sm:text-lg">
            Honey Chain records every step of your honey&apos;s supply chain on an
            immutable cryptographic ledger. Beekeepers register batches, add
            checkpoints — and consumers verify authenticity with a single scan.
          </p>

          {/* ── CTA Block ─────────────────────────────────────────── */}
          <div className="flex flex-col items-center gap-6">
            {/* Consumer batch lookup */}
            <form
              onSubmit={handleVerify}
              className="w-full max-w-md"
              noValidate
            >
              <div className="flex items-stretch gap-2">
                <div className="relative flex-1">
                  <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-stone-500" />
                  <input
                    type="text"
                    placeholder="Enter batch ID — e.g. HCB-2024-001"
                    value={batchId}
                    onChange={(e) => {
                      setBatchId(e.target.value);
                      setError("");
                    }}
                    className="w-full rounded-xl border border-stone-700 bg-stone-900 pl-9 pr-4 py-3 text-sm text-white placeholder-stone-500 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition"
                  />
                </div>
                <button
                  type="submit"
                  className="rounded-xl bg-amber-500 px-5 py-3 text-sm font-semibold text-stone-950 hover:bg-amber-400 active:scale-95 transition-all"
                >
                  Verify
                </button>
              </div>
              {error && (
                <p className="mt-2 text-left text-xs text-red-400">{error}</p>
              )}
            </form>

            <div className="flex items-center gap-3 text-stone-600">
              <div className="h-px w-16 bg-stone-800" />
              <span className="text-xs">or</span>
              <div className="h-px w-16 bg-stone-800" />
            </div>

            {/* Admin CTA */}
            <Link
              href="/admin"
              className="group inline-flex items-center gap-2 rounded-xl border border-stone-700 bg-stone-900 px-5 py-3 text-sm font-semibold text-stone-300 hover:border-amber-500/40 hover:text-amber-400 transition-all"
            >
              Admin Dashboard
              <ArrowRight className="h-4 w-4 group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────────────────────────── */}
      <section className="border-t border-stone-800 bg-stone-900/40 px-4 py-20 sm:py-24">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-12 text-center text-2xl font-bold text-white sm:text-3xl">
            Why Honey Chain?
          </h2>
          <div className="grid gap-6 sm:grid-cols-3">
            {FEATURES.map((f) => (
              <div
                key={f.title}
                className="rounded-2xl border border-stone-800 bg-stone-900 p-6 hover:border-amber-500/30 transition-colors"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-amber-500/10 text-2xl">
                  {f.icon}
                </div>
                <h3 className="mb-2 text-base font-semibold text-white">{f.title}</h3>
                <p className="text-sm leading-relaxed text-stone-400">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Verified banner ──────────────────────────────────────────────────── */}
      <section className="border-t border-stone-800 px-4 py-16 text-center">
        <div className="mx-auto max-w-xl">
          <div className="mb-4 flex justify-center">
            <ShieldCheck className="h-10 w-10 text-emerald-400" />
          </div>
          <h2 className="mb-3 text-xl font-bold text-white">
            Trust built into every jar.
          </h2>
          <p className="text-sm text-stone-400">
            Each batch&apos;s full history — harvested, processed, packaged, shipped — is
            cryptographically linked. Tampering with any record breaks the chain,
            making fraud immediately detectable.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-stone-800 px-4 py-8 text-center text-xs text-stone-600">
        © {new Date().getFullYear()} Honey Chain · Built for Smart India Hackathon
      </footer>
    </div>
  );
}
