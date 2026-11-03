from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_DIR = BASE_DIR / "Data set"
DEFAULT_MODEL_DIR = BASE_DIR / "models"
DEFAULT_OUTPUT_DIR = BASE_DIR / "artifacts"

DATASET_CLASS_MAPPING: dict[str, str] = {
    "Calculus": "Calculus",
    "Data caries": "Dental Caries",
    "Gingivitis": "Gingivitis",
    "hypodontia": "Hypodontia",
    "ulcer original dataset": "Mouth Ulcer",
}

DATASET_CLASS_LABELS: list[str] = list(DATASET_CLASS_MAPPING.values())
MODEL_LABELS = DATASET_CLASS_LABELS


@dataclass
class TrainingConfig:
    dataset_dir: Path = Path(os.getenv("DENTALVISION_DATASET_DIR", DEFAULT_DATASET_DIR))
    output_dir: Path = Path(os.getenv("DENTALVISION_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))
    model_dir: Path = Path(os.getenv("DENTALVISION_MODEL_DIR", DEFAULT_MODEL_DIR))
    image_size: tuple[int, int] = (128, 128)
    batch_size: int = 32
    epochs: int = 20
    validation_ratio: float = 0.2
    test_ratio: float = 0.2
    seed: int = 42
    learning_rate: float = 1e-3
    patience: int = 3
    use_augmentation: bool = True
    model_names: list[str] = field(
        default_factory=lambda: ["Improved_CNN", "MobileNet", "ResNet50", "EfficientNetB0"]
    )

    def __post_init__(self):
        self.dataset_dir = Path(self.dataset_dir)
        self.output_dir = Path(self.output_dir)
        self.model_dir = Path(self.model_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)

    @property
    def input_shape(self) -> tuple[int, int, int]:
        return (*self.image_size, 3)
