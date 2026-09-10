export interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

export interface Detection {
  class_name: string;
  confidence: number;
  bbox: BoundingBox;
}

export interface PredictResponse {
  status: "DEFECT DETECTED" | "PASS";
  defect_count: number;
  detections: Detection[];
  severity_score: number;
  inference_ms: number;
  image_width: number;
  image_height: number;
  model_name: string;
  synthetic_model: boolean;
}

export interface ModelInfoResponse {
  model_name: string;
  architecture: string;
  classes: string[];
  weights_path: string;
  synthetic_model: boolean;
  device: string;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
}

// Passed through verbatim from models/*.json (see ml/evaluation/*.py) — only the
// fields the dashboard actually renders are typed; the rest still round-trips fine
// through the index signature.
export interface EvaluationReport {
  precision: number;
  recall: number;
  f1: number;
  map50: number;
  map50_95: number;
  synthetic_data: boolean;
  per_class_ap50: Record<string, { ap50: number }>;
  [key: string]: unknown;
}

export interface BenchmarkReport {
  mean_ms: number;
  median_ms: number;
  p95_ms: number;
  fps: number;
  runs: number;
  synthetic_data: boolean;
  [key: string]: unknown;
}

export interface ErrorAnalysisReport {
  per_class: Record<string, { tp: number; fp: number; fn: number; precision: number | null; recall: number | null }>;
  worst_images: { image: string; false_positives: number; false_negatives: number }[];
  images_with_errors: number;
  images_evaluated: number;
  synthetic_data: boolean;
  [key: string]: unknown;
}

export interface MetricsResponse {
  evaluation: EvaluationReport | null;
  benchmark: BenchmarkReport | null;
  error_analysis: ErrorAnalysisReport | null;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
