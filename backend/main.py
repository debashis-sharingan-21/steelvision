import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from backend.api.routes import router
from backend.services.inference_service import inference_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("steelvision")


@asynccontextmanager
async def lifespan(app: FastAPI):
    inference_service.load()
    if not inference_service.is_ready:
        logger.warning("Starting without a loaded model — /predict will return 503 until models/best.pt exists.")
    yield


app = FastAPI(
    title="SteelVision API",
    description="AI-powered stainless steel surface defect detection.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("STEELVISION_CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(router)
