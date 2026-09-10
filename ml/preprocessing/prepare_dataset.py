"""Convert the real NEU-DET dataset (Pascal VOC XML annotations) into YOLO format
and split it into train/val/test.

Usage:
    python -m ml.preprocessing.prepare_dataset --source data/raw/NEU-DET --out data

Expects --source to contain:
    IMAGES/<name>.jpg
    ANNOTATIONS/<name>.xml   (Pascal VOC: <size>, one or more <object><bndbox>)

Writes:
    <out>/train/{images,labels}, <out>/val/{images,labels}, <out>/test/{images,labels}
"""
import argparse
import random
import shutil
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.configs.classes import CLASS_NAMES

CLASS_INDEX = {name: i for i, name in enumerate(CLASS_NAMES)}

# NEU-DET annotation files use short/varied spellings for a couple of classes.
CLASS_ALIASES = {
    "crazing": "crazing",
    "inclusion": "inclusion",
    "patches": "patches",
    "pitted_surface": "pitted_surface",
    "rolled-in_scale": "rolled-in_scale",
    "rolled-in scale": "rolled-in_scale",
    "scratches": "scratches",
}


def voc_to_yolo_line(obj_name: str, xmin: float, ymin: float, xmax: float, ymax: float, img_w: int, img_h: int) -> str:
    cls = CLASS_ALIASES.get(obj_name.strip().lower(), obj_name.strip().lower())
    if cls not in CLASS_INDEX:
        raise ValueError(f"Unknown class '{obj_name}' — expected one of {CLASS_NAMES}")
    cx = (xmin + xmax) / 2 / img_w
    cy = (ymin + ymax) / 2 / img_h
    w = (xmax - xmin) / img_w
    h = (ymax - ymin) / img_h
    return f"{CLASS_INDEX[cls]} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"


def parse_annotation(xml_path: Path) -> list[str]:
    root = ET.parse(xml_path).getroot()
    size = root.find("size")
    img_w = int(size.findtext("width"))
    img_h = int(size.findtext("height"))
    lines = []
    for obj in root.findall("object"):
        name = obj.findtext("name")
        box = obj.find("bndbox")
        xmin, ymin = float(box.findtext("xmin")), float(box.findtext("ymin"))
        xmax, ymax = float(box.findtext("xmax")), float(box.findtext("ymax"))
        lines.append(voc_to_yolo_line(name, xmin, ymin, xmax, ymax, img_w, img_h))
    return lines


def stratified_split(items: list[Path], train=0.7, val=0.15, seed=42) -> dict[str, list[Path]]:
    by_class: dict[str, list[Path]] = defaultdict(list)
    for p in items:
        by_class[p.stem.rsplit("_", 1)[0]].append(p)

    rng = random.Random(seed)
    splits = {"train": [], "val": [], "test": []}
    for cls, files in by_class.items():
        files = sorted(files)
        rng.shuffle(files)
        n = len(files)
        n_train = int(n * train)
        n_val = int(n * val)
        splits["train"] += files[:n_train]
        splits["val"] += files[n_train : n_train + n_val]
        splits["test"] += files[n_train + n_val :]
    return splits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to NEU-DET/ containing IMAGES/ and ANNOTATIONS/")
    parser.add_argument("--out", default="data", help="Output data/ root")
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    source = Path(args.source)
    images_dir = source / "IMAGES"
    ann_dir = source / "ANNOTATIONS"
    if not images_dir.is_dir() or not ann_dir.is_dir():
        raise SystemExit(f"Expected {images_dir} and {ann_dir} to exist")

    images = sorted(images_dir.glob("*.jpg")) + sorted(images_dir.glob("*.jpeg")) + sorted(images_dir.glob("*.png"))
    if not images:
        raise SystemExit(f"No images found in {images_dir}")

    splits = stratified_split(images, args.train_ratio, args.val_ratio, args.seed)

    out = Path(args.out)
    for split_name, files in splits.items():
        img_out = out / split_name / "images"
        lbl_out = out / split_name / "labels"
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)
        for img_path in files:
            xml_path = ann_dir / f"{img_path.stem}.xml"
            if not xml_path.exists():
                print(f"WARNING: no annotation for {img_path.name}, skipping")
                continue
            lines = parse_annotation(xml_path)
            shutil.copy2(img_path, img_out / img_path.name)
            (lbl_out / f"{img_path.stem}.txt").write_text("\n".join(lines))
        print(f"{split_name}: {len(files)} images")

    print(f"Done. YOLO dataset written under {out}/")


if __name__ == "__main__":
    main()
