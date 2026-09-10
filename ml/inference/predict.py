"""Core inference wrapper around a trained YOLO checkpoint.

This is the single place that turns a raw image into the structured detection result
used by both the FastAPI backend (backend/services/inference_service.py) and any CLI/
notebook usage. Keeping it here (not duplicated in backend/) means the API and any
offline scripts always agree on output shape and severity scoring.
"""
import time
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image
from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WEIGHTS = REPO_ROOT / "models" / "best.pt"


@dataclass
class Detection:
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]  # xmin, ymin, xmax, ymax in pixels


@dataclass
class InspectionResult:
    detections: list[Detection]
    defect_count: int
    status: str  # "DEFECT DETECTED" | "PASS"
    inference_ms: float
    severity_score: float
    image_width: int
    image_height: int
    model_name: str = ""


def compute_severity(detections: list[Detection], image_w: int, image_h: int) -> float:
    """Heuristic severity in [0, 100]: combines defect count, confidence, and area coverage.

    This is a demo severity heuristic, NOT a validated industrial standard — see
    docs/model.md for the exact formula and its limitations before treating it as
    anything more than an illustrative ranking signal.
    """
    if not detections:
        return 0.0
    image_area = max(image_w * image_h, 1)
    area_frac = sum(
        max(0.0, d.bbox[2] - d.bbox[0]) * max(0.0, d.bbox[3] - d.bbox[1]) for d in detections
    ) / image_area
    avg_conf = sum(d.confidence for d in detections) / len(detections)
    count_factor = min(len(detections) / 5, 1.0)  # saturate at 5+ defects
    score = 100 * (0.5 * avg_conf + 0.3 * min(area_frac * 10, 1.0) + 0.2 * count_factor)
    return round(min(score, 100.0), 1)


class DefectDetector:
    def __init__(self, weights: str | Path = DEFAULT_WEIGHTS, conf: float = 0.25, device: str = "cpu"):
        self.weights_path = Path(weights)
        if not self.weights_path.exists():
            raise FileNotFoundError(
                f"No model weights at {self.weights_path}. Train one first: "
                "python -m ml.training.train  (see docs/model.md)."
            )
        self.model = YOLO(str(self.weights_path))
        self.conf = conf
        self.device = device

    @property
    def class_names(self) -> list[str]:
        return [self.model.names[i] for i in sorted(self.model.names)]

    def predict(self, image: Image.Image) -> InspectionResult:
        t0 = time.perf_counter()
        results = self.model.predict(source=image, conf=self.conf, device=self.device, verbose=False)
        inference_ms = (time.perf_counter() - t0) * 1000

        r = results[0]
        detections = []
        for box in r.boxes:
            cls_id = int(box.cls.item())
            xyxy = box.xyxy[0].tolist()
            detections.append(
                Detection(
                    class_name=self.model.names[cls_id],
                    confidence=float(box.conf.item()),
                    bbox=(xyxy[0], xyxy[1], xyxy[2], xyxy[3]),
                )
            )

        w, h = image.size
        return InspectionResult(
            detections=detections,
            defect_count=len(detections),
            status="DEFECT DETECTED" if detections else "PASS",
            inference_ms=round(inference_ms, 2),
            severity_score=compute_severity(detections, w, h),
            image_width=w,
            image_height=h,
            model_name=self.weights_path.stem,
        )
