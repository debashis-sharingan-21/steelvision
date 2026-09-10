"""Convert the real Severstal Steel Defect Detection dataset (train.csv RLE masks) into
YOLO-seg polygon labels.

Kaggle source: https://www.kaggle.com/competitions/severstal-steel-defect-detection/data
(competition data, accepting rules required — see docs/segmentation.md for exact steps).

Usage:
    python -m ml.segmentation.prepare_severstal --source data/raw/severstal --out data_seg

Expects --source to contain:
    train_images/<ImageId>.jpg
    train.csv   (columns: ImageId_ClassId, EncodedPixels)
"""
import argparse
import csv
import random
import shutil
from collections import defaultdict
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.segmentation.configs.classes import IMAGE_HEIGHT, IMAGE_WIDTH
from ml.segmentation.mask_utils import mask_to_yolo_polygons
from ml.segmentation.rle import rle_decode


def read_annotations(csv_path: Path) -> dict[str, dict[int, str]]:
    """image_id -> {class_idx (0-based): rle_string}"""
    by_image: dict[str, dict[int, str]] = defaultdict(dict)
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            image_id, class_id = row["ImageId_ClassId"].rsplit("_", 1)
            rle = row.get("EncodedPixels", "").strip()
            if rle:
                by_image[image_id][int(class_id) - 1] = rle
    return by_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="dir with train_images/ and train.csv")
    parser.add_argument("--out", default="data_seg")
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    source = Path(args.source)
    images_dir = source / "train_images"
    csv_path = source / "train.csv"
    if not images_dir.is_dir() or not csv_path.is_file():
        raise SystemExit(f"Expected {images_dir} and {csv_path} to exist")

    annotations = read_annotations(csv_path)
    image_ids = sorted(annotations.keys())
    if not image_ids:
        raise SystemExit(f"No annotated images found in {csv_path}")

    rng = random.Random(args.seed)
    rng.shuffle(image_ids)
    n_train = int(len(image_ids) * args.train_ratio)
    n_val = int(len(image_ids) * args.val_ratio)
    splits = {
        "train": image_ids[:n_train],
        "val": image_ids[n_train : n_train + n_val],
        "test": image_ids[n_train + n_val :],
    }

    out = Path(args.out)
    for split_name, ids in splits.items():
        img_out = out / split_name / "images"
        lbl_out = out / split_name / "labels"
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)

        for image_id in ids:
            src_img = images_dir / image_id
            if not src_img.exists():
                print(f"WARNING: missing image {src_img}, skipping")
                continue
            shutil.copy2(src_img, img_out / image_id)

            lines = []
            for class_idx, rle in annotations[image_id].items():
                mask = rle_decode(rle, (IMAGE_HEIGHT, IMAGE_WIDTH))
                for polygon in mask_to_yolo_polygons(mask):
                    coords = " ".join(f"{v:.6f}" for v in polygon)
                    lines.append(f"{class_idx} {coords}")
            (lbl_out / f"{Path(image_id).stem}.txt").write_text("\n".join(lines))

        print(f"{split_name}: {len(ids)} images")

    print(f"Done. YOLO-seg dataset written under {out}/")


if __name__ == "__main__":
    main()
