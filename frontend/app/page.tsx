"use client";

import { ChartLineUp, Camera, FilmStrip } from "@phosphor-icons/react";
import { useState } from "react";
import { BenchmarkPanel } from "@/components/BenchmarkPanel";
import { Header } from "@/components/Header";
import { InspectionWorkspace } from "@/components/InspectionWorkspace";
import { LiveSimulation } from "@/components/LiveSimulation";

type Tab = "inspect" | "simulate" | "benchmark";

const tabs = [
  {
    id: "inspect",
    label: "Single Inspection",
    icon: Camera,
    description: "Analyze one steel-surface image",
  },
  {
    id: "simulate",
    label: "Live Simulation",
    icon: FilmStrip,
    description: "Run repeated inspection inference",
  },
  {
    id: "benchmark",
    label: "Model Benchmark",
    icon: ChartLineUp,
    description: "Review model performance",
  },
] as const;

export default function Home() {
  const [tab, setTab] = useState<Tab>("inspect");

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="mx-auto w-full max-w-6xl px-6 py-8">
        <div className="mb-8">
          <div className="mb-5">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-accent">
              Industrial vision console
            </p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
              Surface Defect Inspection
            </h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
              Inspect stainless-steel surface images with the deployed YOLOv8
              detection model, review defect severity, and evaluate model
              performance.
            </p>
          </div>

          <div className="rounded-xl border border-border bg-surface p-1">
            <div className="grid gap-1 md:grid-cols-3">
              {tabs.map((t) => {
                const Icon = t.icon;
                const active = tab === t.id;

                return (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setTab(t.id)}
                    className={`group rounded-lg px-4 py-3 text-left transition-all duration-200 ${
                      active
                        ? "bg-surface-elevated shadow-sm"
                        : "hover:bg-surface-elevated/60"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span
                        className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md ${
                          active
                            ? "bg-accent/10 text-accent"
                            : "bg-background text-muted group-hover:text-foreground"
                        }`}
                      >
                        <Icon size={17} weight={active ? "duotone" : "regular"} />
                      </span>

                      <span className="min-w-0">
                        <span
                          className={`block text-sm font-medium ${
                            active
                              ? "text-foreground"
                              : "text-muted group-hover:text-foreground"
                          }`}
                        >
                          {t.label}
                        </span>
                        <span className="mt-0.5 block text-xs text-muted">
                          {t.description}
                        </span>
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <section className="rounded-xl border border-border bg-surface/40 p-5 sm:p-6">
          {tab === "inspect" && <InspectionWorkspace />}
          {tab === "simulate" && <LiveSimulation />}
          {tab === "benchmark" && <BenchmarkPanel />}
        </section>
      </main>

      <footer className="border-t border-border px-6 py-4 text-center text-xs text-muted">
        SteelVision, a portfolio project built on the NEU-DET surface defect
        dataset.
      </footer>
    </div>
  );
}