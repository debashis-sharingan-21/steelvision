# models/

Trained checkpoints and their evaluation reports are written here by
`ml/training/train.py` (`best.pt`, `metadata.json`), `ml/evaluation/evaluate.py`
(`metrics.json`), `ml/evaluation/benchmark.py` (`benchmark.json`), and
`ml/evaluation/error_analysis.py` (`error_analysis.json`). All git-ignored intentionally
— weights and generated reports don't belong in the repo; `backend`'s `GET /metrics`
serves their contents live instead.

To get a working `models/best.pt` locally:

```bash
# One command (real data — see data/README.md to get NEU-DET first):
python scripts/run_real_pipeline.py --epochs 100 --model yolov8n.pt --skip-download

# Or step by step, real data:
python -m ml.training.train --epochs 100 --name steelvision
python -m ml.evaluation.evaluate --weights models/best.pt --split test
python -m ml.evaluation.benchmark --weights models/best.pt
python -m ml.evaluation.error_analysis --weights models/best.pt --split test

# Fast path: smoke-test on synthetic data (works with no internet, ~minutes on CPU)
python -m ml.preprocessing.synthetic --out data --per-class 40
python -m ml.training.train --epochs 20 --name smoke_test --synthetic
python -m ml.evaluation.evaluate --weights models/best.pt --split test --synthetic
```

`metadata.json`'s `synthetic_data` field is what the API and frontend use to show the
"synthetic model" banner — don't hand-edit it. Pass `--synthetic` to `evaluate.py` /
`benchmark.py` / `error_analysis.py` too so their JSON output carries the same flag.

When switching a checkpoint out for a new one (e.g. synthetic → real), this project's
convention is to copy the outgoing `best.pt`/`metadata.json`/`metrics.json`/
`benchmark.json`/`error_analysis.json` to `*_synthetic.*` (or another descriptive
suffix) first, so the old, still-honestly-labeled results aren't just lost — see
`docs/model.md`'s "reference only" section for an example.
