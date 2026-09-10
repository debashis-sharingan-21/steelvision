"""Per-class TP/FP/FN error analysis and a worst-offenders list.

This is intentionally independent of ml/evaluation/evaluate.py's Ultralytics-computed
mAP: it re-derives precision/recall from a simple greedy IoU matcher over the same
predictions, as a transparent cross-check, and (more usefully) surfaces which specific
images the model gets most wrong so a human can look at them.

Usage:
    python -m ml.evaluation.error_analysis --weights models/best.pt --split test
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.configs.classes import CLASS_NAMES
from ml.inference.predict import DefectDetector

REPO_ROOT = Path(__file__).resolve().parents[2]


def iou(a, b) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def load_ground_truth(label_path: Path, img_w: int, img_h: int) -> list[tuple[str, tuple[float, float, float, float]]]:
    if not label_path.exists():
        return []
    boxes = []
    for line in label_path.read_text().splitlines():
        if not line.strip():
            continue
        cls_id, cx, cy, w, h = line.split()
        cls_id, cx, cy, w, h = int(cls_id), float(cx), float(cy), float(w), float(h)
        xmin = (cx - w / 2) * img_w
        ymin = (cy - h / 2) * img_h
        xmax = (cx + w / 2) * img_w
        ymax = (cy + h / 2) * img_h
        boxes.append((CLASS_NAMES[cls_id], (xmin, ymin, xmax, ymax)))
    return boxes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default=str(REPO_ROOT / "models" / "best.pt"))
    parser.add_argument("--split", default="test", choices=["val", "test"])
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--top-n", type=int, default=10, help="how many worst images to list")
    parser.add_argument("--out", default=str(REPO_ROOT / "models" / "error_analysis.json"))
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args()

    images_dir = REPO_ROOT / "data" / args.split / "images"
    labels_dir = REPO_ROOT / "data" / args.split / "labels"
    image_paths = sorted(images_dir.glob("*.jpg"))
    if not image_paths:
        raise SystemExit(f"No images found in {images_dir}")

    detector = DefectDetector(weights=args.weights, device=args.device)

    per_class = {c: {"tp": 0, "fp": 0, "fn": 0} for c in CLASS_NAMES}
    image_reports = []

    for img_path in image_paths:
        image = Image.open(img_path).convert("RGB")
        result = detector.predict(image)
        gt_boxes = load_ground_truth(labels_dir / f"{img_path.stem}.txt", image.width, image.height)

        matched_gt = set()
        fp_count = 0
        for det in result.detections:
            best_iou, best_idx = 0.0, -1
            for i, (gt_cls, gt_box) in enumerate(gt_boxes):
                if i in matched_gt or gt_cls != det.class_name:
                    continue
                score = iou(det.bbox, gt_box)
                if score > best_iou:
                    best_iou, best_idx = score, i
            if best_iou >= args.iou_threshold:
                matched_gt.add(best_idx)
                per_class[det.class_name]["tp"] += 1
            else:
                per_class[det.class_name]["fp"] += 1
                fp_count += 1

        fn_count = 0
        for i, (gt_cls, _) in enumerate(gt_boxes):
            if i not in matched_gt:
                per_class[gt_cls]["fn"] += 1
                fn_count += 1

        if fp_count or fn_count:
            image_reports.append({"image": img_path.name, "false_positives": fp_count, "false_negatives": fn_count})

    for cls, counts in per_class.items():
        tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
        counts["precision"] = round(tp / (tp + fp), 4) if (tp + fp) else None
        counts["recall"] = round(tp / (tp + fn), 4) if (tp + fn) else None

    image_reports.sort(key=lambda r: r["false_positives"] + r["false_negatives"], reverse=True)

    out = {
        "weights": str(args.weights),
        "split": args.split,
        "iou_threshold": args.iou_threshold,
        "synthetic_data": args.synthetic,
        "per_class": per_class,
        "worst_images": image_reports[: args.top_n],
        "images_with_errors": len(image_reports),
        "images_evaluated": len(image_paths),
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print(f"\nWritten to {args.out}")


if __name__ == "__main__":
    main()
