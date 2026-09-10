"use client";

import { CircleNotch, UploadSimple } from "@phosphor-icons/react";
import Image from "next/image";
import { useCallback, useRef, useState } from "react";
import { fetchSampleFile, SAMPLE_CLASSES } from "@/lib/sampleImages";

const ACCEPTED = ["image/jpeg", "image/png", "image/bmp"];

export function UploadPanel({ onFile, disabled }: { onFile: (file: File) => void; disabled?: boolean }) {
  const [dragging, setDragging] = useState(false);
  const [loadingSample, setLoadingSample] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const file = files?.[0];
      if (!file) return;
      if (!ACCEPTED.includes(file.type)) return;
      onFile(file);
    },
    [onFile],
  );

  async function handleSample(cls: string) {
    if (disabled || loadingSample) return;
    setLoadingSample(cls);
    try {
      onFile(await fetchSampleFile(cls));
    } finally {
      setLoadingSample(null);
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => {
          if (!disabled && (e.key === "Enter" || e.key === " ")) inputRef.current?.click();
        }}
        role="button"
        tabIndex={0}
        aria-disabled={disabled}
        className={`flex min-h-56 cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border border-dashed px-6 text-center transition-all duration-200 ease-out active:scale-[0.99] ${
          dragging ? "border-accent bg-accent/5" : "border-border bg-surface hover:border-muted"
        } ${disabled ? "pointer-events-none opacity-50" : ""}`}
      >
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent/10">
          <UploadSimple size={22} className="text-accent" />
        </div>
        <div>
          <p className="text-sm font-medium text-foreground">Drop a steel strip image, or click to browse</p>
          <p className="mt-1 text-xs text-muted">JPEG, PNG, or BMP up to 10 MB</p>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED.join(",")}
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      <div className="flex flex-col gap-3">
        <div>
          <h3 className="text-sm font-medium text-foreground">Try a sample</h3>
          <p className="text-xs text-muted">Real NEU-DET images, one per defect class. Click one to inspect it instantly.</p>
        </div>

        <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
          {SAMPLE_CLASSES.map((s) => {
            const isLoading = loadingSample === s.class;
            return (
              <button
                key={s.class}
                type="button"
                disabled={disabled || loadingSample !== null}
                onClick={() => handleSample(s.class)}
                aria-label={`Inspect ${s.label} sample`}
                className="group flex flex-col gap-2 rounded-xl border border-border bg-surface p-2 text-left transition-all duration-200 ease-out hover:-translate-y-0.5 hover:border-muted hover:shadow-[0_8px_24px_-12px_rgba(0,0,0,0.5)] active:translate-y-0 active:scale-[0.97] active:duration-100 disabled:pointer-events-none disabled:opacity-40"
              >
                <span className="relative aspect-square w-full shrink-0 overflow-hidden rounded-lg bg-black">
                  <Image
                    src={`/samples/${s.class}.jpg`}
                    alt=""
                    fill
                    unoptimized
                    className="object-cover opacity-85 transition-opacity duration-200 group-hover:opacity-100"
                  />
                  {isLoading && (
                    <span className="absolute inset-0 flex items-center justify-center bg-black/60">
                      <CircleNotch size={18} className="animate-spin text-accent" />
                    </span>
                  )}
                </span>
                <span className="text-xs font-medium text-muted group-hover:text-foreground">{s.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
