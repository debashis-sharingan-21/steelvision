from fastapi import APIRouter, File, UploadFile

from backend.schemas.detection import ErrorResponse, HealthResponse, MetricsResponse, ModelInfoResponse, PredictResponse
from backend.services.inference_service import inference_service

router = APIRouter()

PREDICT_ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Empty or corrupt file"},
    413: {"model": ErrorResponse, "description": "File exceeds the 10 MB limit"},
    415: {"model": ErrorResponse, "description": "Unsupported content type (must be JPEG, PNG, or BMP)"},
    503: {"model": ErrorResponse, "description": "No model is currently loaded"},
}


@router.get("/health", response_model=HealthResponse, summary="Liveness and model-load status")
def health():
    return HealthResponse(status="ok" if inference_service.is_ready else "degraded", model_loaded=inference_service.is_ready)


@router.get("/model-info", response_model=ModelInfoResponse, summary="Architecture, classes, and whether this checkpoint used synthetic data")
def model_info():
    return ModelInfoResponse(**inference_service.model_info())


@router.get("/metrics", response_model=MetricsResponse, summary="Latest evaluation, benchmark, and error-analysis reports")
def metrics():
    return MetricsResponse(**inference_service.metrics())


@router.post(
    "/predict",
    response_model=PredictResponse,
    responses=PREDICT_ERROR_RESPONSES,
    summary="Run defect detection on an uploaded steel strip image",
)
async def predict(file: UploadFile = File(..., description="JPEG, PNG, or BMP image, up to 10 MB")):
    image = await inference_service.validate_and_load_image(file)
    result = inference_service.predict(image)
    return PredictResponse(**result)
