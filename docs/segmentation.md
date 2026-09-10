# Segmentation module (Severstal) — experimental, scaffolded

> **Status: scaffolded, not trained, not wired into the API or dashboard.** Everything
> below is real, runnable code with passing unit tests, but there is no verified
> successful training run and no accuracy numbers — real or synthetic. Treat this as a
> foundation to build on, not a working feature.

## Why this exists

The detection pipeline (`ml/`, YOLOv8, NEU-DET) is the main, working part of this
project. Severstal Steel Defect Detection is a second, larger public dataset for the
same general problem, but framed as **pixel-level segmentation** (RLE-encoded masks)
rather than bounding boxes. Adding it as an optional module explores whether
SteelVision's architecture generalizes to a segmentation task without touching anything
in the working detection path.

## What's implemented

| File | Purpose |
|---|---|
| `ml/segmentation/rle.py` | Severstal's exact RLE format (1-indexed, column-major) — encode/decode, unit-tested round-trip |
| `ml/segmentation/mask_utils.py` | Binary mask → normalized YOLO-seg polygon conversion via `cv2.findContours` |
| `ml/segmentation/prepare_severstal.py` | Converts real Severstal `train.csv` + `train_images/` into a YOLO-seg dataset |
| `ml/segmentation/synthetic_seg.py` | Synthetic placeholder generator (same rationale as `ml/preprocessing/synthetic.py`) |
| `ml/segmentation/train_seg.py` / `predict_seg.py` | Training and inference wrappers around `ultralytics` YOLOv8n-seg |
| `ml/segmentation/configs/` | 4 class names (`defect_1..4`, Severstal never named them further) + dataset yaml |

All of the pure-logic pieces (RLE codec, mask→polygon, CSV parsing) have unit tests in
`tests/test_rle.py`, `tests/test_mask_utils.py`, `tests/test_prepare_severstal.py` — see
those pass with `pytest tests/test_rle.py tests/test_mask_utils.py tests/test_prepare_severstal.py`.

## What's *not* verified, and why

A smoke-training run (`ml/segmentation/train_seg.py --model yolov8n-seg.yaml` on
synthetic data, since the real Severstal dataset can't be downloaded here either — see
"Getting the real data" below) completed without crashing, but came back with **all
metrics at exactly 0.000** (box and mask precision/recall/mAP) after a short run, and
classification loss did not visibly decrease. Unlike the detection smoke test (which
converged cleanly to a real, reportable mAP@0.5 of 0.82 — see `docs/model.md`), this
result is inconclusive: it could be genuinely too little data/too few epochs for a
segmentation head trained from random initialization (no pretrained weights, since those
also require an internet download unavailable in this sandbox), or it could point to a
real issue in the label generation that hasn't been isolated yet.

**Because the cause isn't confirmed, no segmentation metric is reported anywhere in this
project** — not in this file, not in the README, not in `models/`. Reporting a number
without knowing whether it reflects the code or a bug would violate this project's own
"never fabricate results" rule as surely as inventing one would.

## Verifying / finishing this module (if you pick it up)

1. Confirm the label generation is correct: overfit a single synthetic image (`--epochs
   200 --imgsz 256` on a 1-2 image dataset) and check training loss actually drives
   toward zero and `mask_to_yolo_polygons` output visually matches the drawn defect
   (plot the polygon over the image).
2. If that overfit test also fails to converge, the bug is in
   `mask_utils.mask_to_yolo_polygons` or the label file format, not in "needs more
   data" — instrument `ml/segmentation/synthetic_seg.py` to dump the mask images
   alongside the polygons for visual inspection.
3. If overfitting one image works, scale back up with more synthetic data and epochs,
   or better, move straight to the real Severstal dataset (small models train faster
   with real signal than by throwing more synthetic epochs at a placeholder).

## Getting the real data

[Severstal Steel Defect Detection](https://www.kaggle.com/competitions/severstal-steel-defect-detection/data)
(Kaggle competition, requires accepting competition rules before download):

```bash
kaggle competitions download -c severstal-steel-defect-detection -p data/raw/severstal
unzip data/raw/severstal/severstal-steel-defect-detection.zip -d data/raw/severstal
python -m ml.segmentation.prepare_severstal --source data/raw/severstal --out data_seg
python -m ml.segmentation.train_seg --epochs 50 --name severstal
```

4 defect classes, 256×1600 px images, RLE-encoded masks — see
`ml/segmentation/configs/classes.py` and the competition page for exact licensing terms
before using the data beyond research/portfolio purposes.
