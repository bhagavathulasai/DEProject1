import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = Path(os.getenv("DENTALVISION_DATASET_DIR", BASE_DIR / "Data set"))
MODEL_DIR = Path(os.getenv("DENTALVISION_MODEL_DIR", BASE_DIR / "models"))

DATASET_CLASS_MAPPING = {
    "Calculus": "Calculus",
    "Data caries": "Dental Caries",
    "Gingivitis": "Gingivitis",
    "hypodontia": "Hypodontia",
    "ulcer original dataset": "Mouth Ulcer",
}


def resolve_model_path() -> Path | None:
    """Return the first valid model artifact from the allowed environment paths."""
    env_candidate = os.getenv("DENTALVISION_MODEL_PATH")
    candidates = []

    if env_candidate:
        candidates.append(Path(env_candidate))

    candidates.extend(
        [
            MODEL_DIR / "MobileNet_Model.h5",
            MODEL_DIR / "MobileNet_Model.keras",
            MODEL_DIR / "Improved_CNN_Model.h5",
            MODEL_DIR / "ResNet50_Model.h5",
            MODEL_DIR / "EfficientNet_Model.h5",
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def get_dataset_class_names() -> list[str]:
    """Return the canonical class labels used by the training pipeline."""
    if not DATASET_DIR.exists():
        return []

    names = []
    for child in sorted(DATASET_DIR.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir():
            names.append(DATASET_CLASS_MAPPING.get(child.name, child.name))
    return names
