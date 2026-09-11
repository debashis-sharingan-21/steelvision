"use client";

import { CircleNotch, Gauge } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { getHealth, getModelInfo } from "@/lib/api";
import { ModelInfoResponse } from "@/lib/types";

export function Header() {
  const [info, setInfo] = useState<ModelInfoResponse | null>(null);
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;

    const checkApi = async () => {
      try {
        const modelInfo = await getModelInfo();

        if (mounted) {
          setInfo(modelInfo);
        }
      } catch {
        if (mounted) {
          setInfo(null);
        }
      }

      try {
        const health = await getHealth();

        if (mounted) {
          setHealthy(health.model_loaded);
        }
      } catch {
        if (mounted) {
          setHealthy(false);
        }
      }
    };

    checkApi();

    const interval = setInterval(checkApi, 10000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="border-b border-border bg-surface">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Gauge size={26} className="text-accent" weight="duotone" />
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-foreground">
              SteelVision
            </h1>
            <p className="text-xs text-muted">
              Stainless steel surface defect inspection
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
          {info ? (
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 divide-x divide-border">
              <span className="text-muted">
                Model{" "}
                <span className="ml-1.5 font-mono text-foreground">
                  {info.architecture}
                </span>
              </span>

              <span className="pl-4 text-muted">
                Classes{" "}
                <span className="ml-1.5 font-mono text-foreground">
                  {info.classes.length}
                </span>
              </span>

              {info.synthetic_model && (
                <span className="ml-1 rounded-md border border-accent/30 bg-accent/10 px-2 py-0.5 text-xs text-accent">
                  synthetic model
                </span>
              )}
            </div>
          ) : healthy === null ? (
            <span className="flex items-center gap-2 text-muted">
              <CircleNotch size={14} className="animate-spin" />
              Checking API...
            </span>
          ) : (
            <span className="rounded-md border border-status-defect/30 bg-status-defect/10 px-2 py-0.5 text-xs text-status-defect">
              Model unavailable
            </span>
          )}

          {healthy !== null && (
            <span className="flex items-center gap-1.5 rounded-md border border-border px-2 py-0.5">
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  healthy ? "bg-status-pass" : "bg-status-defect"
                }`}
              />
              <span className="text-xs text-muted">
                {healthy ? "Online" : "Degraded"}
              </span>
            </span>
          )}
        </div>
      </div>
    </header>
  );
}