from __future__ import annotations

import os
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit

from .config import DATASET_CLASS_MAPPING


def list_dataset_classes(dataset_dir: str | os.PathLike[str]) -> list[str]:
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_path}")

    class_dirs = sorted(
        [p for p in dataset_path.iterdir() if p.is_dir()],
        key=lambda p: p.name.lower(),
    )
    return [p.name for p in class_dirs]


def normalize_class_name(folder_name: str) -> str:
    folder_name = folder_name.strip()
    if folder_name in DATASET_CLASS_MAPPING:
        return DATASET_CLASS_MAPPING[folder_name]
    return folder_name


def load_image_dataset(
    dataset_dir: str | os.PathLike[str],
    image_size: tuple[int, int] = (128, 128),
    limit_per_class: int | None = None,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    dataset_path = Path(dataset_dir)
    class_dirs = list_dataset_classes(dataset_path)
    if not class_dirs:
        raise ValueError(f"No valid class folders found in {dataset_path}")

    images: list[np.ndarray] = []
    labels: list[int] = []
    ordered_names: list[str] = []

    for class_index, folder_name in enumerate(class_dirs):
        canonical_name = normalize_class_name(folder_name)
        folder_path = dataset_path / folder_name
        image_files = sorted(
            [
                p
                for p in folder_path.iterdir()
                if p.is_file() and p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}
            ],
            key=lambda p: p.name.lower(),
        )

        if limit_per_class is not None:
            image_files = image_files[:limit_per_class]

        if not image_files:
            continue

        ordered_names.append(canonical_name)

        for image_file in image_files:
            image = cv2.imread(str(image_file), cv2.IMREAD_COLOR)
            if image is None:
                continue
            image = cv2.resize(image, image_size)
            image = image.astype(np.float32) / 255.0
            images.append(image)
            labels.append(class_index)

    if not images:
        raise ValueError(f"No valid images were loaded from {dataset_path}")

    return np.array(images, dtype=np.float32), np.array(labels, dtype=np.int32), ordered_names


def stratified_split_data(
    x: np.ndarray,
    y: np.ndarray,
    test_ratio: float,
    validation_ratio: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if not 0 < test_ratio < 1:
        raise ValueError("test_ratio must be between 0 and 1")
    if not 0 < validation_ratio < 1:
        raise ValueError("validation_ratio must be between 0 and 1")

    unique_classes = np.unique(y)
    if len(unique_classes) < 2:
        raise ValueError("At least two classes are required to perform stratified splitting.")

    min_required_total = len(unique_classes) * 3
    if len(y) < min_required_total:
        raise ValueError(
            f"Not enough samples for a stable train/validation/test split: "
            f"{len(y)} samples across {len(unique_classes)} classes. Use a larger "
            "dataset or a smaller limit-per-class for smoke tests."
        )

    class_counts = np.bincount(y)
    if np.min(class_counts[class_counts > 0]) < 3:
        raise ValueError(
            "Each class must contain at least 3 samples to support a valid "
            "stratified train/validation/test split. Lower the limit-per-class "
            "or use a larger dataset."
        )

    if len(y) * test_ratio < len(unique_classes):
        raise ValueError(
            f"The requested test ratio ({test_ratio}) is too small to retain all "
            f"classes in the test split for {len(unique_classes)} classes. "
            "Increase the sample count or use a larger test ratio."
        )

    if len(y) * validation_ratio < len(unique_classes):
        raise ValueError(
            f"The requested validation ratio ({validation_ratio}) is too small to "
            f"retain all classes in the validation split for {len(unique_classes)} "
            "classes. Increase the sample count or use a larger validation ratio."
        )

    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_ratio, random_state=seed)
    train_index, test_index = next(sss.split(x, y))
    x_train, x_test = x[train_index], x[test_index]
    y_train, y_test = y[train_index], y[test_index]

    sss_val = StratifiedShuffleSplit(n_splits=1, test_size=validation_ratio, random_state=seed)
    val_train_index, val_index = next(sss_val.split(x_train, y_train))
    x_train_final, x_validation = x_train[val_train_index], x_train[val_index]
    y_train_final, y_validation = y_train[val_train_index], y_train[val_index]

    return x_train_final, y_train_final, x_validation, y_validation, x_test, y_test


def compute_class_distribution(y: np.ndarray, class_names: list[str]) -> dict[str, int]:
    counts = Counter(int(i) for i in y)
    return {class_names[index]: counts.get(index, 0) for index in range(len(class_names))}


def dataset_summary(
    dataset_dir: str | os.PathLike[str], class_names: list[str] | None = None
) -> dict[str, int]:
    dataset_path = Path(dataset_dir)
    summaries: dict[str, int] = {}

    class_dirs = sorted(dataset_path.iterdir(), key=lambda p: p.name.lower())
    for index, class_dir in enumerate(class_dirs):
        if not class_dir.is_dir():
            continue
        count = sum(
            1
            for p in class_dir.iterdir()
            if p.is_file() and p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}
        )
        key = class_names[index] if class_names and index < len(class_names) else class_dir.name
        summaries[key] = count
    return summaries
