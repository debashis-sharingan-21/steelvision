"""Segmentation inference wrapper, analogous to ml/inference/predict.py's DefectDetector.

Not wired into the FastAPI backend or dashboard by default — this is an optional,
experimental module (see docs/segmentation.md). Kept separate so the detection API's
existing, working behavior is untouched.
"""
import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WEIGHTS = REPO_ROOT / "models" / "best_seg.pt"


@dataclass
class SegmentationInstance:
    class_name: str
    confidence: float
    polygon: list[tuple[float, float]]  # pixel coordinates


@dataclass
class SegmentationResult:
    instances: list[SegmentationInstance]
    defect_count: int
    status: str
    inference_ms: float
    image_width: int
    image_height: int


class SegmentationInspector:
    def __init__(self, weights: str | Path = DEFAULT_WEIGHTS, conf: float = 0.25, device: str = "cpu"):
        self.weights_path = Path(weights)
        if not self.weights_path.exists():
            raise FileNotFoundError(
                f"No segmentation weights at {self.weights_path}. Train one first: "
                "python -m ml.segmentation.train_seg (see docs/segmentation.md)."
            )
        self.model = YOLO(str(self.weights_path))
        self.conf = conf
        self.device = device

    def predict(self, image: Image.Image) -> SegmentationResult:
        t0 = time.perf_counter()
        results = self.model.predict(source=image, conf=self.conf, device=self.device, verbose=False)
        inference_ms = (time.perf_counter() - t0) * 1000

        r = results[0]
        instances = []
        if r.masks is not None:
            for cls_tensor, conf_tensor, polygon in zip(r.boxes.cls, r.boxes.conf, r.masks.xy):
                instances.append(
                    SegmentationInstance(
                        class_name=self.model.names[int(cls_tensor.item())],
                        confidence=float(conf_tensor.item()),
                        polygon=[(float(x), float(y)) for x, y in polygon],
                    )
                )

        w, h = image.size
        return SegmentationResult(
            instances=instances,
            defect_count=len(instances),
            status="DEFECT DETECTED" if instances else "PASS",
            inference_ms=round(inference_ms, 2),
            image_width=w,
            image_height=h,
        )
