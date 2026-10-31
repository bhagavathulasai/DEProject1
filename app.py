from flask import Flask, request, render_template, jsonify, url_for
import tensorflow as tf
import numpy as np
import cv2,base64
from another import analyze_image
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the trained model
model_path = r"C:\Users\exter\OneDrive\Desktop\project\MobileNet_Model (1).h5"
model = tf.keras.models.load_model(model_path)

# Preprocess image function
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (128, 128))
    image = image / 255.0  # Normalize
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

# Function to calculate entropy of predictions
def calculate_entropy(probs):
    return -np.sum(probs * np.log(probs + 1e-10))  # Small epsilon to avoid log(0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files or request.files['file'].filename == '':
            logging.error("No file uploaded in the request.")
            return jsonify({'error': 'No file uploaded'})

        file = request.files['file']
        upload_folder = "static/uploads/"
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        forteeth = analyze_image(file_path)
        logging.info(f"Analyze image response: {forteeth}")

        if file_path:
            is_teeth = analyze_image(file_path)
            logging.info(f"Is teeth response: {is_teeth}")

        if is_teeth['is_teeth']:
            image = preprocess_image(file_path)

            # Class labels
            class_labels = ["Calculus", "Dental Caries", "Gingivitis", "Hypodontia", "Mouth Ulcer", "Tooth Discoloration"]
            
            # Predict
            pred_probs = model.predict(image)[0]
            logging.info(f"Prediction probabilities: {pred_probs}")
            predicted_index = np.argmax(pred_probs)
            confidence = pred_probs[predicted_index]
            entropy = calculate_entropy(pred_probs)
            logging.info(f"Predicted index: {predicted_index}, Confidence: {confidence}, Entropy: {entropy}")
            
            # Define rejection criteria
            confidence_threshold = 0.9  # Only accept highly confident predictions
            entropy_threshold = 1.2  # Reject if probabilities are too spread out
            second_highest_prob = np.sort(pred_probs)[-2]  # Second highest probability
            
            # Decision logic
            if confidence >= confidence_threshold and entropy < entropy_threshold and (confidence - second_highest_prob) > 0.2:
                prediction = class_labels[predicted_index]
            else:
                prediction = "Not the proper data"
            
            response = {
                "confidence_score": round(float(confidence), 4),
                "image_url": url_for('static', filename=f'uploads/{file.filename}'),
                "prediction": prediction
            }
        else:
            response = {
                "message": "Please upload a teeth image",
                "image_url": url_for('static', filename=f'uploads/{file.filename}')
            }

        return jsonify(response)
    except Exception as e:
        logging.error("Error occurred during prediction", exc_info=True)
        return jsonify({'error': 'An internal server error occurred. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True)