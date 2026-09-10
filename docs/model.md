# Model

## Architecture

**YOLOv8n** (Ultralytics), a single-stage anchor-free object detector.

Why YOLOv8n over alternatives:
- The task is bounding-box detection with a small number of classes (6) on small
  (200×200) images — a lightweight one-stage detector is a good fit; two-stage detectors
  (Faster R-CNN) add latency the problem statement's "production-line inference speed"
  requirement doesn't need.
- Ultralytics' YOLOv8 ships training, validation, export, and inference in one
  well-maintained package, which matters for a portfolio project that has to stay
  reproducible without a bespoke training loop.
- `yolov8n` (nano) is the smallest variant — appropriate given this project targets CPU
  inference by default; `yolov8s`/`m` are drop-in upgrades (`--model yolov8s.pt`) if more
  accuracy is needed and GPU time is available.

## Input / output

- **Input:** RGB image, any size (YOLO letterboxes internally); dataset images are
  200×200 to match NEU-DET's native resolution.
- **Output per image:** zero or more detections, each with `class_name`, `confidence`
  (0-1), and `bbox` (`x_min, y_min, x_max, y_max` in source-image pixels).

## Training process

`ml/training/train.py` wraps `ultralytics.YOLO(...).train(...)` against
`ml/configs/data.yaml`. It defaults to starting from the COCO-pretrained `yolov8n.pt`
checkpoint (transfer learning), which needs internet access to Ultralytics' asset
servers; pass `--model yolov8n.yaml` to train from random initialization instead when
that access isn't available (that's what this project's own `models/best.pt` used — see
"Reported results" below).

```bash
python -m ml.training.train --epochs 100 --imgsz 200 --batch 16 --device cpu --name steelvision
```

Use `--device 0` (or whatever CUDA index) if a GPU is available — the flag passes
straight through to Ultralytics.

## Evaluation metrics

`ml/evaluation/evaluate.py` runs Ultralytics' own validation loop against the held-out
`test` split and writes precision, recall, F1, mAP@0.5, mAP@0.5:0.95, per-class AP@0.5,
and inference wall time to `models/metrics.json`. `ml/evaluation/benchmark.py` separately
times real inference calls for latency/FPS, and `ml/evaluation/error_analysis.py`
independently re-derives per-class precision/recall via IoU matching and lists the
worst-performing images. **Only** real numbers from actual runs of these three scripts
ever land in `models/*.json` or in this document — nothing here is hand-typed.

### Reported results — real NEU-DET

The real [NEU-DET dataset](../data/README.md) (1,800 images, verified counts: 300/class)
was obtained outside this sandbox and copied into `data/raw/NEU-DET/`, then converted
with the unmodified `ml/preprocessing/prepare_dataset.py` (1,260 train / 270 val / 270
test, stratified 70/15/15 per class, seed 42). Training used `yolov8n.yaml` (random
init, not COCO-pretrained — see the caveat above and in the README's Limitations).

```bash
python -m ml.training.train --model yolov8n.yaml --epochs 50 --imgsz 200 --batch 16 --device cpu --name steelvision_real
python -m ml.evaluation.evaluate --weights models/best.pt --split test
python -m ml.evaluation.benchmark --weights models/best.pt
python -m ml.evaluation.error_analysis --weights models/best.pt --split test
```

Training ran 50 epochs on an Intel Core i7-5500U (CPU only). It was interrupted once at
epoch 12 by an unrelated environment restart and resumed from Ultralytics' own
`last.pt` checkpoint via `python -m ml.training.train --name steelvision_real --resume`
(see `ml/training/train.py`'s `--resume` flag) — training continued from exactly where
it left off, not from scratch.

| Metric | Value | Data |
|---|---|---|
| Precision | 0.6629 | real |
| Recall | 0.5900 | real |
| F1 | 0.6243 | real |
| mAP@0.5 | 0.6765 | real |
| mAP@0.5:0.95 | 0.3447 | real |
| Mean inference latency (CPU, i7-5500U) | 63.35 ms/image | real |
| Median / P95 latency | 56.07 ms / 70.29 ms | real |
| Throughput | 15.79 FPS | real |

Per-class AP@0.5 (real NEU-DET test split, 270 images / 628 defect instances):

| Class | AP@0.5 |
|---|---|
| crazing | 0.2989 (weakest class — see below) |
| inclusion | 0.7587 |
| patches | 0.8704 |
| pitted_surface | 0.7833 |
| rolled-in_scale | 0.4729 |
| scratches | 0.8750 |

Independent error-analysis cross-check (IoU ≥ 0.5 greedy matching at the model's default
0.25 confidence threshold, real test split): per-class precision/recall from
`error_analysis.py` (`models/error_analysis.json`) line up with the pattern above —
**`crazing` recall is only 0.020** (2 of 99 true crazing instances matched; 97 false
negatives), by far the weakest class, while `scratches` (0.882 recall) and `patches`
(0.854 recall) perform best. 186 of 270 test images had at least one FP or FN.

**Honest read:** this is a real, unfabricated result for a YOLOv8n trained from random
initialization (no COCO pretraining) for only 50 epochs on 1,260 images, evaluated on a
real held-out test set. `crazing`'s near-total miss rate is the standout weakness and the
most likely first thing to fix — plausible causes to investigate: crazing's
fine-grained, low-contrast texture pattern may need more epochs, a higher input
resolution, or targeted augmentation to learn from scratch; transfer learning from
`yolov8n.pt` (blocked here by no internet access) would likely help across all classes,
crazing probably most of all. The benchmark numbers were measured while the dev
frontend/backend servers were also running on the same machine (unlike the synthetic
benchmark's idle-machine numbers below), so treat the P95/max as somewhat pessimistic
versus a dedicated inference host.

### Reported results — synthetic smoke test (reference only)

> Kept for reference: this is what the pipeline produced on
> `ml/preprocessing/synthetic.py`'s procedurally generated placeholder images (240 train
> / 48 val / 48 test, 40 per class) before the real dataset was available, proving the
> training → evaluation → `models/metrics.json` pipeline runs end-to-end on real code
> paths. It says nothing about real-world defect-detection accuracy — the "defects" are
> drawn shapes, not real steel imagery. The synthetic checkpoint and its metrics are
> preserved as `models/*_synthetic.*` (git-ignored, like all `models/` artifacts).

| Metric | Value | Data |
|---|---|---|
| Precision | 0.846 | synthetic |
| Recall | 0.703 | synthetic |
| F1 | 0.768 | synthetic |
| mAP@0.5 | 0.823 | synthetic |
| mAP@0.5:0.95 | 0.472 | synthetic |
| Inference latency (CPU, i7-5500U) | 24.2 ms/image (39.4 ms mean end-to-end via the API) | synthetic |
| Throughput | 25.4 FPS (end-to-end via the API) | synthetic |

Per-class AP@0.5 (synthetic test split, 8 images/class):

| Class | AP@0.5 |
|---|---|
| crazing | 0.586 |
| inclusion | 0.947 |
| patches | 0.952 |
| pitted_surface | 0.696 |
| rolled-in_scale | 0.995 |
| scratches | 0.761 |

Independent error-analysis cross-check (IoU ≥ 0.5 greedy matching, synthetic test split):
precision/recall per class came out close to but not identical to Ultralytics' own
mAP-derived numbers above (e.g. `pitted_surface` precision 0.455 / recall 0.556 from
`error_analysis.py` vs. AP@0.5 0.696 from `evaluate.py`) — expected, since one is a
fixed-confidence-threshold count and the other integrates over the full
precision-recall curve. Full breakdown: `models/error_analysis_synthetic.json`.

Full machine-readable output: `models/metrics.json`, `models/benchmark.json`,
`models/error_analysis.json` (git-ignored, regenerate with the commands above).

## Severity score

`ml/inference/predict.py::compute_severity` combines three measurable signals into a
0-100 score:

```text
score = 100 * (0.5 * avg_confidence + 0.3 * min(total_defect_area_fraction * 10, 1) + 0.2 * min(defect_count / 5, 1))
```

This is a **demo heuristic invented for this project**, not an industry-standard
severity measurement. It is a reasonable, explainable ranking signal (more/bigger/more-
confident defects score higher) but has not been validated against real inspection
outcomes or a domain expert's severity rubric. Treat it as illustrative only.

## Checkpoint management

- `ml/training/train.py` copies Ultralytics' `best.pt` (chosen by validation mAP during
  training) to `models/best.pt`, and writes `models/metadata.json` recording the base
  checkpoint, epochs, device, and whether synthetic data was used.
- `backend/services/inference_service.py` reads `models/metadata.json` at startup so the
  API and frontend can honestly display `synthetic_model: true/false` alongside every
  prediction — this flag is what stops a synthetic-data checkpoint from silently being
  presented as a real one.

## Plugging in the real dataset

One command runs the whole thing (download if you have Kaggle credentials, or point it
at a manually-downloaded `data/raw/NEU-DET/` with `--skip-download`):

```bash
python scripts/run_real_pipeline.py --epochs 100 --model yolov8n.pt
python scripts/run_real_pipeline.py --epochs 100 --model yolov8n.yaml --skip-download  # no pretrained-weights access
```

Or run each step yourself:

```bash
python scripts/download_neu_det.py          # Kaggle API, run where you have credentials + internet
python -m ml.preprocessing.prepare_dataset --source data/raw/NEU-DET --out data
python -m ml.training.train --epochs 100 --name steelvision
python -m ml.evaluation.evaluate --weights models/best.pt --split test
python -m ml.evaluation.benchmark --weights models/best.pt
python -m ml.evaluation.error_analysis --weights models/best.pt --split test
```
