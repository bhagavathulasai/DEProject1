from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    prediction_id: str = Field(..., description="Unique prediction identifier.")
    label: str = Field(..., description="Predicted dental condition label.")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score for the predicted class."
    )
    status: str = Field(default="completed", description="Prediction lifecycle status.")
    created_at: str = Field(..., description="Timestamp for the prediction record.")
    model_name: str = Field(..., description="Model used for inference.")


class PredictionRecord(BaseModel):
    prediction_id: str
    label: str | None = None
    confidence_score: float | None = None
    status: str = "completed"
    created_at: str
    model_name: str
    validation_passed: bool | None = None
    file_name: str | None = None
    file_size_bytes: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str | None = None
    groq_configured: bool
    upload_dir: str
    api_version: str


class ModelInfo(BaseModel):
    name: str
    path: str | None = None
    status: str
