"""Evaluate a trained checkpoint on the test split and write real metrics to models/metrics.json.

Usage:
    python -m ml.evaluation.evaluate --weights models/best.pt --split test

Never hand-edit models/metrics.json — it should always be the direct output of this script,
so numbers in README/docs stay traceable to an actual eval run.
"""
import argparse
import json
import time
from pathlib import Path

from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_YAML = REPO_ROOT / "ml" / "configs" / "data.yaml"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default=str(REPO_ROOT / "models" / "best.pt"))
    parser.add_argument("--split", default="test", choices=["val", "test"])
    parser.add_argument("--imgsz", type=int, default=200)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--out", default=str(REPO_ROOT / "models" / "metrics.json"))
    parser.add_argument("--synthetic", action="store_true", help="mark this run as having used synthetic placeholder data")
    args = parser.parse_args()

    model = YOLO(args.weights)

    t0 = time.perf_counter()
    metrics = model.val(data=str(DATA_YAML), split=args.split, imgsz=args.imgsz, device=args.device)
    elapsed = time.perf_counter() - t0

    precision = float(metrics.box.mp)
    recall = float(metrics.box.mr)
    map50 = float(metrics.box.map50)
    map50_95 = float(metrics.box.map)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    per_class = {}
    class_names = metrics.names
    for i, ap50 in enumerate(metrics.box.ap50.tolist() if hasattr(metrics.box.ap50, "tolist") else metrics.box.ap50):
        per_class[class_names[i]] = {"ap50": float(ap50)}

    out = {
        "weights": str(args.weights),
        "split": args.split,
        "imgsz": args.imgsz,
        "device": args.device,
        "synthetic_data": args.synthetic,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "map50": map50,
        "map50_95": map50_95,
        "per_class_ap50": per_class,
        "eval_wall_time_s": elapsed,
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print(f"\nWritten to {args.out}")


if __name__ == "__main__":
    main()
