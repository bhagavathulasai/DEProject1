from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf
from dentalvision.config import DATASET_CLASS_LABELS
from project_config import resolve_model_path

logger = logging.getLogger("dentalvision.api.model")


class ModelService:
    def __init__(self):
        self.model: tf.keras.Model | None = None
        self.model_path: Path | None = None

    def load(self) -> tf.keras.Model | None:
        candidate = resolve_model_path()
        if candidate is None:
            logger.warning(
                "No trained model artifact found. Set DENTALVISION_MODEL_PATH or "
                "add a model under the project models directory."
            )
            self.model = None
            self.model_path = None
            return None

        try:
            self.model = tf.keras.models.load_model(str(candidate))
            self.model_path = candidate
            logger.info("Loaded model from %s", candidate)
            return self.model
        except Exception:
            logger.exception("Failed to load model from %s", candidate)
            self.model = None
            self.model_path = candidate
            return None

    def is_loaded(self) -> bool:
        return self.model is not None

    def predict(self, image_file: str | Path) -> dict[str, float | str | list[float]]:
        if self.model is None:
            raise RuntimeError("Model is not available for inference.")

        image = cv2.imread(str(image_file), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Unable to read image file: {image_file}")

        image = cv2.resize(image, (128, 128))
        image = image.astype(np.float32) / 255.0
        image = np.expand_dims(image, axis=0)

        probabilities = self.model.predict(image, verbose=0)[0]
        predicted_index = int(np.argmax(probabilities))
        confidence = float(probabilities[predicted_index])
        label = (
            DATASET_CLASS_LABELS[predicted_index]
            if predicted_index < len(DATASET_CLASS_LABELS)
            else str(predicted_index)
        )

        return {
            "predicted_index": predicted_index,
            "label": label,
            "confidence_score": confidence,
            "probabilities": [float(item) for item in probabilities.tolist()],
        }

    def describe(self) -> dict[str, str | None]:
        return {
            "name": self.model_path.name if self.model_path else None,
            "path": str(self.model_path) if self.model_path else None,
            "status": "loaded" if self.model is not None else "missing",
        }
