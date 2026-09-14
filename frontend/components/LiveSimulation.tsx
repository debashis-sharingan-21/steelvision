"use client";

import {
  ArrowLeft,
  ArrowRight,
  Bug,
  FilmStrip,
  Gauge as GaugeIcon,
  Play,
  Spinner,
  Stop,
  Timer,
  WarningCircle,
} from "@phosphor-icons/react";
import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import { predict } from "@/lib/api";
import { fetchSampleFile, SAMPLE_CLASSES } from "@/lib/sampleImages";
import { PredictResponse } from "@/lib/types";
import { BoundingBoxOverlay } from "./BoundingBoxOverlay";
import { StatusBadge } from "./StatusBadge";
import { MetricTile } from "./MetricTile";

const ACCEPTED = ["image/jpeg", "image/png", "image/bmp"];

export function LiveSimulation() {
  const [files, setFiles] = useState<File[]>([]);
  const [urls, setUrls] = useState<string[]>([]);
  const [index, setIndex] = useState(0);
  const [results, setResults] = useState<Array<PredictResponse | null>>([]);
  const [processing, setProcessing] = useState(false);
  const [processedCount, setProcessedCount] = useState(0);
  const [loadingSamples, setLoadingSamples] = useState(false);
  const [fps, setFps] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const cancelledRef = useRef(false);

  useEffect(() => {
    return () => {
      urls.forEach((url) => URL.revokeObjectURL(url));
      cancelledRef.current = true;
    };
  }, [urls]);

  function setSequence(chosen: File[]) {
    if (chosen.length === 0) return;

    setFiles(chosen);
    setUrls(chosen.map((file) => URL.createObjectURL(file)));
    setIndex(0);
    setResults(Array(chosen.length).fill(null));
    setProcessedCount(0);
    setProcessing(false);
    setError(null);
    cancelledRef.current = false;
  }

  function handleFiles(fileList: FileList | null) {
    const chosen = Array.from(fileList ?? []).filter((file) =>
      ACCEPTED.includes(file.type),
    );

    setSequence(chosen);
  }

  async function loadSampleSequence() {
    setLoadingSamples(true);
    setError(null);

    try {
      const sampleFiles = await Promise.all(
        SAMPLE_CLASSES.map((sample) => fetchSampleFile(sample.class)),
      );

      setSequence(sampleFiles);
    } catch {
      setError("Could not load the sample images.");
    } finally {
      setLoadingSamples(false);
    }
  }

  async function startProcessing() {
    if (files.length === 0 || processing) return;

    cancelledRef.current = false;
    setProcessing(true);
    setError(null);

    for (let i = 0; i < files.length; i += 1) {
      if (cancelledRef.current) break;

      // Skip frames that have already been processed successfully.
      let alreadyProcessed = false;

      setResults((previous) => {
        alreadyProcessed = previous[i] !== null;
        return previous;
      });

      if (alreadyProcessed) {
        continue;
      }

      const t0 = performance.now();

      try {
        const response = await predict(files[i]);

        if (cancelledRef.current) break;

        setResults((previous) => {
          const next = [...previous];
          next[i] = response;
          return next;
        });

        const elapsed = performance.now() - t0;

        setFps(elapsed > 0 ? 1000 / elapsed : 0);
        setProcessedCount((count) => count + 1);

        // Automatically show the first completed result.
        setIndex((current) => (current === 0 ? i : current));
      } catch {
        if (!cancelledRef.current) {
          setError(
            `Frame ${i + 1} could not be processed. Continuing with the remaining frames.`,
          );
        }
      }
    }

    if (!cancelledRef.current) {
      setProcessing(false);
    }
  }

  function stopProcessing() {
    cancelledRef.current = true;
    setProcessing(false);
  }

  const currentUrl = urls[index] ?? null;
  const currentResult = results[index] ?? null;

  const completedResults = results.filter((result) => result !== null).length;

  const canGoPrevious = index > 0;
  const canGoNext = index < Math.max(files.length - 1, 0);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start gap-3 rounded-md border border-accent/30 bg-accent/10 px-4 py-3 text-sm text-accent">
        <FilmStrip size={20} className="mt-0.5 shrink-0" />

        <p>
          <strong>Frame sequence inspection.</strong> Upload multiple steel
          surface frames and run real AI inference on them sequentially.
          Results are stored as they become available, so you can review
          completed frames while the remaining frames continue processing.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <label
          className={`cursor-pointer rounded-md border border-border bg-surface px-4 py-2 text-sm text-foreground transition-colors hover:border-muted ${
            processing || loadingSamples
              ? "pointer-events-none opacity-50"
              : ""
          }`}
        >
          Select image sequence

          <input
            type="file"
            accept={ACCEPTED.join(",")}
            multiple
            disabled={processing || loadingSamples}
            className="hidden"
            onChange={(event) => handleFiles(event.target.files)}
          />
        </label>

        <button
          type="button"
          disabled={processing || loadingSamples}
          onClick={loadSampleSequence}
          className="rounded-md border border-border bg-surface px-4 py-2 text-sm text-muted transition-colors hover:border-muted hover:text-foreground disabled:opacity-50"
        >
          {loadingSamples ? "Loading..." : "Use 6 NEU-DET samples"}
        </button>

        {!processing ? (
          <button
            type="button"
            disabled={files.length === 0}
            onClick={startProcessing}
            className="inline-flex items-center gap-2 rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-colors hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Play size={16} weight="fill" />
            {completedResults > 0 ? "Continue Analysis" : "Start Analysis"}
          </button>
        ) : (
          <button
            type="button"
            onClick={stopProcessing}
            className="inline-flex items-center gap-2 rounded-md border border-status-defect/30 bg-status-defect/10 px-4 py-2 text-sm font-medium text-status-defect"
          >
            <Stop size={16} weight="fill" />
            Stop
          </button>
        )}

        {files.length > 0 && (
          <span className="font-mono text-sm text-muted">
            Frame {index + 1} / {files.length}
          </span>
        )}
      </div>

      {files.length > 0 && (
        <div className="flex flex-col gap-3 rounded-lg border border-border bg-background px-4 py-3">
          <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
            <span className="text-muted">
              Analysis progress
            </span>

            <span className="font-mono text-foreground">
              {completedResults} / {files.length} completed
            </span>
          </div>

          <div className="h-2 overflow-hidden rounded-full bg-surface">
            <div
              className="h-full rounded-full bg-accent transition-all duration-300"
              style={{
                width: `${(completedResults / files.length) * 100}%`,
              }}
            />
          </div>

          {processing && (
            <div className="flex items-center gap-2 text-xs text-muted">
              <Spinner size={14} className="animate-spin" />
              Processing frames in the background. You can browse completed
              results while analysis continues.
            </div>
          )}

          {processing && (
            <div className="flex items-start gap-2 rounded-md border border-accent/30 bg-accent/5 px-3 py-2 text-xs text-accent">
              <WarningCircle size={16} className="mt-0.5 shrink-0" />
              <span>
                Inference is currently slow due to high backend latency.
                Results will appear as each frame finishes.
              </span>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 rounded-md border border-status-defect/30 bg-status-defect/10 px-4 py-3 text-sm text-status-defect">
          <WarningCircle size={18} className="mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      {currentUrl ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="flex flex-col gap-3">
            {currentResult ? (
              <BoundingBoxOverlay
                src={currentUrl}
                alt={`Inspection result for frame ${index + 1}`}
                width={currentResult.image_width}
                height={currentResult.image_height}
                detections={currentResult.detections}
              />
            ) : (
              <div className="relative aspect-square w-full overflow-hidden rounded-lg border border-border bg-black">
                <Image
                  src={currentUrl}
                  alt={`Frame ${index + 1}`}
                  fill
                  unoptimized
                  className="object-contain"
                />

                <div className="absolute inset-x-0 bottom-0 flex items-center justify-center bg-black/65 px-4 py-3">
                  <div className="flex items-center gap-2 text-sm text-muted">
                    {processing && (
                      <Spinner size={16} className="animate-spin text-accent" />
                    )}
                    {processing ? "Waiting for inference..." : "Not analyzed yet"}
                  </div>
                </div>
              </div>
            )}

            <div className="flex items-center justify-between gap-3">
              <button
                type="button"
                disabled={!canGoPrevious}
                onClick={() => setIndex((value) => Math.max(value - 1, 0))}
                className="inline-flex items-center gap-2 rounded-md border border-border bg-surface px-3 py-2 text-sm text-muted transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40"
              >
                <ArrowLeft size={16} />
                Previous
              </button>

              <span className="font-mono text-sm text-muted">
                Frame {index + 1} / {files.length}
              </span>

              <button
                type="button"
                disabled={!canGoNext}
                onClick={() =>
                  setIndex((value) =>
                    Math.min(value + 1, files.length - 1),
                  )
                }
                className="inline-flex items-center gap-2 rounded-md border border-border bg-surface px-3 py-2 text-sm text-muted transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
                <ArrowRight size={16} />
              </button>
            </div>

            <input
              type="range"
              min={0}
              max={Math.max(files.length - 1, 0)}
              value={index}
              onChange={(event) => setIndex(Number(event.target.value))}
              className="w-full accent-[var(--accent)]"
              aria-label="Select frame"
            />
          </div>

          <div className="flex flex-col gap-4">
            {currentResult ? (
              <>
                <StatusBadge status={currentResult.status} />

                <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                  <MetricTile
                    label="Defects"
                    value={currentResult.defect_count}
                    icon={Bug}
                  />

                  <MetricTile
                    label="Latency"
                    value={currentResult.inference_ms}
                    unit="ms"
                    icon={Timer}
                  />

                  <MetricTile
                    label="Inference FPS"
                    value={fps.toFixed(1)}
                    icon={GaugeIcon}
                  />
                </div>

                <div className="rounded-lg border border-border bg-surface px-4 py-3 text-sm">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-muted">Frame status</span>
                    <span className="font-medium text-status-pass">
                      Analysis complete
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex min-h-40 flex-col items-center justify-center rounded-lg border border-border bg-surface px-6 text-center">
                <Spinner
                  size={26}
                  className={processing ? "animate-spin text-accent" : "text-muted"}
                />

                <p className="mt-3 text-sm font-medium text-foreground">
                  {processing ? "Inference pending" : "Frame not analyzed"}
                </p>

                <p className="mt-1 text-xs text-muted">
                  {processing
                    ? "This frame will receive its result when the queue reaches it."
                    : 'Press "Start Analysis" to process the sequence.'}
                </p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <p className="text-sm text-muted">
          Select multiple steel-surface images, or click &quot;Use 6 NEU-DET
          samples&quot; for a quick demo, then press Start Analysis.
        </p>
      )}
    </div>
  );
}