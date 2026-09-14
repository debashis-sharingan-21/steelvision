````markdown
# SteelVision

**AI-powered surface defect detection for stainless steel strips** — a YOLOv8 detector behind a FastAPI backend and a Next.js inspection dashboard, built around the NEU-DET surface defect dataset.

[![CI](https://github.com/debashis-sharingan-21/steelvision/actions/workflows/ci.yml/badge.svg)](https://github.com/debashis-sharingan-21/steelvision/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-ff6f00)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## Overview

SteelVision is an AI-assisted visual inspection system for detecting and classifying surface defects on steel-strip images.

The system combines:

- YOLOv8-based defect detection
- FastAPI inference backend
- Next.js inspection dashboard
- Multi-frame inspection workflow
- Bounding-box visualization
- Defect confidence and severity information
- Model performance benchmarking
- Docker-based deployment
- Cloud deployment through Render

The project was built as a portfolio implementation for the **Jindal Stainless Engineering Case Study Competition 2026 — Problem Statement 1**.

---

## Problem

Manual visual inspection of steel strip surfaces can be:

- Slow
- Inconsistent between inspectors
- Difficult to scale
- Dependent on operator attention
- Challenging to integrate with continuous production lines

An automated inspection system should detect defects consistently and present the results in a form that an operator can quickly review.

---

## Solution

SteelVision follows a simple inspection pipeline:

```text
Steel Surface Image
        │
        ▼
Next.js Inspection Dashboard
        │
        ▼
FastAPI /predict
        │
        ▼
InferenceService
        │
        ▼
YOLOv8n Detector
        │
        ▼
Defect Detection
        │
        ├── Defect class
        ├── Confidence
        ├── Bounding box
        ├── Defect count
        ├── Severity score
        └── Inference latency
````

The same inference endpoint is used by the single-image and multi-frame inspection workflows.

---

## Features

### 1. Single Image Inspection

Upload a steel-surface image and receive:

* Defect / pass status
* Detected defect classes
* Confidence scores
* Bounding boxes
* Defect count
* Severity score
* Inference latency

### 2. Multi-Frame Sequence Inspection

SteelVision can process a sequence of steel-surface frames sequentially.

Users can:

* Upload multiple frames manually
* Start AI analysis
* Allow frames to be processed one after another
* Review completed results
* Navigate between frames using Previous / Next controls
* Use a frame slider
* Inspect the individual detection result for each frame

Results are stored as they become available, allowing completed frames to be reviewed without requiring the user to inspect the entire sequence as one image.

This workflow is designed as a practical bridge between single-image inspection and a future industrial camera pipeline.

**Current limitation:** inference is CPU-based and can have relatively high latency in the deployed environment. The interface therefore processes frames sequentially rather than blocking the entire inspection workflow.

### 3. Live Simulation

The application also includes a clearly labelled **Live Simulation** mode.

It cycles through selected NEU-DET images and repeatedly calls the same `/predict` endpoint.

> **Important:** this is a simulation, not a real industrial camera feed.

The production-camera integration path is documented separately in `docs/deployment.md`.

### 4. Model Benchmark

The dashboard includes a **Model Benchmark** section showing:

* Precision
* Recall
* F1 score
* mAP@0.5
* mAP@0.5:0.95
* Per-class AP
* Model performance information

Benchmark information is served through the backend API rather than being hard-coded into the frontend.

### 5. Six Defect Classes

The model detects six NEU-DET defect categories:

| Class           |
| --------------- |
| Crazing         |
| Inclusion       |
| Patches         |
| Pitted Surface  |
| Rolled-in Scale |
| Scratches       |

---

## Model

SteelVision uses **YOLOv8n** because of its relatively small size and suitability for CPU-oriented inference.

The current checkpoint was trained from random initialization using:

```text
yolov8n.yaml
```

rather than COCO-pretrained weights.

The model was trained on the real NEU-DET dataset.

### Verified test-set metrics

| Metric       |  Score |
| ------------ | -----: |
| Precision    | 0.6629 |
| Recall       | 0.5900 |
| F1           | 0.6243 |
| mAP@0.5      | 0.6765 |
| mAP@0.5:0.95 | 0.3447 |

The reported values are generated from the project's evaluation pipeline.

### Important model limitation

Crazing is currently the weakest class:

* AP@0.5 ≈ 0.2989
* Recall ≈ 0.0202

This means the current model misses a significant number of crazing defects.

Improving this would require additional training, better representation of the class, and potentially transfer learning or additional data.

---

## Dataset

SteelVision uses the **NEU-DET** hot-rolled steel strip surface defect dataset.

The dataset contains:

* 1,800 images
* 6 defect classes
* 200 × 200 pixel images
* Bounding-box annotations

The original annotations are provided in VOC-XML format and are converted into YOLO format by the preprocessing pipeline.

Dataset documentation:

```text
data/README.md
```

---

## Tech Stack

| Layer          | Technology                       |
| -------------- | -------------------------------- |
| Model          | YOLOv8n, Ultralytics, PyTorch    |
| Backend        | FastAPI, Pydantic, Uvicorn       |
| Frontend       | Next.js 16, React 19, TypeScript |
| Styling        | Tailwind CSS v4                  |
| Data           | NEU-DET, OpenCV, Pillow          |
| Testing        | pytest, httpx                    |
| Infrastructure | Docker, Docker Compose           |
| Deployment     | Render                           |
| Model Hosting  | GitHub Release                   |

---

## Architecture

```text
                         ┌─────────────────────────┐
                         │    Next.js Dashboard    │
                         └────────────┬────────────┘
                                      │
                     ┌────────────────┼────────────────┐
                     │                │                │
                     ▼                ▼                ▼
              Single Image      Multi-Frame       Live Simulation
               Inspection        Inspection
                     │                │                │
                     └────────────────┼────────────────┘
                                      │
                                      ▼
                             FastAPI /predict
                                      │
                                      ▼
                              InferenceService
                                      │
                                      ▼
                              DefectDetector
                                      │
                                      ▼
                                  YOLOv8n
                                      │
                                      ▼
                                  best.pt
```

---

## API

| Method | Endpoint      | Description                              |
| ------ | ------------- | ---------------------------------------- |
| GET    | `/health`     | Health status and model availability     |
| GET    | `/model-info` | Model architecture and class information |
| GET    | `/metrics`    | Model evaluation and benchmark metrics   |
| POST   | `/predict`    | Image upload and defect inference        |

### Example

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@frontend/public/samples/scratches.jpg"
```

### Example response

```json
{
  "status": "DEFECT DETECTED",
  "defect_count": 2,
  "detections": [
    {
      "class_name": "scratches",
      "confidence": 0.556,
      "bbox": {
        "x_min": 132.3,
        "y_min": 0.0,
        "x_max": 163.2,
        "y_max": 194.4
      }
    }
  ],
  "severity_score": 58.2,
  "inference_ms": 54.43,
  "image_width": 200,
  "image_height": 200,
  "model_name": "best",
  "synthetic_model": false
}
```

---

## Running Locally

### Backend

From the project root:

```bash
uvicorn backend.main:app --reload --port 8000
```

API:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard:

```text
http://localhost:3000
```

### Docker

The project contains Docker configurations for both frontend and backend.

Run:

```bash
docker compose up --build
```

---

## Deployment

SteelVision is deployed as two services.

### Frontend

```text
https://steelvision-yp4e.onrender.com
```

### Backend

```text
https://steelvision-backend.onrender.com
```

The frontend communicates with the deployed FastAPI backend through:

```text
NEXT_PUBLIC_API_URL
```

The model checkpoint is distributed through a GitHub Release and downloaded during the backend Docker build.

### Deployment Architecture

```text
                         Internet
                            │
                            ▼
                 ┌──────────────────────┐
                 │    Render Frontend   │
                 │       Next.js        │
                 └──────────┬───────────┘
                            │
                            │ HTTPS
                            ▼
                 ┌──────────────────────┐
                 │    Render Backend    │
                 │       FastAPI        │
                 └──────────┬───────────┘
                            │
                            ▼
                         YOLOv8n
                            │
                            ▼
                         best.pt
```

---

## Industrial Camera Direction

The current application accepts manually uploaded images and image sequences.

The architecture is intentionally built around the same `/predict` endpoint that a future industrial camera pipeline could use.

A future production setup could follow:

```text
Industrial Camera
       │
       ▼
Frame Acquisition
       │
       ▼
Frame Queue
       │
       ▼
Inference Worker
       │
       ▼
YOLOv8 Detection
       │
       ▼
Inspection Result
       │
       ▼
Operator Dashboard
```

Potential camera interfaces include:

* GigE Vision
* USB3 Vision
* Industrial area-scan cameras
* Industrial line-scan cameras

> The current project does not claim to have real camera integration.

---

## Multi-Frame Inspection

The multi-frame workflow is designed to handle sequences of inspection images without pretending that the current cloud deployment provides real-time industrial inference.

The workflow is:

```text
Multiple Frames
      │
      ▼
Frontend Frame Queue
      │
      ▼
Frame-by-frame /predict Requests
      │
      ▼
YOLOv8 Inference
      │
      ▼
Individual Detection Results
      │
      ▼
Review Completed Frames
```

Each frame is processed independently through the same inference API.

This approach is useful when inference latency is higher than the desired display rate because completed results can be reviewed without waiting for the entire sequence to finish.

The current implementation is therefore a practical software-level foundation for a future camera-based inspection pipeline.

---

## Performance Considerations

The current deployment performs inference on CPU.

This means latency can be significantly higher on cloud/free-tier infrastructure than on a local machine.

For this reason, the multi-frame inspection workflow processes frames sequentially and stores results individually.

The interface also exposes inference latency so that users can distinguish model processing time from the visual inspection workflow.

> ⚠️ **Performance notice:** The current deployment uses CPU inference and may experience high latency. Processing multiple frames can therefore take time. This version prioritizes reliable result generation and review over real-time production-line speed.

For real industrial deployment, the next optimization targets would include:

* ONNX export
* TensorRT
* GPU/edge inference
* Batch processing where appropriate
* Dedicated inference workers
* Frame queues
* Asynchronous job processing

---

## Limitations

### Dataset Domain

NEU-DET images were captured under relatively controlled conditions.

A real production line may introduce:

* Different lighting
* Different steel grades
* Different surface finishes
* Camera variation
* Motion blur
* Reflections
* Different defect appearances

Additional real production data would therefore be required before industrial deployment.

### Defect Classes

The current model only recognizes the six NEU-DET classes.

Unknown defect types may not be detected correctly.

### Model Performance

The current checkpoint is a portfolio/research implementation and should not be treated as a validated industrial inspection system.

### Crazing Detection

Crazing is currently the weakest model class, with AP@0.5 of approximately 0.2989 and recall of approximately 0.0202 on the test set.

### Severity Score

The displayed severity score is a project-specific heuristic and is not an industry-standard defect severity measurement.

### Camera Integration

The current project does not directly control or acquire frames from an industrial camera.

### CPU Inference

The current cloud deployment performs inference on CPU and can have substantially higher latency than a local machine or dedicated inference hardware.

---

## Future Improvements

The current architecture leaves a clear path toward a more production-oriented inspection system.

### Immediate Improvements

* GPU/edge inference
* ONNX/TensorRT optimization
* Better handling of long frame sequences
* Background job queue
* Improved progress reporting
* Automatic retry for failed frames

### Industrial Inspection Improvements

* GigE/USB3 Vision camera integration
* Line-scan camera support
* Multi-camera inspection
* Frame synchronization
* Defect tracking across consecutive frames
* Production-line monitoring
* PLC integration
* Reject-gate signaling

### ML Improvements

* Transfer learning from pretrained YOLO weights
* More training data
* Improved crazing detection
* Data augmentation
* Hard-negative mining
* Continuous learning from operator corrections
* Defect tracking and temporal analysis

---

## Experimental Segmentation Module

The repository also contains an optional Severstal steel-defect segmentation module.

Location:

```text
ml/segmentation/
```

This module is separate from the primary NEU-DET detection pipeline and is not used by the deployed detection dashboard.

It is currently experimental and should not be considered part of the verified production path of SteelVision.

---

## Reproducibility

Evaluation metrics are generated by the project's evaluation scripts rather than manually entered into the application.

Relevant scripts include:

```bash
python -m ml.evaluation.evaluate --weights models/best.pt --split test

python -m ml.evaluation.benchmark --weights models/best.pt

python -m ml.evaluation.error_analysis --weights models/best.pt --split test
```

The resulting metrics are stored in the project's model artifacts and exposed to the dashboard through the backend API.

The current model was trained from random initialization using `yolov8n.yaml` rather than COCO-pretrained weights.

---

## Project Status

**Current status: Working prototype / portfolio project**

### Completed

* NEU-DET preprocessing pipeline
* YOLOv8 defect detection model
* FastAPI inference backend
* Next.js inspection dashboard
* Single-image inspection
* Multi-frame sequence inspection
* Frame-by-frame result navigation
* Model benchmark dashboard
* Docker deployment
* Render deployment
* API health monitoring
* Model metadata reporting
* Real trained checkpoint
* Evaluation and error-analysis pipeline

### In Progress / Future

* GPU-accelerated inference
* Industrial camera integration
* Asynchronous production inference queue
* ONNX/TensorRT optimization
* Multi-camera inspection
* PLC/reject-gate integration
* Improved model performance

---

## Repository Structure

```text
steelvision/

├── frontend/
│   └── Next.js inspection dashboard
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── schemas/
│   └── main.py
│
├── ml/
│   ├── training/
│   ├── inference/
│   ├── preprocessing/
│   ├── evaluation/
│   ├── configs/
│   └── segmentation/
│
├── data/
│   └── dataset documentation
│
├── models/
│   └── model and evaluation artifacts
│
├── scripts/
│
├── tests/
│
├── docs/
│   ├── architecture.md
│   ├── model.md
│   ├── deployment.md
│   └── segmentation.md
│
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── docker-compose.yml
└── LICENSE
```

---

## Author

**Debashis Mohapatra**

B.Tech Electrical Engineering
National Institute of Technology, Rourkela

---

## License

MIT — see [LICENSE](LICENSE).

````

