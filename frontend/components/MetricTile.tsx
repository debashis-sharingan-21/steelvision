import type { Icon } from "@phosphor-icons/react";

export function MetricTile({
  label,
  value,
  unit,
  icon: IconComponent,
  tone = "default",
}: {
  label: string;
  value: string | number;
  unit?: string;
  icon?: Icon;
  tone?: "default" | "defect" | "pass";
}) {
  const toneClass =
    tone === "defect" ? "text-status-defect" : tone === "pass" ? "text-status-pass" : "text-foreground";

  return (
    <div className="rounded-md border border-border bg-surface px-4 py-3">
      <div className="flex items-center gap-1.5 text-xs uppercase tracking-wide text-muted">
        {IconComponent && <IconComponent size={13} />}
        {label}
      </div>
      <div className={`mt-1 font-mono text-2xl ${toneClass}`}>
        {value}
        {unit && <span className="ml-1 text-sm text-muted">{unit}</span>}
      </div>
    </div>
  );
}
