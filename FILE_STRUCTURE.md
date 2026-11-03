# DentalVision AI – File and Directory Structure

## Repository root

```text
DEProject1/
├── .git/
├── .gitignore
├── .vscode/
│   └── launch.json
├── Data set/
│   ├── Calculus/
│   ├── Data caries/
│   ├── Gingivitis/
│   ├── hypodontia/
│   └── ulcer original dataset/
├── static/
│   └── uploads/
├── templates/
│   └── index.html
├── another.py
├── app.py
├── requirements.txt
├── Source code.ipynb
├── project_config.py
├── PROJECT_OVERVIEW.md
├── ARCHITECTURE.md
├── FILE_STRUCTURE.md
├── TECHNICAL_DOCUMENTATION.md
├── EXISTING_ISSUES.md
└── (no trained model files currently present)
```

## Purpose of each path

### `.gitignore`

Defines which files should not be tracked by Git. It includes Python env folders, compiled caches, and common model file extensions such as `.h5`, `.keras`, `.pth`, `.pt`, and `.onnx`.

### `.vscode/launch.json`

A VS Code debug configuration for running Python files in the integrated terminal.

### `Data set/`

This is the dataset directory containing class folders. The actual class names observed are:

- `Calculus`
- `Data caries`
- `Gingivitis`
- `hypodontia`
- `ulcer original dataset`

These folders contain image files used to train and evaluate the model.

### `static/uploads/`

This is the upload directory where images submitted through the web UI are saved before processing.

### `templates/index.html`

The frontend HTML page including the upload form, CSS, and JavaScript for sending prediction requests.

### `another.py`

This module validates whether an uploaded image is a teeth image by sending it to Groq’s multimodal LLM API. It returns a JSON object with an `is_teeth` boolean.

### `app.py`

This file is the Flask backend. It serves the web page, saves uploaded files, invokes image validation, preprocesses images, loads the model, runs inference, and returns prediction JSON.

### `requirements.txt`

Lists the Python dependencies required by the project.

### `Source code.ipynb`

The notebook containing the ML pipeline used for dataset loading, splitting, augmentation, model training, evaluation, and model export.

### `project_config.py`

A small configuration helper for dataset and model directories. It defines environment-variable-based paths and resolves valid model files from a small candidate list.

### `PROJECT_OVERVIEW.md`

High-level summary of the project and current status.

### `ARCHITECTURE.md`

Architecture and data flow documentation, including a Mermaid diagram.

### `FILE_STRUCTURE.md`

Repository structure inventory.

### `TECHNICAL_DOCUMENTATION.md`

Detailed technical explanation of dataset processing, model training, Flask backend, prediction logic, and integration points.

### `EXISTING_ISSUES.md`

Current known issues and risk areas discovered during the repository inspection.

## Important missing items

The following artifacts are absent from the current workspace and should be explicitly called out:

- trained model weights (.h5 / .keras / .weights)
- dedicated README.md
- test suite
- deployment configuration (Dockerfile, docker-compose.yml, Kubernetes manifests)
- environment template (.env.example)
- database configuration or SQL schema
- CI/CD pipeline configuration
