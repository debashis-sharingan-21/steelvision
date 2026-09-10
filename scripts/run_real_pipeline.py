"""One-command real-data pipeline: download NEU-DET (if needed) -> convert to YOLO ->
train -> evaluate -> benchmark.

Run this on a machine with internet access (this project's own build sandbox has none —
see data/README.md). It reuses the exact same scripts documented individually in
docs/model.md; this just chains them so real results take one command instead of five.

Usage:
    python scripts/run_real_pipeline.py                     # full run, 100 epochs
    python scripts/run_real_pipeline.py --epochs 30 --skip-download
    python scripts/run_real_pipeline.py --kaggle-json path/to/kaggle.json
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw" / "NEU-DET"


def run(cmd: list[str]):
    print(f"\n$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--model", default="yolov8n.pt", help="use yolov8n.yaml instead if you have no internet access to pretrained weights")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--name", default="steelvision")
    parser.add_argument("--skip-download", action="store_true", help="use an already-populated data/raw/NEU-DET/")
    parser.add_argument("--kaggle-json", help="path to a kaggle.json API token; copied to ~/.kaggle/kaggle.json if given")
    args = parser.parse_args()

    if args.kaggle_json:
        kaggle_dir = Path.home() / ".kaggle"
        kaggle_dir.mkdir(exist_ok=True)
        shutil.copy2(args.kaggle_json, kaggle_dir / "kaggle.json")
        print(f"Copied Kaggle credentials to {kaggle_dir / 'kaggle.json'}")

    if not args.skip_download:
        if RAW_DIR.exists() and any(RAW_DIR.iterdir()):
            print(f"{RAW_DIR} already populated, skipping download (use --skip-download to silence this).")
        else:
            run([sys.executable, "scripts/download_neu_det.py", "--out", "data/raw"])

    if not RAW_DIR.exists():
        raise SystemExit(
            f"{RAW_DIR} not found. Either run this with internet access, or manually place the "
            "dataset there (see data/README.md) and re-run with --skip-download."
        )

    run([sys.executable, "-m", "ml.preprocessing.prepare_dataset", "--source", str(RAW_DIR), "--out", "data"])
    run(
        [
            sys.executable, "-m", "ml.training.train",
            "--model", args.model,
            "--epochs", str(args.epochs),
            "--device", args.device,
            "--name", args.name,
        ]
    )
    run([sys.executable, "-m", "ml.evaluation.evaluate", "--weights", "models/best.pt", "--split", "test"])
    run([sys.executable, "-m", "ml.evaluation.benchmark", "--weights", "models/best.pt"])
    run([sys.executable, "-m", "ml.evaluation.error_analysis", "--weights", "models/best.pt", "--split", "test"])

    print(
        "\nDone. Real results: models/metrics.json, models/benchmark.json, "
        "models/error_analysis.json. Paste them into docs/model.md and README.md to "
        "replace the synthetic-data placeholders."
    )


if __name__ == "__main__":
    main()
