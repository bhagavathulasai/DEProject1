from __future__ import annotations

import logging
from typing import Annotated, Any

from api_app.config import settings
from api_app.db.database import create_db_and_tables
from api_app.schemas import HealthResponse, ModelInfo, PredictionRecord, PredictionResponse
from api_app.services.image_validation_service import ImageValidationService
from api_app.services.model_service import ModelService
from api_app.services.prediction_service import PredictionService
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger("dentalvision.api")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="DentalVision AI private API for oral disease classification and image validation.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

model_service = ModelService()
image_validation_service = ImageValidationService()
prediction_service = PredictionService(
    model_service=model_service, image_validation_service=image_validation_service
)


@app.on_event("startup")
def startup_event() -> None:
    create_db_and_tables()
    app.state.model_service = model_service
    app.state.image_validation_service = image_validation_service
    app.state.prediction_service = prediction_service
    app.state.model = model_service.load()
    logger.info("DentalVision API startup complete. Model loaded: %s", bool(app.state.model))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled API error for %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )


@app.get(f"{settings.api_prefix}/health", response_model=HealthResponse, tags=["system"])
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "model_loaded": model_service.is_loaded(),
        "model_name": model_service.model_path.name if model_service.model_path else None,
        "groq_configured": image_validation_service.is_configured(),
        "upload_dir": str(settings.upload_dir),
        "api_version": settings.app_version,
    }


@app.post(
    f"{settings.api_prefix}/predictions",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["predictions"],
)
async def create_prediction(
    file: Annotated[UploadFile, File(description="Image file to classify.")],
) -> PredictionResponse:
    try:
        record = prediction_service.create_prediction(file)
        return PredictionResponse(
            prediction_id=record["prediction_id"],
            label=record["label"],
            confidence_score=float(record["confidence_score"]),
            status=record["status"],
            created_at=record["created_at"],
            model_name=record["model_name"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc


@app.get(
    f"{settings.api_prefix}/predictions/{{prediction_id}}",
    response_model=PredictionRecord,
    tags=["predictions"],
)
async def get_prediction(prediction_id: str) -> PredictionRecord:
    result = prediction_service.get_prediction(prediction_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found.")
    return PredictionRecord(**result)


@app.get(f"{settings.api_prefix}/predictions", tags=["predictions"])
async def list_predictions() -> dict[str, Any]:
    data = prediction_service.list_predictions()
    return {"count": len(data), "items": data}


@app.get(f"{settings.api_prefix}/models", response_model=list[ModelInfo], tags=["system"])
async def list_models() -> list[ModelInfo]:
    model_info = model_service.describe()
    return [
        ModelInfo(
            name=model_info["name"] if model_info["name"] else "unavailable",
            path=model_info["path"],
            status=model_info["status"],
        )
    ]
