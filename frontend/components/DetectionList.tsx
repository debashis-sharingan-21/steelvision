import { colorForClass } from "@/lib/classColors";
import { Detection } from "@/lib/types";

export function DetectionList({ detections }: { detections: Detection[] }) {
  if (detections.length === 0) {
    return <p className="text-sm text-muted">No defects detected.</p>;
  }

  const sorted = [...detections].sort((a, b) => b.confidence - a.confidence);

  return (
    <ul className="flex flex-col gap-2">
      {sorted.map((d, i) => (
        <li key={i} className="flex items-center gap-3 rounded-md border border-border bg-surface px-3 py-2">
          <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: colorForClass(d.class_name) }} />
          <span className="flex-1 text-sm capitalize text-foreground">{d.class_name.replace(/_/g, " ")}</span>
          <span className="font-mono text-sm text-muted">{(d.confidence * 100).toFixed(1)}%</span>
        </li>
      ))}
    </ul>
  );
}
