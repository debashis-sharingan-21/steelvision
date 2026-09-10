export function severityLabel(score: number): "Low" | "Medium" | "High" {
  if (score < 34) return "Low";
  if (score < 67) return "Medium";
  return "High";
}

export function severityTone(score: number): "pass" | "default" | "defect" {
  if (score < 34) return "pass";
  if (score < 67) return "default";
  return "defect";
}
