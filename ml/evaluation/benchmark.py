"""Benchmark real inference latency/FPS for a trained checkpoint.

Separate from ml/evaluation/evaluate.py's accuracy metrics: this measures wall-clock
speed through the exact same DefectDetector.predict() path the API uses, on whatever
images are available (defaults to the test split), after a warmup pass.

Usage:
    python -m ml.evaluation.benchmark --weights models/best.pt --runs 50
"""
import argparse
import json
import statistics
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.inference.predict import DefectDetector

REPO_ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default=str(REPO_ROOT / "models" / "best.pt"))
    parser.add_argument("--images", default=str(REPO_ROOT / "data" / "test" / "images"))
    parser.add_argument("--runs", type=int, default=50, help="number of timed inference calls")
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--out", default=str(REPO_ROOT / "models" / "benchmark.json"))
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args()

    image_paths = sorted(Path(args.images).glob("*.jpg"))
    if not image_paths:
        raise SystemExit(f"No images found in {args.images}")

    detector = DefectDetector(weights=args.weights, device=args.device)
    images = [Image.open(p).convert("RGB") for p in image_paths[: max(args.runs, args.warmup)]]
    # Cycle through available images if there are fewer than requested runs.
    def image_at(i: int) -> Image.Image:
        return images[i % len(images)]

    for i in range(args.warmup):
        detector.predict(image_at(i))

    latencies_ms = []
    for i in range(args.runs):
        t0 = time.perf_counter()
        detector.predict(image_at(i))
        latencies_ms.append((time.perf_counter() - t0) * 1000)

    latencies_ms.sort()
    mean_ms = statistics.mean(latencies_ms)
    result = {
        "weights": str(args.weights),
        "device": args.device,
        "synthetic_data": args.synthetic,
        "runs": args.runs,
        "mean_ms": round(mean_ms, 2),
        "median_ms": round(statistics.median(latencies_ms), 2),
        "p95_ms": round(latencies_ms[int(0.95 * (args.runs - 1))], 2),
        "min_ms": round(min(latencies_ms), 2),
        "max_ms": round(max(latencies_ms), 2),
        "fps": round(1000 / mean_ms, 2) if mean_ms > 0 else 0.0,
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWritten to {args.out}")


if __name__ == "__main__":
    main()
