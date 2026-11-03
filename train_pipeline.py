from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from dentalvision.config import DATASET_CLASS_LABELS, TrainingConfig
from dentalvision.data_pipeline import (
    compute_class_distribution,
    load_image_dataset,
    stratified_split_data,
)
from dentalvision.metrics import (
    compute_classification_report,
    compute_confusion_matrix,
    compute_precision_recall_f1,
    estimate_expected_calibration_error,
    generate_gradcam,
    get_model_size_mb,
    measure_inference_latency,
    rejection_decision,
    save_json,
)
from dentalvision.models import build_model
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train and evaluate the DentalVision dental image classification pipeline."
    )
    parser.add_argument(
        "--dataset-dir",
        type=str,
        default="Data set",
        help="Directory containing class subfolders.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="artifacts",
        help="Folder to store metrics and trained models.",
    )
    parser.add_argument(
        "--model-dir",
        type=str,
        default="models",
        help="Folder to save model artifacts.",
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--image-size", type=int, nargs=2, default=(128, 128))
    parser.add_argument("--test-ratio", type=float, default=0.2)
    parser.add_argument("--validation-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--model-name",
        type=str,
        choices=["Improved_CNN", "MobileNet", "ResNet50", "EfficientNetB0"],
        default="Improved_CNN",
    )
    parser.add_argument("--limit-per-class", type=int, default=None)
    parser.add_argument("--mlflow-tracking-uri", type=str, default=None)
    return parser.parse_args()


def maybe_enable_mlflow(uri: str | None) -> None:
    try:
        import mlflow
    except ImportError:
        return

    if uri:
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment("dentalvision-ai")


def train_and_evaluate_single_model(
    model_name: str,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    class_names: list[str],
    config: TrainingConfig,
    output_dir: Path,
) -> dict[str, object]:
    model = build_model(model_name, config.input_shape, len(class_names))
    model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=config.epochs,
        batch_size=config.batch_size,
        verbose=1,
    )

    test_predictions = model.predict(x_test, verbose=0)
    y_pred = np.argmax(test_predictions, axis=1)

    report = compute_classification_report(y_test, y_pred, class_names)
    precision_recall = compute_precision_recall_f1(y_test, y_pred, class_names)
    conf_matrix = compute_confusion_matrix(y_test, y_pred, list(range(len(class_names))))
    ece = estimate_expected_calibration_error(
        y_test, test_predictions, list(range(len(class_names)))
    )

    rejection_mask = [rejection_decision(prob) for prob in test_predictions]
    rejection_rate = float(np.mean(rejection_mask))

    latency = measure_inference_latency(model, x_test[:10], runs=10)
    model_path = output_dir / "models" / f"{model_name}_trained.keras"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(model_path)

    metrics = {
        "test_accuracy": float(report["accuracy"]),
        "loss": float(report.get("macro avg", {}).get("f1-score", 0.0)),
        "precision_macro": float(report["macro avg"]["precision"]),
        "recall_macro": float(report["macro avg"]["recall"]),
        "f1_macro": float(report["macro avg"]["f1-score"]),
        "expected_calibration_error": ece,
        "rejection_rate": rejection_rate,
        "inference_latency_seconds": latency,
        "model_size_mb": get_model_size_mb(model_path),
        "class_distribution": compute_class_distribution(y_test, class_names),
        "per_class_metrics": precision_recall,
        "confusion_matrix": conf_matrix.tolist(),
    }

    save_json(metrics, output_dir / "metrics" / f"{model_name}_metrics.json")
    save_json(report, output_dir / "metrics" / f"{model_name}_classification_report.json")

    sample_image = x_test[0]
    _, overlay = generate_gradcam(model, sample_image, class_index=int(y_pred[0]))
    Image.fromarray(overlay).save(output_dir / "gradcam" / f"{model_name}_overlay.png")

    return metrics


def run_training() -> None:
    args = parse_args()
    config = TrainingConfig(
        dataset_dir=args.dataset_dir,
        output_dir=args.output_dir,
        model_dir=args.model_dir,
        image_size=tuple(args.image_size),
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_ratio=args.validation_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )

    x, y, folder_names = load_image_dataset(
        config.dataset_dir,
        image_size=config.image_size,
        limit_per_class=args.limit_per_class,
    )
    class_names = list(folder_names)
    if len(class_names) != len(DATASET_CLASS_LABELS):
        class_names = class_names[: len(DATASET_CLASS_LABELS)]

    x_train, y_train, x_val, y_val, x_test, y_test = stratified_split_data(
        x, y, config.test_ratio, config.validation_ratio, config.seed
    )

    model_output_root = Path(config.output_dir)
    model_output_root.mkdir(parents=True, exist_ok=True)
    (model_output_root / "metrics").mkdir(parents=True, exist_ok=True)
    (model_output_root / "gradcam").mkdir(parents=True, exist_ok=True)
    (model_output_root / "models").mkdir(parents=True, exist_ok=True)

    maybe_enable_mlflow(args.mlflow_tracking_uri)
    try:
        import mlflow
    except ImportError:
        mlflow = None

    results: dict[str, dict[str, object]] = {}
    for model_name in [args.model_name]:
        metrics = train_and_evaluate_single_model(
            model_name=model_name,
            x_train=x_train,
            y_train=y_train,
            x_val=x_val,
            y_val=y_val,
            x_test=x_test,
            y_test=y_test,
            class_names=class_names,
            config=config,
            output_dir=model_output_root,
        )
        results[model_name] = metrics
        if mlflow is not None:
            mlflow.log_param("model_name", model_name)
            for key, value in metrics.items():
                if isinstance(value, int | float):
                    mlflow.log_metric(key, float(value))

    save_json(results, model_output_root / "summary.json")
    summary = {
        key: {
            k: v
            for k, v in val.items()
            if isinstance(v, int | float | str)
        }
        for key, val in results.items()
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    tf.keras.utils.set_random_seed(42)
    run_training()
