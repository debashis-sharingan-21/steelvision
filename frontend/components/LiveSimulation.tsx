"use client";

import { Bug, FilmStrip, Gauge as GaugeIcon, Pause, Play, Timer } from "@phosphor-icons/react";
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
  const [playing, setPlaying] = useState(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [fps, setFps] = useState(0);
  const [loadingSamples, setLoadingSamples] = useState(false);
  const runningRef = useRef(false);

  useEffect(() => {
    return () => urls.forEach((u) => URL.revokeObjectURL(u));
  }, [urls]);

  function setSequence(chosen: File[]) {
    if (chosen.length === 0) return;
    setFiles(chosen);
    setUrls(chosen.map((f) => URL.createObjectURL(f)));
    setIndex(0);
    setResult(null);
  }

  function handleFiles(fileList: FileList | null) {
    setSequence(Array.from(fileList ?? []).filter((f) => ACCEPTED.includes(f.type)));
  }

  async function loadSampleSequence() {
    setLoadingSamples(true);
    try {
      const sampleFiles = await Promise.all(SAMPLE_CLASSES.map((s) => fetchSampleFile(s.class)));
      setSequence(sampleFiles);
    } finally {
      setLoadingSamples(false);
    }
  }

  useEffect(() => {
    if (!playing || files.length === 0) return;
    runningRef.current = true;

    let cancelled = false;
    async function loop() {
      while (!cancelled && runningRef.current) {
        const i = index % files.length;
        const t0 = performance.now();
        try {
          const res = await predict(files[i]);
          if (cancelled) return;
          setResult(res);
          const elapsed = performance.now() - t0;
          setFps(elapsed > 0 ? 1000 / elapsed : 0);
        } catch {
          // a single failed frame shouldn't stop the simulation loop
        }
        setIndex((prev) => (prev + 1) % files.length);
        await new Promise((r) => setTimeout(r, 50));
      }
    }
    loop();

    return () => {
      cancelled = true;
      runningRef.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playing, files]);

  const currentUrl = urls[index % Math.max(urls.length, 1)];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start gap-3 rounded-md border border-accent/30 bg-accent/10 px-4 py-3 text-sm text-accent">
        <FilmStrip size={20} className="mt-0.5 shrink-0" />
        <p>
          <strong>Simulation mode.</strong> This cycles through images you select on this page and calls the same
          /predict endpoint repeatedly. It is not a live camera feed; see docs/deployment.md for how a real
          industrial camera would connect here.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <label className="cursor-pointer rounded-md border border-border bg-surface px-4 py-2 text-sm text-foreground transition-colors hover:border-muted">
          Select image sequence
          <input type="file" accept={ACCEPTED.join(",")} multiple className="hidden" onChange={(e) => handleFiles(e.target.files)} />
        </label>

        <button
          type="button"
          disabled={loadingSamples}
          onClick={loadSampleSequence}
          className="rounded-md border border-border bg-surface px-4 py-2 text-sm text-muted transition-colors hover:border-muted hover:text-foreground disabled:opacity-50"
        >
          {loadingSamples ? "Loading..." : "Use 6 NEU-DET samples"}
        </button>

        <button
          disabled={files.length === 0}
          onClick={() => setPlaying((p) => !p)}
          className="inline-flex items-center gap-2 rounded-md bg-accent px-4 py-2 text-sm font-medium text-accent-foreground disabled:cursor-not-allowed disabled:opacity-40"
        >
          {playing ? <Pause size={16} weight="fill" /> : <Play size={16} weight="fill" />}
          {playing ? "Pause" : "Start"}
        </button>

        {files.length > 0 && (
          <span className="font-mono text-sm text-muted">
            Frame {index + 1} / {files.length}
          </span>
        )}
      </div>

      {currentUrl && result ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <BoundingBoxOverlay
            src={currentUrl}
            alt="Live simulation frame"
            width={result.image_width}
            height={result.image_height}
            detections={result.detections}
          />
          <div className="flex flex-col gap-4">
            <StatusBadge status={result.status} />
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <MetricTile label="FPS" value={fps.toFixed(1)} icon={GaugeIcon} />
              <MetricTile label="Latency" value={result.inference_ms} unit="ms" icon={Timer} />
              <MetricTile label="Defects" value={result.defect_count} icon={Bug} />
            </div>
          </div>
        </div>
      ) : (
        files.length === 0 && (
          <p className="text-sm text-muted">
            Select a folder of images, or click &quot;Use 6 NEU-DET samples&quot; for a quick demo, then press Start.
          </p>
        )
      )}
    </div>
  );
}
