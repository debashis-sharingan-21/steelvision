import { ApiError, HealthResponse, MetricsResponse, ModelInfoResponse, PredictResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function unwrap<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new ApiError(detail, res.status);
  }
  return res.json();
}

export async function predict(file: File): Promise<PredictResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/predict`, { method: "POST", body: form });
  return unwrap<PredictResponse>(res);
}

export async function getModelInfo(): Promise<ModelInfoResponse> {
  const res = await fetch(`${API_URL}/model-info`);
  return unwrap<ModelInfoResponse>(res);
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`);
  return unwrap<HealthResponse>(res);
}

export async function getMetrics(): Promise<MetricsResponse> {
  const res = await fetch(`${API_URL}/metrics`);
  return unwrap<MetricsResponse>(res);
}
