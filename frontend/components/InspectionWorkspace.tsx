"use client";

import { Bug, Gauge, Timer, WarningCircle } from "@phosphor-icons/react";
import Image from "next/image";
import { useState } from "react";
import { predict } from "@/lib/api";
import { severityLabel, severityTone } from "@/lib/severity";
import { ApiError, PredictResponse } from "@/lib/types";
import { UploadPanel } from "./UploadPanel";
import { BoundingBoxOverlay } from "./BoundingBoxOverlay";
import { StatusBadge } from "./StatusBadge";
import { MetricTile } from "./MetricTile";
import { DetectionList } from "./DetectionList";

type ImageView = "annotated" | "original";

function ResultSkeleton() {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="aspect-square animate-pulse rounded-lg bg-surface" />
      <div className="flex flex-col gap-4">
        <div className="h-8 w-40 animate-pulse rounded-md bg-surface" />
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-16 animate-pulse rounded-md bg-surface" />
          ))}
        </div>
        <div className="h-24 animate-pulse rounded-md bg-surface" />
      </div>
    </div>
  );
}

export function InspectionWorkspace() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [view, setView] = useState<ImageView>("annotated");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PredictResponse | null>(null);

  async function handleFile(file: File) {
    setError(null);
    setResult(null);
    setView("annotated");
    setLoading(true);
    const url = URL.createObjectURL(file);
    setImageUrl(url);

    try {
      const res = await predict(file);
      setResult(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reach the inference API.");
    } finally {
      setLoading(false);
    }
  }

  const idle = !loading && !error && !result;

  return (
    <div className={`flex flex-col gap-6 ${idle ? "min-h-[50vh] justify-center" : ""}`}>
      <UploadPanel onFile={handleFile} disabled={loading} />

      {error && (
        <div className="flex items-start gap-2 rounded-md border border-status-defect/30 bg-status-defect/10 px-4 py-3 text-sm text-status-defect">
          <WarningCircle size={18} className="mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      {loading && <ResultSkeleton />}

      {!loading && result && imageUrl && (
        <div className="animate-result-enter grid gap-6 lg:grid-cols-2">
          <div className="flex flex-col gap-2">
            <div className="flex gap-1 self-start rounded-md border border-border bg-surface p-0.5">
              {(["annotated", "original"] as const).map((v) => (
                <button
                  key={v}
                  onClick={() => setView(v)}
                  className={`rounded px-3 py-1 text-xs font-medium capitalize transition-colors ${
                    view === v ? "bg-accent text-accent-foreground" : "text-muted hover:text-foreground"
                  }`}
                >
                  {v}
                </button>
              ))}
            </div>

            {view === "annotated" ? (
              <BoundingBoxOverlay
                src={imageUrl}
                alt="Annotated inspection result"
                width={result.image_width}
                height={result.image_height}
                detections={result.detections}
              />
            ) : (
              <div
                className="relative w-full overflow-hidden rounded-lg border border-border bg-black"
                style={{ aspectRatio: `${result.image_width} / ${result.image_height}` }}
              >
                <Image src={imageUrl} alt="Original upload" fill unoptimized className="object-contain" />
              </div>
            )}
          </div>

          <div className="flex flex-col gap-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <StatusBadge status={result.status} />
              {result.synthetic_model && (
                <span className="rounded-md border border-accent/30 bg-accent/10 px-2 py-1 text-xs text-accent">
                  Synthetic-data model
                </span>
              )}
            </div>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <MetricTile label="Defects" value={result.defect_count} icon={Bug} />
              <MetricTile
                label="Severity"
                value={severityLabel(result.severity_score)}
                unit={`${result.severity_score}/100`}
                icon={Gauge}
                tone={severityTone(result.severity_score)}
              />
              <MetricTile label="Inference" value={result.inference_ms} unit="ms" icon={Timer} />
            </div>

            <div>
              <h3 className="mb-2 text-sm font-medium text-foreground">Detections</h3>
              <DetectionList detections={result.detections} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
