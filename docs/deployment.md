# Deployment

## Local (Docker Compose)

```bash
cp .env.example .env
docker compose up --build
```

- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:3000

The backend container expects `models/best.pt` to exist on the host (bind-mounted in
`docker-compose.yml`) — train one first, see `models/README.md`. Without it, `/health`
reports `model_loaded: false` and `/predict` returns `503` rather than crashing.

## CPU vs GPU

The default images and `docker-compose.yml` run inference on CPU (`--device cpu` /
`device="cpu"` in `ml/inference/predict.py`'s default). For GPU:

1. Use an image with CUDA + matching torch build (`nvidia/cuda:12.x-runtime` base, or
   swap `pip install torch` for the CUDA wheel index in `docker/backend.Dockerfile`).
2. Add `deploy.resources.reservations.devices` (NVIDIA Container Toolkit) to the
   `backend` service in `docker-compose.yml`, or run with `docker run --gpus all`.
3. Set `STEELVISION_DEVICE=0` (or the relevant CUDA index) and pass it through to
   `DefectDetector(device=...)` — currently hardcoded to `"cpu"` in
   `backend/services/inference_service.py`; parameterize via env var when adding GPU
   support.

## Connecting a real industrial camera

Nothing in `backend/api/routes.py` assumes the image came from a browser upload. A
production line camera integration would look like:

```text
Line-scan / area-scan camera
        │  (GigE Vision / USB3 Vision / camera SDK)
        ▼
Frame-grabber process (small script or edge service)
        │  encode frame as JPEG/PNG
        ▼
POST http://<backend-host>:8000/predict  (multipart/form-data, field "file")
        │
        ▼
Same InferenceService / DefectDetector path used by the dashboard
```

Practical considerations for that jump (not implemented here — see Limitations):
- **Latency budget:** a real line needs sub-frame-interval inference; benchmark
  `models/metrics.json`'s `eval_wall_time_s` against your line speed and consider
  `yolov8n` → ONNX/TensorRT export if CPU inference isn't fast enough (see Future
  Improvements in the README).
- **Backpressure:** a queue (or simply dropping frames) between the frame grabber and
  the API so a slow inference cycle doesn't stall image capture.
- **Auth/network isolation:** the API has no auth layer today; a plant network
  deployment should sit behind a reverse proxy or VPN, not be exposed publicly.

## Environment variables

See `.env.example`. `STEELVISION_WEIGHTS` overrides the checkpoint path;
`STEELVISION_CORS_ORIGINS` overrides which frontend origin(s) may call the API.
