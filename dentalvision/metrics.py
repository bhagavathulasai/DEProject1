from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)


def compute_confusion_matrix(
    y_true: np.ndarray, y_pred: np.ndarray, labels: list[int]
) -> np.ndarray:
    return confusion_matrix(y_true, y_pred, labels=labels)


def compute_classification_report(
    y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str]
) -> dict[str, object]:
    report = classification_report(
        y_true,
        y_pred,
        labels=list(range(len(class_names))),
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )
    return report


def compute_precision_recall_f1(
    y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str]
) -> dict[str, dict[str, float]]:
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(range(len(class_names))),
        zero_division=0,
    )
    results: dict[str, dict[str, float]] = {}
    for idx, name in enumerate(class_names):
        results[name] = {
            "precision": float(precision[idx]),
            "recall": float(recall[idx]),
            "f1_score": float(f1[idx]),
            "support": int(support[idx]),
        }
    return results


def estimate_expected_calibration_error(
    y_true: np.ndarray, probs: np.ndarray, labels: list[int], bins: int = 10
) -> float:
    if probs.shape[0] != y_true.shape[0]:
        raise ValueError("Probability matrix and labels must have the same number of rows.")

    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == y_true).astype(np.float32)

    bin_boundaries = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    total = len(y_true)

    for index in range(bins):
        left, right = bin_boundaries[index], bin_boundaries[index + 1]
        mask = (confidences >= left) & (confidences < right)
        if index == bins - 1:
            mask = (confidences >= left) & (confidences <= right)
        if not np.any(mask):
            continue
        avg_conf = float(np.mean(confidences[mask]))
        avg_acc = float(np.mean(accuracies[mask]))
        ece += (np.sum(mask) / total) * abs(avg_conf - avg_acc)
    return float(ece)


def rejection_decision(
    probabilities: np.ndarray,
    confidence_threshold: float = 0.9,
    entropy_threshold: float = 1.2,
    margin: float = 0.2,
) -> bool:
    probabilities = np.asarray(probabilities, dtype=np.float32)
    confidence = float(np.max(probabilities))
    entropy = -np.sum(probabilities * np.log(probabilities + 1e-10))
    sorted_probs = np.sort(probabilities)
    second_highest = float(sorted_probs[-2]) if len(sorted_probs) > 1 else 0.0
    accepted = (
        confidence >= confidence_threshold
        and entropy < entropy_threshold
        and (confidence - second_highest) > margin
    )
    return accepted


def measure_inference_latency(model: tf.keras.Model, x: np.ndarray, runs: int = 20) -> float:
    timings = []
    for _ in range(runs):
        start = tf.timestamp()
        _ = model.predict(x, verbose=0)
        stop = tf.timestamp()
        timings.append(float(stop - start))
    return float(np.mean(timings))


def get_model_size_mb(model_path: str | Path) -> float:
    path = Path(model_path)
    if not path.exists():
        return 0.0
    return path.stat().st_size / (1024 * 1024)


def save_json(data: dict[str, object], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)


def generate_gradcam(
    model: tf.keras.Model,
    image: np.ndarray,
    class_index: int | None = None,
    last_conv_layer_name: str | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate a Grad-CAM heatmap and overlay for an image.

    This is an interpretability aid only. It highlights regions that increased
    the activation of the selected class, but it does not prove disease
    causality or medical diagnosis.
    """
    image = np.asarray(image).astype(np.float32)
    if image.ndim == 3:
        image = np.expand_dims(image, axis=0)

    _ = model(image, training=False)

    if last_conv_layer_name is None:
        conv_layers = [layer.name for layer in model.layers if "conv" in layer.name.lower()]
        if conv_layers:
            last_conv_layer_name = conv_layers[-1]
        elif len(model.layers) >= 2:
            last_conv_layer_name = model.layers[-2].name
        else:
            raise ValueError("Model does not expose a usable convolutional layer for Grad-CAM.")

    conv_layer = model.get_layer(last_conv_layer_name)
    output_layer = model.layers[-1]
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[conv_layer.output, output_layer.output],
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image, training=False)
        if class_index is None:
            class_index = int(tf.argmax(predictions[0]))
        class_loss = predictions[:, class_index]

    grads = tape.gradient(class_loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    heatmap = tf.reduce_mean(tf.cast(conv_outputs, tf.float32) * pooled_grads, axis=-1)
    heatmap = tf.maximum(heatmap, 0.0)
    heatmap = heatmap / (tf.reduce_max(heatmap) + 1e-8)
    heatmap_array = heatmap[0].numpy()

    heatmap_array = cv2.resize(heatmap_array, (image.shape[2], image.shape[1]))
    heatmap_array = (heatmap_array * 255).astype(np.uint8)
    heatmap_colored = cv2.applyColorMap(heatmap_array, cv2.COLORMAP_JET)
    original_image = (image[0] * 255).astype(np.uint8)
    overlay = cv2.addWeighted(original_image, 0.7, heatmap_colored, 0.3, 0)
    return heatmap_array, overlay
