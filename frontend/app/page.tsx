"use client";

import { useState } from "react";
import { BenchmarkPanel } from "@/components/BenchmarkPanel";
import { Header } from "@/components/Header";
import { InspectionWorkspace } from "@/components/InspectionWorkspace";
import { LiveSimulation } from "@/components/LiveSimulation";

type Tab = "inspect" | "simulate" | "benchmark";

export default function Home() {
  const [tab, setTab] = useState<Tab>("inspect");

  return (
    <>
      <Header />
      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
        <div className="mb-6 flex gap-1 border-b border-border">
          {(
            [
              { id: "inspect", label: "Single Inspection" },
              { id: "simulate", label: "Live Simulation" },
              { id: "benchmark", label: "Model Benchmark" },
            ] as const
          ).map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
                tab === t.id
                  ? "border-accent text-foreground"
                  : "border-transparent text-muted hover:text-foreground"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {tab === "inspect" && <InspectionWorkspace />}
        {tab === "simulate" && <LiveSimulation />}
        {tab === "benchmark" && <BenchmarkPanel />}
      </main>
      <footer className="border-t border-border px-6 py-4 text-center text-xs text-muted">
        SteelVision, a portfolio project built on the NEU-DET surface defect dataset.
      </footer>
    </>
  );
}
