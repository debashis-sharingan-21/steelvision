# Dataset — NEU-DET Steel Surface Defect Detection

SteelVision is built around the **NEU-DET** (Northeastern University Surface Defect
Detection) dataset — hot-rolled steel strip images with bounding-box annotations for
six defect classes.

## Source

- Original dataset: Northeastern University (NEU) surface defect database, introduced in
  Song & Yan, *"A Noise Robust Method Based on Completed Local Binary Patterns for Hot-Rolled
  Steel Strip Surface Defects"* (2013), and later re-released with detection (bounding box)
  annotations as **NEU-DET**.
- One known Kaggle mirror (flat `IMAGES/`/`ANNOTATIONS/` layout):
  [`danielfinez/neu-det-steel-surface-defect-detection-dataset`](https://www.kaggle.com/datasets/danielfinez/neu-det-steel-surface-defect-detection-dataset)
- Also indexed at [IEEE DataPort](https://ieee-dataport.org/documents/neu-det).
- The copy actually used in this repo (see "Getting the data") was downloaded manually
  from Kaggle by the project owner, not fetched by this codebase, in a different but
  equally common mirror layout: `NEU-DET/{train,validation}/images/<class>/*.jpg` +
  `NEU-DET/{train,validation}/annotations/*.xml`. Both mirrors carry the exact same 1,800
  images, classes, and VOC-XML annotation schema — see "Verified" below.

## Classes (6)

| Class | Abbreviation |
|---|---|
| crazing | Cr |
| inclusion | In |
| patches | Pa |
| pitted_surface | PS |
| rolled-in_scale | RS |
| scratches | Sc |

## Size and format

- 1800 grayscale images total, 300 per class, 200×200 px.
- Conventional split: 1440 train / 360 test (this project further splits train into
  train/val — see `ml/preprocessing/prepare_dataset.py`).
- Annotations are Pascal VOC XML (`ANNOTATIONS/`) matched to `IMAGES/`.

## Licensing / usage

NEU-DET is a widely used **academic research** dataset, freely redistributed on Kaggle
and IEEE DataPort for research/educational use. It is **not** included in this repository
— see "Getting the data" below. If you plan to use it beyond research/portfolio purposes,
verify current licensing terms on the source pages above.

## Getting the data

This sandbox this project was built in has no outbound access to Kaggle/GitHub, so
`scripts/download_neu_det.py` can't run inside it. The real dataset in this repo's
`data/raw/NEU-DET/` was downloaded manually (Kaggle, outside this sandbox) and copied
in. If you're starting fresh with internet + Kaggle API credentials
(`~/.kaggle/kaggle.json`):

```bash
python scripts/download_neu_det.py --out data/raw   # expects the flat IMAGES/ANNOTATIONS mirror
```

If your download instead uses the nested `{train,validation}/images/<class>/` +
`{train,validation}/annotations/` layout (as this repo's own copy did), flatten it first:

```bash
mkdir -p data/raw/NEU-DET/IMAGES data/raw/NEU-DET/ANNOTATIONS
cp <extracted>/NEU-DET/{train,validation}/images/*/*.jpg data/raw/NEU-DET/IMAGES/
cp <extracted>/NEU-DET/{train,validation}/annotations/*.xml data/raw/NEU-DET/ANNOTATIONS/
```

Either way you should end up with exactly 1,800 files in each of `IMAGES/` and
`ANNOTATIONS/` (`ls data/raw/NEU-DET/IMAGES | wc -l`) before the next step. Then build
the YOLO-format dataset — this project's own stratified 70/15/15 split, regardless of
how the source mirror organized train/val:

```bash
python -m ml.preprocessing.prepare_dataset --source data/raw/NEU-DET --out data
```

This produces:

```text
data/
├── raw/NEU-DET/{IMAGES,ANNOTATIONS}/   # untouched original data (git-ignored)
├── train/{images,labels}/              # 1,260 images, stratified per class, seed 42
├── val/{images,labels}/                # 270 images
└── test/{images,labels}/               # 270 images
```

Or use `python scripts/run_real_pipeline.py --skip-download` to run this conversion and
the full train/evaluate/benchmark chain in one command (see `docs/model.md`).

## Synthetic fallback

For environments without access to the real dataset (like this sandbox before the real
data was manually added), `ml/preprocessing/synthetic.py` generates a small
**synthetic placeholder set** (procedurally drawn blobs/lines on gray backgrounds,
labeled with the same 6 class names) so the rest of the pipeline can still be exercised
end-to-end. Synthetic data and any metrics produced from it are clearly labeled as such
throughout this repo (`synthetic_data: true` in every JSON report) and **must not be
read as real model performance**. See [`docs/model.md`](../docs/model.md).
