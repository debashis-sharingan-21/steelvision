import io
import json
import logging
import os
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from ml.inference.predict import DefectDetector

logger = logging.getLogger("steelvision")

REPO_ROOT = Path(__file__).resolve().parents[2]
WEIGHTS_PATH = Path(os.environ.get("STEELVISION_WEIGHTS", REPO_ROOT / "models" / "best.pt"))
METADATA_PATH = REPO_ROOT / "models" / "metadata.json"
METRICS_PATH = REPO_ROOT / "models" / "metrics.json"
BENCHMARK_PATH = REPO_ROOT / "models" / "benchmark.json"
ERROR_ANALYSIS_PATH = REPO_ROOT / "models" / "error_analysis.json"

MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/bmp"}


class InferenceService:
    """Owns the single loaded model instance for the process's lifetime."""

    def __init__(self):
        self.detector: DefectDetector | None = None
        self.metadata: dict = {}
        self.load_error: str | None = None

    def load(self):
        self.metadata = json.loads(METADATA_PATH.read_text()) if METADATA_PATH.exists() else {}
        try:
            self.detector = DefectDetector(weights=WEIGHTS_PATH)
        except Exception as exc:  # model missing or corrupt — surface as a clear 503, not a crash
            self.load_error = str(exc)
            logger.error("Failed to load model: %s", exc)

    @property
    def is_ready(self) -> bool:
        return self.detector is not None

    def model_info(self) -> dict:
        return {
            "model_name": WEIGHTS_PATH.stem,
            "architecture": self.metadata.get("base_model", "unknown"),
            "classes": self.detector.class_names if self.detector else [],
            "weights_path": str(WEIGHTS_PATH),
            "synthetic_model": bool(self.metadata.get("synthetic_data", False)),
            "device": self.metadata.get("device", "cpu"),
        }

    def metrics(self) -> dict:
        def read_json(path: Path) -> dict | None:
            return json.loads(path.read_text()) if path.exists() else None

        return {
            "evaluation": read_json(METRICS_PATH),
            "benchmark": read_json(BENCHMARK_PATH),
            "error_analysis": read_json(ERROR_ANALYSIS_PATH),
        }

    async def validate_and_load_image(self, file: UploadFile) -> Image.Image:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=415, detail=f"Unsupported file type: {file.content_type}. Use JPEG, PNG, or BMP.")

        raw = await file.read()
        if len(raw) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail=f"Image too large: {len(raw)} bytes (max {MAX_IMAGE_BYTES}).")
        if not raw:
            raise HTTPException(status_code=400, detail="Empty file.")

        try:
            image = Image.open(io.BytesIO(raw))
            image.load()
        except UnidentifiedImageError:
            raise HTTPException(status_code=400, detail="File is not a valid image.")

        return image.convert("RGB")

    def predict(self, image: Image.Image) -> dict:
        if not self.is_ready:
            raise HTTPException(status_code=503, detail="Model is not loaded. See server logs.")
        try:
            result = self.detector.predict(image)
        except Exception as exc:
            logger.exception("Inference failed")
            raise HTTPException(status_code=500, detail="Inference failed.") from exc

        return {
            "status": result.status,
            "defect_count": result.defect_count,
            "detections": [
                {
                    "class_name": d.class_name,
                    "confidence": d.confidence,
                    "bbox": {"x_min": d.bbox[0], "y_min": d.bbox[1], "x_max": d.bbox[2], "y_max": d.bbox[3]},
                }
                for d in result.detections
            ],
            "severity_score": result.severity_score,
            "inference_ms": result.inference_ms,
            "image_width": result.image_width,
            "image_height": result.image_height,
            "model_name": result.model_name,
            "synthetic_model": bool(self.metadata.get("synthetic_data", False)),
        }


inference_service = InferenceService()
