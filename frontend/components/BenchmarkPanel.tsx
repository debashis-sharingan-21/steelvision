"use client";

import { ChartLineUp, type Icon, MagnifyingGlass, Timer, WarningCircle } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { getMetrics } from "@/lib/api";
import { MetricsResponse } from "@/lib/types";
import { MetricTile } from "./MetricTile";

function Section({ title, icon: IconComponent, children }: { title: string; icon: Icon; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-3">
      <h3 className="flex items-center gap-2 text-sm font-medium text-foreground">
        <IconComponent size={16} className="text-accent" />
        {title}
      </h3>
      {children}
    </div>
  );
}

function SyntheticNotice() {
  return (
    <div className="flex items-start gap-2 rounded-md border border-accent/30 bg-accent/10 px-4 py-3 text-sm text-accent">
      <WarningCircle size={18} className="mt-0.5 shrink-0" />
      <p>
        These numbers come from a model trained on synthetic placeholder data, not the
        real NEU-DET dataset. See docs/model.md. They prove the evaluation pipeline
        works, not real-world detection accuracy.
      </p>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="flex flex-col gap-8">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        {[0, 1, 2, 3, 4].map((i) => (
          <div key={i} className="h-16 animate-pulse rounded-md bg-surface" />
        ))}
      </div>
      <div className="h-48 animate-pulse rounded-md bg-surface" />
    </div>
  );
}

export function BenchmarkPanel() {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMetrics()
      .then(setMetrics)
      .catch(() => setError("Could not reach the inference API."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Skeleton />;
  if (error) {
    return (
      <div className="flex items-start gap-2 rounded-md border border-status-defect/30 bg-status-defect/10 px-4 py-3 text-sm text-status-defect">
        <WarningCircle size={18} className="mt-0.5 shrink-0" />
        {error}
      </div>
    );
  }
  if (!metrics || (!metrics.evaluation && !metrics.benchmark && !metrics.error_analysis)) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <p className="max-w-md text-center text-sm text-muted">
          No evaluation reports yet. Run <code className="font-mono">ml/evaluation/evaluate.py</code>,{" "}
          <code className="font-mono">benchmark.py</code>, and <code className="font-mono">error_analysis.py</code>{" "}
          (see docs/model.md). This tab reads their output directly, so nothing shows until they have run.
        </p>
      </div>
    );
  }

  const isSynthetic =
    metrics.evaluation?.synthetic_data || metrics.benchmark?.synthetic_data || metrics.error_analysis?.synthetic_data;

  return (
    <div className="flex flex-col gap-8">
      {isSynthetic && <SyntheticNotice />}

      {metrics.evaluation && (
        <Section title="Accuracy (ml/evaluation/evaluate.py)" icon={ChartLineUp}>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
            <MetricTile label="Precision" value={metrics.evaluation.precision.toFixed(3)} />
            <MetricTile label="Recall" value={metrics.evaluation.recall.toFixed(3)} />
            <MetricTile label="F1" value={metrics.evaluation.f1.toFixed(3)} />
            <MetricTile label="mAP@0.5" value={metrics.evaluation.map50.toFixed(3)} />
            <MetricTile label="mAP@0.5:0.95" value={metrics.evaluation.map50_95.toFixed(3)} />
          </div>
          <div className="overflow-x-auto rounded-md border border-border">
            <table className="w-full min-w-[320px] text-sm">
              <thead className="bg-surface text-muted">
                <tr>
                  <th className="px-3 py-2 text-left font-normal">Class</th>
                  <th className="px-3 py-2 text-left font-normal">AP@0.5</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(metrics.evaluation.per_class_ap50).map(([cls, v]) => (
                  <tr key={cls} className="border-t border-border">
                    <td className="px-3 py-2 capitalize text-foreground">{cls.replace(/_/g, " ")}</td>
                    <td className="px-3 py-2 font-mono text-foreground">{v.ap50.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}

      {metrics.benchmark && (
        <Section title="Latency & throughput (ml/evaluation/benchmark.py)" icon={Timer}>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MetricTile label="Mean" value={metrics.benchmark.mean_ms} unit="ms" />
            <MetricTile label="Median" value={metrics.benchmark.median_ms} unit="ms" />
            <MetricTile label="P95" value={metrics.benchmark.p95_ms} unit="ms" />
            <MetricTile label="Throughput" value={metrics.benchmark.fps} unit="FPS" />
          </div>
        </Section>
      )}

      {metrics.error_analysis && (
        <Section title="Error analysis (ml/evaluation/error_analysis.py)" icon={MagnifyingGlass}>
          <div className="overflow-x-auto rounded-md border border-border">
            <table className="w-full min-w-[320px] text-sm">
              <thead className="bg-surface text-muted">
                <tr>
                  <th className="px-3 py-2 text-left font-normal">Class</th>
                  <th className="px-3 py-2 text-left font-normal">TP</th>
                  <th className="px-3 py-2 text-left font-normal">FP</th>
                  <th className="px-3 py-2 text-left font-normal">FN</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(metrics.error_analysis.per_class).map(([cls, c]) => (
                  <tr key={cls} className="border-t border-border">
                    <td className="px-3 py-2 capitalize text-foreground">{cls.replace(/_/g, " ")}</td>
                    <td className="px-3 py-2 font-mono text-foreground">{c.tp}</td>
                    <td className="px-3 py-2 font-mono text-status-defect">{c.fp}</td>
                    <td className="px-3 py-2 font-mono text-status-defect">{c.fn}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {metrics.error_analysis.worst_images.length > 0 && (
            <div>
              <p className="mb-2 text-xs uppercase tracking-wide text-muted">Worst images</p>
              <ul className="flex flex-col gap-1 font-mono text-sm text-muted">
                {metrics.error_analysis.worst_images.slice(0, 5).map((img) => (
                  <li key={img.image}>
                    {img.image}: {img.false_positives} FP, {img.false_negatives} FN
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Section>
      )}
    </div>
  );
}
