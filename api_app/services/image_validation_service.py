from __future__ import annotations

import os
from pathlib import Path

from another import analyze_image, is_groq_configured


class ImageValidationService:
    def __init__(self):
        self.allowed_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

    def validate_file_extension(self, filename: str) -> None:
        suffix = Path(filename).suffix.lower()
        if suffix not in self.allowed_extensions:
            raise ValueError(
                "Unsupported file type. Please upload a JPG, JPEG, PNG, BMP, or WEBP image."
            )

    def validate_image(self, image_path: str | os.PathLike[str]) -> dict:
        if not is_groq_configured():
            raise RuntimeError(
                "Image validation is unavailable because GROQ_API_KEY is not configured."
            )

        result = analyze_image(str(image_path))
        if not isinstance(result, dict):
            raise RuntimeError("Image validation returned an invalid response.")
        return result

    def is_configured(self) -> bool:
        return is_groq_configured()
