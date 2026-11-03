import logging
import os
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf
from another import analyze_image, is_groq_configured
from dentalvision.config import DATASET_CLASS_LABELS
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, url_for
from project_config import resolve_model_path
from werkzeug.utils import secure_filename

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
app.config.update(
    UPLOAD_FOLDER=str(UPLOAD_FOLDER),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    SECRET_KEY=os.getenv("SECRET_KEY", "dentalvision-dev-secret"),
)


def load_model():
    model_path = resolve_model_path()
    if model_path is None:
        logging.warning(
            "No trained model artifact found. Set DENTALVISION_MODEL_PATH or "
            "place a model in ./models/"
        )
        return None

    try:
        model = tf.keras.models.load_model(str(model_path))
        logging.info("Loaded model from %s", model_path)
        return model
    except Exception:
        logging.exception("Failed to load model from %s", model_path)
        return None


app.config["MODEL"] = load_model()


def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Unable to read image file: {image_path}")

    image = cv2.resize(image, (128, 128))
    image = image.astype(np.float32) / 255.0
    image = np.expand_dims(image, axis=0)
    return image


def calculate_entropy(probs):
    return -np.sum(probs * np.log(probs + 1e-10))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "model_loaded": app.config["MODEL"] is not None,
            "groq_configured": is_groq_configured(),
            "uploads_dir": str(UPLOAD_FOLDER),
        }
    )


@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files or request.files["file"].filename == "":
            logging.error("No file uploaded in the request.")
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        file_extension = Path(file.filename).suffix.lower()
        allowed_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
        if file_extension not in allowed_extensions:
            return (
                jsonify(
                    {
                        "error": (
                            "Unsupported file type. Please upload a JPG, JPEG, PNG, "
                            "BMP, or WEBP image."
                        )
                    }
                ),
                400,
            )

        upload_folder = Path(app.config["UPLOAD_FOLDER"])
        upload_folder.mkdir(parents=True, exist_ok=True)
        safe_name = secure_filename(file.filename)
        file_path = upload_folder / safe_name
        file.save(str(file_path))

        if not is_groq_configured():
            logging.warning("GROQ_API_KEY not configured. Image validation skipped.")
            return (
                jsonify(
                    {
                        "error": (
                            "Image validation is unavailable because GROQ_API_KEY is "
                            "not set. Add it to your .env file."
                        )
                    }
                ),
                503,
            )

        try:
            validation_result = analyze_image(str(file_path))
        except Exception as exc:
            logging.exception("Image validation failed")
            return jsonify({"error": f"Image validation failed: {exc}"}), 503

        if not validation_result.get("is_teeth", False):
            return jsonify(
                {
                    "message": "Please upload a teeth image",
                    "image_url": url_for("static", filename=f"uploads/{safe_name}"),
                }
            )

        if app.config["MODEL"] is None:
            return (
                jsonify(
                    {
                        "error": (
                            "The model is not available. Add a trained .h5 or .keras "
                            "model to the configured model path."
                        )
                    }
                ),
                503,
            )

        image = preprocess_image(str(file_path))
        pred_probs = app.config["MODEL"].predict(image, verbose=0)[0]
        logging.info("Prediction probabilities: %s", pred_probs)

        predicted_index = int(np.argmax(pred_probs))
        confidence = float(pred_probs[predicted_index])
        entropy = calculate_entropy(pred_probs)

        class_labels = DATASET_CLASS_LABELS
        confidence_threshold = 0.9
        entropy_threshold = 1.2
        second_highest_prob = float(np.sort(pred_probs)[-2])

        if (
            confidence >= confidence_threshold
            and entropy < entropy_threshold
            and (confidence - second_highest_prob) > 0.2
        ):
            prediction = class_labels[predicted_index]
        else:
            prediction = "Not the proper data"

        response = {
            "confidence_score": round(confidence, 4),
            "image_url": url_for("static", filename=f"uploads/{safe_name}"),
            "prediction": prediction,
        }
        return jsonify(response)

    except Exception:
        logging.exception("Error occurred during prediction")
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
