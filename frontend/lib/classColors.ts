const CLASS_COLORS: Record<string, string> = {
  crazing: "#f5a524",
  inclusion: "#fb5563",
  patches: "#38bdf8",
  pitted_surface: "#a78bfa",
  "rolled-in_scale": "#fb923c",
  scratches: "#34d399",
};

export function colorForClass(className: string): string {
  return CLASS_COLORS[className] ?? "#f5a524";
}
