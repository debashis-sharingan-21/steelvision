"""API tests. The real model is not exercised here (no network/GPU available in CI) --
inference_service.detector is monkeypatched with a deterministic fake so these tests
check the API contract (status codes, schema, validation) independent of model weights.
"""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

import backend.services.inference_service as inference_service_module
from backend.main import app
from backend.services.inference_service import inference_service
from ml.inference.predict import Detection, InspectionResult


class FakeDetector:
    class_names = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]

    def predict(self, image):
        w, h = image.size
        detections = [Detection(class_name="scratches", confidence=0.91, bbox=(10, 10, 50, 40))]
        return InspectionResult(
            detections=detections,
            defect_count=len(detections),
            status="DEFECT DETECTED",
            inference_ms=12.3,
            severity_score=42.0,
            image_width=w,
            image_height=h,
            model_name="fake",
        )


@pytest.fixture
def client(monkeypatch):
    # The app's startup event calls inference_service.load(), which would try to load
    # real weights and stomp our fake detector — no-op it for these API-contract tests.
    monkeypatch.setattr(inference_service, "load", lambda: None)
    inference_service.detector = FakeDetector()
    inference_service.metadata = {"synthetic_data": True, "base_model": "yolov8n.pt", "device": "cpu"}
    inference_service.load_error = None
    with TestClient(app) as c:
        yield c
    inference_service.detector = None


def _jpeg_bytes(size=(64, 64), color=(120, 120, 120)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="JPEG")
    return buf.getvalue()


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_health_degraded_when_model_missing(client):
    inference_service.detector = None
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "degraded", "model_loaded": False}


def test_model_info(client):
    r = client.get("/model-info")
    assert r.status_code == 200
    body = r.json()
    assert body["classes"] == FakeDetector.class_names
    assert body["synthetic_model"] is True


def test_predict_success(client):
    files = {"file": ("sample.jpg", _jpeg_bytes(), "image/jpeg")}
    r = client.post("/predict", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "DEFECT DETECTED"
    assert body["defect_count"] == 1
    assert body["detections"][0]["class_name"] == "scratches"
    assert 0.0 <= body["detections"][0]["confidence"] <= 1.0
    assert body["synthetic_model"] is True


def test_predict_rejects_unsupported_content_type(client):
    files = {"file": ("sample.txt", b"not an image", "text/plain")}
    r = client.post("/predict", files=files)
    assert r.status_code == 415


def test_predict_rejects_corrupt_image(client):
    files = {"file": ("sample.jpg", b"\xff\xd8\xff\xff\x00\x01garbage", "image/jpeg")}
    r = client.post("/predict", files=files)
    assert r.status_code == 400


def test_predict_returns_503_without_model(client):
    inference_service.detector = None
    files = {"file": ("sample.jpg", _jpeg_bytes(), "image/jpeg")}
    r = client.post("/predict", files=files)
    assert r.status_code == 503


def test_metrics_returns_null_fields_when_no_reports_exist(client, monkeypatch, tmp_path):
    monkeypatch.setattr(inference_service_module, "METRICS_PATH", tmp_path / "metrics.json")
    monkeypatch.setattr(inference_service_module, "BENCHMARK_PATH", tmp_path / "benchmark.json")
    monkeypatch.setattr(inference_service_module, "ERROR_ANALYSIS_PATH", tmp_path / "error_analysis.json")

    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.json() == {"evaluation": None, "benchmark": None, "error_analysis": None}


def test_metrics_returns_file_contents_when_present(client, monkeypatch, tmp_path):
    metrics_path = tmp_path / "metrics.json"
    metrics_path.write_text('{"map50": 0.82}')
    monkeypatch.setattr(inference_service_module, "METRICS_PATH", metrics_path)
    monkeypatch.setattr(inference_service_module, "BENCHMARK_PATH", tmp_path / "missing_benchmark.json")
    monkeypatch.setattr(inference_service_module, "ERROR_ANALYSIS_PATH", tmp_path / "missing_errors.json")

    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.json()
    assert body["evaluation"] == {"map50": 0.82}
    assert body["benchmark"] is None
    assert body["error_analysis"] is None
