from typing import Any

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float


class Detection(BaseModel):
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BoundingBox


class PredictResponse(BaseModel):
    status: str = Field(description='"DEFECT DETECTED" or "PASS"')
    defect_count: int
    detections: list[Detection]
    severity_score: float = Field(description="0-100 heuristic, see docs/model.md")
    inference_ms: float
    image_width: int
    image_height: int
    model_name: str
    synthetic_model: bool = Field(
        description="True if the loaded weights were trained on synthetic placeholder data, not real NEU-DET images."
    )


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    model_name: str
    architecture: str
    classes: list[str]
    weights_path: str
    synthetic_model: bool
    device: str


class ErrorResponse(BaseModel):
    detail: str


class MetricsResponse(BaseModel):
    """Verbatim contents of models/*.json, written only by ml/evaluation/*.py — never
    hand-edited, so whatever this returns is exactly what those scripts measured. Each
    field is null if that script hasn't been run yet for the currently loaded model."""

    evaluation: dict[str, Any] | None = Field(description="ml/evaluation/evaluate.py output (models/metrics.json)")
    benchmark: dict[str, Any] | None = Field(description="ml/evaluation/benchmark.py output (models/benchmark.json)")
    error_analysis: dict[str, Any] | None = Field(
        description="ml/evaluation/error_analysis.py output (models/error_analysis.json)"
    )
