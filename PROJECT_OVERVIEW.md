# DentalVision AI – Project Overview

## 1. Problem the project tries to solve

This project is a dental disease classification system that attempts to classify oral health conditions from a single input image. The current repository is built around a Flask web application that accepts an uploaded dental image and predicts the likely disease class.

The intended use case is:

- A user uploads a dental image or intraoral photo.
- The application checks whether the image looks like a dental/teeth image.
- If it passes the validation step, a deep learning model predicts the disease category.
- The application returns a predicted class and confidence score to the user.

The disease classes represented in the project are related to common dental conditions, including calculus, caries (dental caries), gingivitis, hypodontia, and mouth ulcer. The project is intended as an academic prototype and portfolio artifact rather than a fully hardened production system.

## 2. Current project status

The repository currently contains:

- A Flask backend in `app.py`
- A Groq-based image validation helper in `another.py`
- A single HTML frontend page in `templates/index.html`
- A dataset folder named `Data set/`
- A training notebook: `Source code.ipynb`
- Dependency definitions in `requirements.txt`
- No README file
- No trained model artifact in the repository

This means the repository is a working prototype skeleton rather than a complete, deployment-ready ML product. The project demonstrates the core idea, but it is not yet production-quality.

## 3. What the application does end-to-end

### Frontend flow

1. A user opens the root URL (`/`) in the browser.
2. The browser receives an HTML form that allows an image upload.
3. The user selects an image and submits it to the `/predict` endpoint.
4. The JavaScript in the page sends a `multipart/form-data` request using `fetch()`.
5. The browser displays the prediction result, confidence, and uploaded image.

### Backend flow

1. The Flask application receives the uploaded file.
2. It saves the uploaded image into `static/uploads/`.
3. It calls `analyze_image(file_path)` from `another.py`.
4. That function sends the image to Groq’s multimodal LLM API for a yes/no check: “Is this a teeth image?”
5. If the image passes validation, the backend loads a TensorFlow model from a hardcoded local file path.
6. The image is resized to 128x128, normalized to `[0,1]`, and converted into a batch tensor.
7. The model predicts class probabilities.
8. The application calculates the top class, confidence, and entropy.
9. It applies a simple confidence threshold and rejects low-confidence predictions.
10. It returns JSON to the frontend.

### ML workflow

1. The dataset is loaded from folders under `Data set/`.
2. Each class folder is converted into arrays of images and class indices.
3. The notebook uses a stratified split for train/test/validation sets.
4. Several models are trained and compared.
5. Model checkpoints are saved as `.h5` files, but none are included in this repository snapshot.

## 4. Core project purpose

The repository demonstrates a full-stack AI academic project where:

- computer vision is used for dental image classification,
- deep learning models are trained on image datasets,
- a simple web interface provides user interaction,
- a backend API performs inference,
- a multimodal external LLM is used as a sanity gate before model inference.

This is useful as an academic project because it combines:

- Python programming
- ML model training
- Computer vision preprocessing
- Deep learning inference
- REST-like backend integration
- Full-stack UI
- External cloud API integration

## 5. Current strengths

- Clear proof-of-concept for full-stack ML inference
- Real dataset folder structure available in the repo
- Notebook contains the training logic and architecture experiments
- Backend and frontend are connected through a basic upload flow
- The app structure is simple enough to understand and extend

## 6. Current limitations

- No README or architecture documentation
- No trained model file in the repo
- Model path is hardcoded to a Windows file location that does not exist in this environment
- Class names in the backend do not align with actual dataset folder names
- Groq API key is required and not versioned into the repo
- The project is not modularized for production engineering
- There are no automated tests
- There is no database layer or persistent storage
- There is no proper managed deployment configuration
- Error handling and validation are minimal

## 7. Summary

This repository is best understood as an academic, end-to-end proof-of-concept for dental image classification. It shows how a dataset can be loaded, a model can be trained, and an application can deploy a working inference pipeline via a lightweight web frontend. However, it is not yet productionized or architecture-grade, and several important issues must be corrected before it can be treated as a strong professional portfolio system.
