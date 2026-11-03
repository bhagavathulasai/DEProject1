# DentalVision AI – Setup Guide

This guide is for the current repository baseline. It is meant to help you reproduce the original project as it exists today, with clear handling for missing model files and missing environment configuration.

## 1. Recommended Python version

The project has been validated with Python 3.11.

Use:

```bash
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Environment configuration

Create a local `.env` file using the example template:

```bash
copy .env.example .env
```

Then edit `.env` and set the required values:

```env
GROQ_API_KEY=your_api_key_here
DENTALVISION_MODEL_PATH=
DENTALVISION_MODEL_DIR=./models
DENTALVISION_DATASET_DIR=./Data set
FLASK_DEBUG=1
PORT=5000
```

Important:
- `GROQ_API_KEY` is required for the validation step.
- A trained model file is still required for actual inference.
- Without a valid model file, the app will start, but prediction requests will return a clear 503 error.

## 3. Model artifact requirement

The repository does not contain a trained model file. The backend expects a valid TensorFlow model artifact before making predictions.

You must provide one of the following:

- an exported `.h5` or `.keras` file under `./models/`, or
- a configured path via `DENTALVISION_MODEL_PATH`

Examples:

```bash
mkdir models
# place model file here
```

or:

```env
DENTALVISION_MODEL_PATH=C:/path/to/your/model/MobileNet_Model.h5
```

## 4. Dataset expectation

The dataset is expected under:

```text
./Data set/
```

The repo currently contains class folders such as:

- Calculus
- Data caries
- Gingivitis
- hypodontia
- ulcer original dataset

This is the actual folder layout that the notebook uses.

## 5. Run the application

From the project root:

```bash
.\.venv\Scripts\activate
python app.py
```

Then open:

```text
http://localhost:5000/
```

## 6. Validate the startup

Check the health endpoint:

```bash
curl http://localhost:5000/health
```

Expected behavior:
- server starts successfully,
- `status` is `ok`,
- `model_loaded` may be `false` if no model file is available,
- `groq_configured` reflects whether the API key is set.

## 7. Upload and prediction flow

1. Open the web UI
2. Upload an image
3. The app saves the file to `static/uploads/`
4. It checks the `GROQ_API_KEY` and validates the image using the external Groq API
5. If the image passes validation and the model exists, it runs inference and returns a prediction JSON object
6. If the model is missing, the app returns a clear error instead of crashing

## 8. Notes about the original implementation

This repository is a prototype and is not yet fully production-ready. The main blockers are:

- no trained model artifact committed to the repo,
- hardcoded Windows path in the original app,
- missing environment configuration,
- Groq validation dependency when no API key is present,
- class-label mismatch between the dataset and app output vocabulary.

This guide keeps the original project runnable and explicit about those constraints before any major modernization work.
