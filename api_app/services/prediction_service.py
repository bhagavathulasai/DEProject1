from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from api_app.config import settings
from fastapi import UploadFile
from werkzeug.utils import secure_filename


class PredictionStore:
    def __init__(self):
        self.records: dict[str, dict[str, Any]] = {}

    def add(self, record: dict[str, Any]) -> dict[str, Any]:
        self.records[record["prediction_id"]] = record
        return record

    def get(self, prediction_id: str) -> dict[str, Any] | None:
        return self.records.get(prediction_id)

    def list(self) -> list[dict[str, Any]]:
        return list(self.records.values())


class PredictionService:
    def __init__(self, model_service: Any, image_validation_service: Any):
        self.model_service = model_service
        self.image_validation_service = image_validation_service
        self.store = PredictionStore()

    def _save_uploaded_file(self, upload: UploadFile) -> tuple[str, Path]:
        if upload.filename is None or not upload.filename.strip():
            raise ValueError("No file uploaded.")

        filename = Path(upload.filename).name
        safe_name = secure_filename(filename)
        settings.upload_dir.mkdir(parents=True, exist_ok=True)

        prediction_id = str(uuid.uuid4())
        destination = settings.upload_dir / f"{prediction_id}_{safe_name}"
        contents = upload.file.read()
        if len(contents) > settings.max_upload_size_bytes:
            raise ValueError(
                f"Uploaded file exceeds the {settings.max_upload_size_mb} MB limit."
            )
        destination.write_bytes(contents)
        return prediction_id, destination

    def create_prediction(self, upload: UploadFile) -> dict[str, Any]:
        if upload.filename is None or not upload.filename.strip():
            raise ValueError("No file uploaded.")

        prediction_id, saved_path = self._save_uploaded_file(upload)

        self.image_validation_service.validate_file_extension(upload.filename)

        validation_result = self.image_validation_service.validate_image(saved_path)
        if not validation_result.get("is_teeth", False):
            raise ValueError(
                "Please upload an image containing visible teeth or oral structures."
            )

        if not self.model_service.is_loaded():
            raise RuntimeError(
                "The model is not available. Please configure a valid model "
                "artifact before inference."
            )

        prediction = self.model_service.predict(saved_path)
        label = prediction["label"]
        confidence = float(prediction["confidence_score"])

        record = {
            "prediction_id": prediction_id,
            "label": label,
            "confidence_score": confidence,
            "status": "completed",
            "created_at": datetime.now(UTC).isoformat(),
            "model_name": (
                self.model_service.model_path.name if self.model_service.model_path else "unknown"
            ),
            "validation_passed": bool(validation_result.get("is_teeth", False)),
            "file_name": upload.filename,
            "file_size_bytes": saved_path.stat().st_size,
            "metadata": {
                "probabilities": prediction.get("probabilities", []),
                "validation": validation_result,
            },
        }
        self.store.add(record)
        return record

    def get_prediction(self, prediction_id: str) -> dict[str, Any] | None:
        return self.store.get(prediction_id)

    def list_predictions(self) -> list[dict[str, Any]]:
        return self.store.list()
