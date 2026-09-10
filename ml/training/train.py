"""Train a YOLOv8 detector on the NEU-DET-format dataset described by ml/configs/data.yaml.

Usage:
    python -m ml.training.train --epochs 50 --model yolov8n.pt --name steelvision
    python -m ml.training.train --epochs 3 --model yolov8n.pt --name smoke_test  # synthetic data smoke test

Ultralytics handles checkpointing itself: runs/detect/<name>/weights/{last,best}.pt.
On completion this script copies best.pt to models/best.pt for the API to load.
"""
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml
from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_YAML = REPO_ROOT / "ml" / "configs" / "data.yaml"
MODELS_DIR = REPO_ROOT / "models"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="yolov8n.pt", help="base checkpoint or .yaml arch to start from")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=200)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--name", default="steelvision")
    parser.add_argument("--project", default=str(REPO_ROOT / "runs" / "detect"))
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="mark models/metadata.json to say this checkpoint was trained on synthetic placeholder data",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="continue an interrupted run from <project>/<name>/weights/last.pt instead of starting over",
    )
    args = parser.parse_args()

    if args.resume:
        run_dir = Path(args.project) / args.name
        last = run_dir / "weights" / "last.pt"
        if not last.exists():
            raise SystemExit(f"--resume given but no checkpoint at {last}")
        # The original run's args.yaml is the source of truth for what this checkpoint
        # actually started from — argparse's --model/--epochs/etc. defaults on a resumed
        # invocation describe nothing real and would corrupt metadata.json if trusted.
        original_args = yaml.safe_load((run_dir / "args.yaml").read_text())
        args.model = original_args.get("model", args.model)
        args.epochs = original_args.get("epochs", args.epochs)
        args.imgsz = original_args.get("imgsz", args.imgsz)
        args.device = original_args.get("device", args.device)
        model = YOLO(str(last))
        results = model.train(resume=True)
    else:
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
        shutil.copy2(best, MODELS_DIR / "best.pt")
        print(f"Copied {best} -> {MODELS_DIR / 'best.pt'}")

        metadata = {
            "base_model": args.model,
            "epochs": args.epochs,
            "imgsz": args.imgsz,
            "device": args.device,
            "synthetic_data": args.synthetic,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "run_dir": str(results.save_dir),
        }
        (MODELS_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2))
    else:
        print(f"WARNING: no best.pt found at {best}")


if __name__ == "__main__":
    main()
