"""Train a YOLOv8-seg model on the Severstal-format dataset (ml/segmentation/configs/data_seg.yaml).

Optional module — mirrors ml/training/train.py but for segmentation. See docs/segmentation.md.

Usage:
    python -m ml.segmentation.train_seg --epochs 15 --name seg_smoke_test --synthetic
"""
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_YAML = REPO_ROOT / "ml" / "segmentation" / "configs" / "data_seg.yaml"
MODELS_DIR = REPO_ROOT / "models"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="yolov8n-seg.pt", help="use yolov8n-seg.yaml if pretrained weights can't be downloaded")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=256)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--name", default="steelvision_seg")
    parser.add_argument("--project", default=str(REPO_ROOT / "runs" / "segment"))
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args()

    model = YOLO(args.model)
    results = model.train(
        data=str(DATA_YAML),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        exist_ok=True,
    )

    best = Path(results.save_dir) / "weights" / "best.pt"
    if best.exists():
        MODELS_DIR.mkdir(exist_ok=True)
        shutil.copy2(best, MODELS_DIR / "best_seg.pt")
        print(f"Copied {best} -> {MODELS_DIR / 'best_seg.pt'}")

        metadata = {
            "task": "segment",
            "base_model": args.model,
            "epochs": args.epochs,
            "imgsz": args.imgsz,
            "device": args.device,
            "synthetic_data": args.synthetic,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "run_dir": str(results.save_dir),
        }
        (MODELS_DIR / "metadata_seg.json").write_text(json.dumps(metadata, indent=2))
    else:
        print(f"WARNING: no best.pt found at {best}")


if __name__ == "__main__":
    main()
