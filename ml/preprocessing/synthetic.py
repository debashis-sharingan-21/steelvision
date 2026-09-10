"""Generate a SYNTHETIC placeholder dataset with the same 6 NEU-DET class names and
YOLO layout as the real dataset.

This is NOT real steel imagery. It exists solely so the rest of the pipeline
(training, evaluation, inference, API, frontend) can be run and smoke-tested in an
environment without internet access to the real NEU-DET dataset. Any metric produced
from this data must be reported as a synthetic pipeline-validation number, never as a
measure of real-world defect-detection accuracy — see docs/model.md.

Usage:
    python -m ml.preprocessing.synthetic --out data --per-class 40
"""
import argparse
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.configs.classes import CLASS_NAMES

IMG_SIZE = 200


def steel_background(rng: random.Random) -> Image.Image:
    base = 120 + rng.randint(-15, 15)
    arr = np.full((IMG_SIZE, IMG_SIZE), base, dtype=np.uint8)
    noise = rng.gauss
    grain = np.array([[max(0, min(255, base + noise(0, 6))) for _ in range(IMG_SIZE)] for _ in range(IMG_SIZE)], dtype=np.uint8)
    return Image.fromarray(grain, mode="L").convert("RGB")


def draw_defect(draw: ImageDraw.ImageDraw, cls: str, rng: random.Random):
    """Draw a shape loosely evoking each defect class and return its bbox (xmin,ymin,xmax,ymax)."""
    cx, cy = rng.randint(50, IMG_SIZE - 50), rng.randint(50, IMG_SIZE - 50)
    color = rng.randint(20, 70)

    if cls == "scratches":
        length = rng.randint(40, 90)
        angle_dx, angle_dy = rng.choice([(1, 0.2), (1, -0.2), (0.2, 1)])
        x0, y0 = cx - length * angle_dx / 2, cy - length * angle_dy / 2
        x1, y1 = cx + length * angle_dx / 2, cy + length * angle_dy / 2
        draw.line([(x0, y0), (x1, y1)], fill=color, width=rng.randint(2, 4))
        box = (min(x0, x1) - 3, min(y0, y1) - 3, max(x0, x1) + 3, max(y0, y1) + 3)
    elif cls == "crazing":
        for _ in range(rng.randint(3, 6)):
            dx, dy = rng.randint(-20, 20), rng.randint(-20, 20)
            draw.line([(cx, cy), (cx + dx, cy + dy)], fill=color, width=1)
        box = (cx - 22, cy - 22, cx + 22, cy + 22)
    elif cls == "inclusion":
        r = rng.randint(6, 14)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
        box = (cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2)
    elif cls == "pitted_surface":
        r = rng.randint(3, 6)
        pts = [(cx + rng.randint(-25, 25), cy + rng.randint(-25, 25)) for _ in range(rng.randint(4, 7))]
        for px, py in pts:
            draw.ellipse([px - r, py - r, px + r, py + r], fill=color)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        box = (min(xs) - r, min(ys) - r, max(xs) + r, max(ys) + r)
    elif cls == "patches":
        w, h = rng.randint(30, 60), rng.randint(20, 40)
        box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        draw.rectangle(box, fill=color)
    elif cls == "rolled-in_scale":
        w, h = rng.randint(35, 70), rng.randint(8, 16)
        box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        draw.rectangle(box, fill=color)
        for i in range(3):
            draw.line([(box[0], box[1] + i * h / 3), (box[2], box[1] + i * h / 3)], fill=color - 10, width=1)
    else:
        raise ValueError(cls)

    xmin, ymin, xmax, ymax = box
    return (max(0, xmin), max(0, ymin), min(IMG_SIZE, xmax), min(IMG_SIZE, ymax))


def make_sample(cls: str, rng: random.Random):
    img = steel_background(rng)
    draw = ImageDraw.Draw(img)
    n_defects = rng.choice([1, 1, 1, 2])
    boxes = []
    for _ in range(n_defects):
        box = draw_defect(draw, cls, rng)
        boxes.append(box)
    return img, boxes


def yolo_label(cls_idx: int, box, img_size=IMG_SIZE) -> str:
    xmin, ymin, xmax, ymax = box
    cx = (xmin + xmax) / 2 / img_size
    cy = (ymin + ymax) / 2 / img_size
    w = (xmax - xmin) / img_size
    h = (ymax - ymin) / img_size
    return f"{cls_idx} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data")
    parser.add_argument("--per-class", type=int, default=40, help="synthetic images per class per split multiplier")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    out = Path(args.out)
    split_counts = {"train": args.per_class, "val": max(4, args.per_class // 5), "test": max(4, args.per_class // 5)}

    for split, count in split_counts.items():
        img_dir = out / split / "images"
        lbl_dir = out / split / "labels"
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        for cls_idx, cls in enumerate(CLASS_NAMES):
            for i in range(count):
                img, boxes = make_sample(cls, rng)
                name = f"{cls}_{split}_{i:04d}"
                img.save(img_dir / f"{name}.jpg", quality=90)
                lines = [yolo_label(cls_idx, b) for b in boxes]
                (lbl_dir / f"{name}.txt").write_text("\n".join(lines))
        print(f"{split}: {count * len(CLASS_NAMES)} synthetic images")

    readme = out / "SYNTHETIC_DATA_NOTICE.md"
    readme.write_text(
        "# Synthetic placeholder data\n\n"
        "Everything under train/val/test in this data/ directory (unless you have run "
        "ml/preprocessing/prepare_dataset.py on the real NEU-DET dataset) was generated by "
        "ml/preprocessing/synthetic.py. It is procedurally drawn shapes, not real steel "
        "imagery, and exists only to let the training/inference/API/frontend pipeline run "
        "end-to-end without internet access. Do not report metrics from this data as real "
        "model performance. See docs/model.md.\n"
    )
    print(f"Done. Synthetic YOLO dataset written under {out}/ ({readme.name} added as a warning marker).")


if __name__ == "__main__":
    main()
