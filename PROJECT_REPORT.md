# DentalVision AI — Project Report and Operator Guide

## 1. Executive summary

DentalVision AI is an academic/portfolio prototype for classifying oral-health
images. Its intended pipeline is:

1. A user supplies an oral or dental image.
2. The backend checks that the file is a supported image and asks Groq's
   multimodal API whether it appears to show teeth/oral structures.
3. If validation passes, TensorFlow/Keras preprocesses the image and runs a
   locally stored classifier.
4. The API returns a predicted class and confidence score.

The repository also contains a dataset, model-training code, evaluation tools,
database scaffolding, a React/Vite frontend experiment, and an older Flask
prototype.

**The currently active server is FastAPI, not Flask.** Running `python app.py`
starts the FastAPI application on port 8000. The browser-based interactive API
documentation is at `http://localhost:8000/docs`. The old port-5000 instructions
in `SETUP_GUIDE.md` describe the Flask prototype and are not correct for this
entry point.

The model file currently configured in the local `.env` is
`artifacts/smoke/models/Improved_CNN_trained.keras`. The startup log confirms
that it loads. However, its saved smoke-test evaluation reports **20% accuracy
on 20 test images** (four per class). It is useful for confirming the
load-and-predict path, not as evidence of a reliable or clinically useful
classifier. This project is not a medical diagnostic device.

## 2. What the project is trying to achieve

The project combines a few learning goals into one demonstrator:

- **Computer vision:** read, resize, and normalize image data.
- **Machine learning:** train a multi-class image classifier using TensorFlow
  and Keras.
- **Model evaluation:** report classification metrics, confusion matrices,
  calibration, latency, model size, and Grad-CAM visualizations.
- **Backend/API development:** accept uploaded images, validate them, run
  inference, and return structured results.
- **External service integration:** use Groq image understanding as a
  preliminary image-type check.
- **Application scaffolding:** include database models/migrations,
  containerization, CI, and a frontend experiment.

The five dataset folders are `Calculus`, `Data caries`, `Gingivitis`,
`hypodontia`, and `ulcer original dataset`. The code maps those source folder
names to the output labels Calculus, Dental Caries, Gingivitis, Hypodontia, and
Mouth Ulcer.

## 3. How to run and use the current application

### 3.1 Run locally on Windows

Open PowerShell in the project directory (the directory containing `app.py`):

```powershell
cd M:\balasai_project\DEProject1
.\.venv\Scripts\Activate.ps1
python app.py
```

If you are creating the environment for the first time, use Python 3.11:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

The running server prints a Uvicorn address. Keep that PowerShell window open.
Open:

- API documentation and interactive testing: `http://localhost:8000/docs`
- Health status: `http://localhost:8000/api/v1/health`
- Alternative API documentation: `http://localhost:8000/redoc`

`0.0.0.0:8000` in the log is the address the server listens on; use
`localhost:8000` in your browser.

### 3.2 Make a prediction in the current API

1. Open `http://localhost:8000/docs`.
2. Expand `POST /api/v1/predictions`.
3. Select **Try it out**, choose an image file, and execute the request.
4. A successful response contains a prediction ID, class label, confidence
   score, completion status, timestamp, and model name.

The request must be a supported image (`.png`, `.jpg`, `.jpeg`, `.bmp`, or
`.webp`) and must not exceed the configured upload-size limit (8 MB by default).
The image is sent to Groq for the image-type check, so a valid `GROQ_API_KEY`
and network access are required. If the check passes and the model is loaded,
the classifier returns its highest-probability class. The confidence is the
model's top class probability, not a medical certainty score.

Other useful endpoints:

| Method and path | Purpose |
|---|---|
| `GET /api/v1/health` | Reports API status, whether the model loaded, and whether Groq is configured. |
| `GET /api/v1/models` | Reports the configured model and whether it is loaded. |
| `POST /api/v1/predictions` | Validates and classifies an uploaded image. |
| `GET /api/v1/predictions` | Lists prediction records held by the running process. |
| `GET /api/v1/predictions/{prediction_id}` | Returns a prediction record from the running process. |

Prediction records are currently kept in process memory, not persisted in the
PostgreSQL tables. They disappear when the server restarts.

### 3.3 Environment settings

The local `.env` file is private configuration and should not be shared or
committed. The report intentionally does not reproduce its contents. Important
variables include:

| Variable | What it controls |
|---|---|
| `GROQ_API_KEY` | Credential for the external image-validation request. Keep it secret; rotate it if it has been exposed. |
| `DENTALVISION_MODEL_PATH` | Explicit path to a `.h5` or `.keras` model file. The current local setting points to the smoke-test model under `artifacts/smoke/models`. |
| `DENTALVISION_MODEL_DIR` | Fallback directory searched for a few conventional model filenames. |
| `DENTALVISION_DATASET_DIR` | Dataset directory used by the training pipeline. |
| `DENTALVISION_UPLOAD_DIR` | Directory where the FastAPI prediction service stores uploads. |
| `DENTALVISION_STORAGE_DIR` | Configured secure-storage directory; it is not the active prediction-record database. |
| `DATABASE_URL` | SQLAlchemy connection string for PostgreSQL. |
| `PORT` | Server port; this project defaults to 8000. |
| `LOG_LEVEL` | Backend log verbosity. |

The `.env.example` file is a template, not the live settings. Do not copy a
real API key into documentation, source code, screenshots, or version control.

### 3.4 Docker

The Compose setup is intended to run the API and PostgreSQL:

```powershell
cd M:\balasai_project\DEProject1
docker compose up --build
```

The API is mapped to host port 8000, and PostgreSQL to 5432. If the local
`python app.py` server is already using port 8000, stop it with Ctrl+C before
starting the Compose API (or stop Compose before starting the local API).

**The current Docker model mount needs attention before expecting predictions.**
Compose mounts `./models` into `/app/models`, while the local model is under
`./artifacts/smoke/models`; moreover, an absolute Windows path from `.env` is
not a valid container path. Therefore, a container may start without loading
the local model unless the model is mounted into the container and
`DENTALVISION_MODEL_PATH` is set to the corresponding Linux path. For now, the
documented reliable run path is local Python.

The Compose database startup does not mean prediction history is persisted:
the current prediction service still uses an in-memory store.

### 3.5 What the startup messages mean

The supplied run log showed:

- Uvicorn started on port 8000 and reported application startup complete.
- The model loaded from the configured `.keras` path (`Model loaded: True`).
- PostgreSQL was not reachable, so schema creation was skipped. This warning
  did not stop the API.
- TensorFlow reported oneDNN CPU optimizations and that native Windows GPU
  support is unavailable for that TensorFlow build. These messages did not
  prevent the CPU model from loading.

Thus, the server was running successfully at that time. A PostgreSQL warning
does not explain a browser connection failure; use port 8000, not 5000, and
check that the server process is still running.

## 4. What has actually been produced so far

The repository contains a trained Keras artifact and smoke-test evaluation
files in `artifacts/smoke/`:

- `models/Improved_CNN_trained.keras` — about 298.4 MiB; loads successfully in
  the reported local run.
- `metrics/Improved_CNN_metrics.json` and
  `metrics/Improved_CNN_classification_report.json` — evaluation data.
- `summary.json` — summary of the model metrics.
- `gradcam/Improved_CNN_overlay.png` — an interpretability visualization.

The recorded test split has 20 images (four per class), with **20% accuracy**,
and **0.0667 macro F1**. The confusion matrix in the report shows all 20 test
samples predicted as Gingivitis. This is a smoke-test result with very weak
performance; it must not be presented as demonstrating useful diagnostic
accuracy. The saved metrics also have naming inconsistencies: the
`rejection_rate` field records the fraction accepted by the current
`rejection_decision` helper, and the `loss` field is populated with macro F1,
not model loss. Interpret those values using the implementation rather than
the field names. The server log proves the artifact can be loaded, not that
the model is accurate.

The API returns machine-generated labels and scores only. It is not a
substitute for a dental professional or clinical evaluation.

## 5. Repository map

This section explains the project files and directories that are part of the
application, its data, or its development workflow. Individual dataset images
and generated/uploaded images are data files rather than separately meaningful
source files, so they are described by folder and purpose.

### 5.1 Root-level project files

| File | Purpose |
|---|---|
| `app.py` | **Current entry point.** Imports `api_app.main:app` and runs it with Uvicorn on the configured port (8000 by default). It does not launch Flask. |
| `legacy_flask_app.py` | Earlier Flask upload/prediction prototype. It serves `templates/index.html`, uses `/predict` and `/health`, and defaults to port 5000. It is not the app launched by `python app.py`. |
| `another.py` | Groq integration shared by the API and old Flask app. Converts image bytes to base64, requests an `is_teeth` JSON response, and checks whether the API key is configured. Uploaded image content is sent to the external service. |
| `project_config.py` | Resolves dataset/model directories and searches for configured or conventional model paths. The current explicit model path is important because the smoke-test filename is not one of its conventional fallback names. |
| `train_pipeline.py` | Command-line model training and evaluation workflow. Loads/splits images, trains one selected model, writes evaluation artifacts, and prints a JSON summary. |
| `Source code.ipynb` | Jupyter notebook for original ML experimentation and training. It is exploratory notebook content, separate from the current API runtime. |
| `requirements.txt` | Runtime Python dependencies, including FastAPI/Uvicorn, TensorFlow, image libraries, Groq, SQLAlchemy, and PostgreSQL support. |
| `requirements-dev.txt` | Test and quality-tool dependencies such as pytest, coverage, Ruff, and Black. |
| `pyproject.toml` | Ruff, Black, and pytest configuration. |
| `Makefile` | Convenience targets for install, formatting, lint, tests, checks, API startup, and Docker Compose. |
| `Dockerfile` | Builds the Python API container, installs requirements, copies project files, exposes port 8000, and starts `app.py`. |
| `docker-compose.yml` | Defines the API and PostgreSQL containers, health checks, ports, and local storage/model mounts. See the Docker model-path caveat above. |
| `alembic.ini` | Alembic migration configuration and default database URL setting. |
| `.env.example` | Safe-to-copy environment-variable template with a placeholder API key. Replace placeholders locally; do not put real secrets in it. |
| `.env` | Machine-specific live configuration, including credentials and paths. It is intentionally not documented or reproduced here. Treat it as secret and keep it out of Git. |
| `.gitignore` | Excludes virtual environments, caches, model artifacts, and editor/system files from version control. |
| `.dockerignore` | Excludes Git metadata, local environments, secrets, generated uploads, and local model files from the Docker build context. |
| `.pre-commit-config.yaml` | Configures Ruff, Black, and pytest hooks for pre-commit checks. |
| `SETUP_GUIDE.md` | Older setup instructions. Parts of it (notably Flask, port 5000, and `/health`) are stale for the active FastAPI entry point. |
| `DEPLOYMENT.md` | Local, Docker, Compose, CI, and deployment notes. Its FastAPI/port-8000 instructions are closer to the current app. |
| `PROJECT_OVERVIEW.md` | Earlier high-level overview. Some statements (no model, no tests, Flask-only runtime) are outdated. |
| `ARCHITECTURE.md` | Earlier architecture description, primarily of the Flask design; do not treat it as an exact map of the current FastAPI implementation. |
| `FILE_STRUCTURE.md` | Earlier file-tree guide. It omits newer API, training, database, frontend, Docker, and artifact files. |
| `TECHNICAL_DOCUMENTATION.md` | Technical explanation of the original training and Flask flow. Useful background, but parts do not match the current runtime. |
| `EXISTING_ISSUES.md` | Earlier risk list. It predates the current model artifact, tests, Docker files, and newer API structure, so its inventory is not current. |

### 5.2 Backend: `api_app/`

This is the active FastAPI server implementation.

| Path | Purpose |
|---|---|
| `api_app/main.py` | Creates the FastAPI app, starts model/database initialization, defines health/model/prediction endpoints, and maps application errors to HTTP responses. |
| `api_app/config.py` | Loads `.env` and defines runtime settings: API name/version, database URL, model/upload/storage paths, upload size, allowed extensions, and secret-key fallback. |
| `api_app/schemas.py` | Pydantic response shapes for health, model information, prediction results, and prediction records. |
| `api_app/db/__init__.py` | Package marker/documentation for the database layer. |
| `api_app/db/database.py` | Creates the SQLAlchemy engine/session factory and attempts to create tables during startup. The connection warning in the run log comes from this startup path. |
| `api_app/db/deps.py` | Provides a generator dependency that opens and closes a SQLAlchemy session. |
| `api_app/db/models.py` | Defines SQLAlchemy models for users, model versions, uploaded images, predictions, and prediction results. Current prediction API logic does not yet save records through these models. |
| `api_app/services/__init__.py` | Package marker/documentation for service classes. |
| `api_app/services/image_validation_service.py` | Validates filename extension and calls the Groq image-validation helper; requires `GROQ_API_KEY`. |
| `api_app/services/model_service.py` | Loads the Keras model, reads/resizes/normalizes images to 128×128, runs inference, maps class indices to labels, and describes model status. |
| `api_app/services/prediction_service.py` | Saves uploads, runs extension/Groq/model checks, constructs prediction records, and stores them in an in-memory `PredictionStore`. |

### 5.3 ML package: `dentalvision/`

| Path | Purpose |
|---|---|
| `dentalvision/__init__.py` | Exposes shared training configuration and label constants. |
| `dentalvision/config.py` | Defines training defaults (dataset/output/model paths, image size, batch size, epochs, splits, seed, and model names) and maps dataset directory names to display labels. |
| `dentalvision/data_pipeline.py` | Lists class folders, loads image files through OpenCV, resizes and normalizes them, performs stratified train/validation/test splits, and calculates class counts. |
| `dentalvision/models.py` | Builds the custom CNN or transfer-learning classifiers based on MobileNet, ResNet50, and EfficientNetB0. |
| `dentalvision/metrics.py` | Computes classification reports, confusion matrices, precision/recall/F1, calibration error, rejection decisions, model size, inference latency, JSON output, and Grad-CAM overlays. |

### 5.4 Dataset: `Data set/`

This is the class-folder dataset consumed by `train_pipeline.py`. It currently
contains:

| Folder | Intended class |
|---|---|
| `Data set/Calculus/` | Calculus |
| `Data set/Data caries/` | Dental Caries |
| `Data set/Gingivitis/` | Gingivitis |
| `Data set/hypodontia/` | Hypodontia |
| `Data set/ulcer original dataset/` | Mouth Ulcer |

The folders contain image files used for training/evaluation. The folder names
are the source labels; the configuration maps some of them to normalized
display labels. Dataset counts and quality should be rechecked before a
production-quality training run.

### 5.5 Model/artifact/data folders

| Path | Purpose and current contents |
|---|---|
| `models/` | Default model-search directory used by the app. It currently has a `smoke/` subfolder but no model directly at the conventional paths searched by fallback logic. |
| `artifacts/smoke/` | Outputs from a smoke-training/evaluation run. Contains the saved Keras model, JSON metrics/reports, summary, and Grad-CAM overlay described in section 4. |
| `static/uploads/` | Legacy Flask upload directory; currently contains uploaded image files. The active FastAPI service uses the configured storage upload directory instead. |
| `storage/uploads/` | Default upload location configured for the active API; may contain files from API use. |
| `storage/secure/` | Configured secure-storage directory for future use; the current prediction flow does not use it as a database or model store. |
| `uploads/` | Separate root-level image directory present in the workspace. It is not the configured upload destination for the active FastAPI route. |

Generated models, test artifacts, and uploaded images may contain large files or
sensitive data. Avoid committing them unless there is a specific, reviewed
reason to do so.

### 5.6 Web UI: `frontend/`, `templates/`, and `static/`

| Path | Purpose |
|---|---|
| `frontend/package.json` | React/Vite frontend dependencies and `dev`, `build`, and `preview` scripts. |
| `frontend/package-lock.json` | Locks the npm dependency versions. |
| `frontend/index.html` | Vite HTML entry document; it loads the React `src/main.tsx` entry. |
| `frontend/src/App.tsx` | React/Tailwind dashboard-style page. Current code is a frontend experiment and does not call the FastAPI prediction endpoints. |
| `frontend/src/main.tsx` | Mounts the React `App` in the document root. |
| `frontend/src/main.ts` | Separate Vite starter/demo script. The active `frontend/index.html` uses `main.tsx`, not this file. |
| `frontend/src/counter.ts` | Small counter helper used by the unused Vite starter page. |
| `frontend/src/index.css`, `frontend/src/style.css` | Frontend styles for the React app and starter page, respectively. |
| `frontend/src/assets/` | Image and starter-framework assets used by the frontend. |
| `frontend/public/` | Static frontend assets copied to the build output. |
| `frontend/dist/` | Existing built Vite output. It is generated output, not the FastAPI server's root page. |
| `frontend/node_modules/` | Installed npm dependencies; generated locally and should not be checked in. |
| `frontend/vite.config.ts` | Vite and React plugin configuration; frontend dev server uses port 5173. |
| `frontend/tsconfig.json` | TypeScript compiler options for the frontend. |
| `frontend/tailwind.config.js` | Tailwind content scanning and theme extension. |
| `frontend/postcss.config.js` | PostCSS/Tailwind/autoprefixer configuration. |
| `frontend/.gitignore` | Ignores frontend logs, `node_modules`, build output, and editor artifacts. |
| `frontend/Dockerfile` | Empty placeholder; it does not currently build or serve the frontend. |
| `templates/index.html` | Older single-page upload form used by `legacy_flask_app.py`; it is not served by the active FastAPI API. |

The React frontend can be started separately with `cd frontend` and
`npm run dev` (port 5173), but it is not currently wired to the API. For
working predictions today, use FastAPI's `/docs` interface.

### 5.7 Tests, migrations, and developer tooling

| Path | Purpose |
|---|---|
| `tests/test_api_health.py` | Contains basic tests for the health and models API endpoints. This is a small smoke-test suite, not comprehensive prediction or model-quality validation. |
| `alembic/env.py` | Connects Alembic to the SQLAlchemy metadata and configured database URL. |
| `alembic/versions/20261102_initial_schema.py` | Initial schema migration for the database tables represented in `api_app/db/models.py`. |
| `.github/workflows/ci.yml` | GitHub Actions workflow for Python setup, dependency installation, Ruff linting, and pytest with coverage; includes PostgreSQL as a CI service. |
| `.vscode/launch.json` | Generic VS Code Python debugger configuration for the currently selected file. |

## 6. Training a model

The scripted training workflow can be run from the project root. For a small
smoke run, pass a small `--limit-per-class`; for meaningful evaluation, use the
full dataset and a properly chosen number of epochs:

```powershell
python train_pipeline.py --help
python train_pipeline.py --dataset-dir "Data set" --output-dir artifacts\experiment --model-name Improved_CNN
```

The script loads and normalizes images, makes stratified splits, trains the
selected model, and writes model/metric/Grad-CAM outputs under the output
directory. Available model names are `Improved_CNN`, `MobileNet`, `ResNet50`,
and `EfficientNetB0`.

After training, configure `DENTALVISION_MODEL_PATH` to the exact generated
`.keras` file before starting the API. The current model resolver checks an
explicit environment path first, followed by a limited set of conventional
filenames in `DENTALVISION_MODEL_DIR`; it does not automatically discover
every model generated by the training script.

Training a file is not proof of quality. Review per-class recall, confusion
matrix, sample counts, data leakage risks, and performance on a sufficiently
large independent test set before interpreting predictions.

## 7. Known limitations and interpretation

1. **Not for diagnosis:** This is a prototype. Predictions must not guide care
   or replace a qualified dental professional.
2. **Weak smoke-test model:** The recorded 20% accuracy and 0.0667 macro F1
   show that the current artifact is not a reliable classifier. Some saved
   metric field names also do not match the quantities they contain.
3. **Groq dependency and privacy:** Prediction uploads are sent to a third
   party for image validation. Do not upload identifiable or sensitive patient
   material without appropriate authorization and privacy review.
4. **No production frontend integration:** The React dashboard is not
   connected to the API; use `/docs` to test the backend.
5. **No persistent prediction history yet:** The API's prediction list is
   in-memory; the SQL tables exist as scaffolding but are not used by the
   prediction service.
6. **Database optional for current startup:** Local startup can continue when
   PostgreSQL is unreachable, as shown by the warning in the supplied logs.
7. **Docker model path mismatch:** The model currently resides in the
   artifacts tree, whereas Compose mounts only the default models folder.
8. **Documentation drift:** Several historical documents describe the Flask
   app, port 5000, and a missing model. The observed current code and run log
   instead show a FastAPI server on port 8000 with a loadable smoke model.

## 8. Suggested next steps

1. Keep the current FastAPI `/docs` workflow as the simple demonstration path.
2. Replace the smoke model with a properly trained and independently evaluated
   model before presenting useful classification results.
3. Make the model path portable and mount the model correctly in Docker.
4. Decide whether the React frontend should be integrated; if so, connect its
   upload flow to `POST /api/v1/predictions` and surface API errors.
5. Persist prediction records if history is a requirement.
6. Update or retire the older Flask-oriented setup and architecture documents
   so future users receive one consistent set of instructions.
7. Rotate any API key that has been exposed and keep all credentials out of
   source control.
