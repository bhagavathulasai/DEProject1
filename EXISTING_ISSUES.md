# DentalVision AI – Existing Issues and Risks

This document summarizes the major issues identified during the project inspection.

## 1. Missing trained model artifact

### Issue

The Flask app expects a model file at a hardcoded Windows path:

```python
r"C:\Users\exter\OneDrive\Desktop\project\MobileNet_Model (1).h5"
```

No `.h5`, `.keras`, `.pt`, or `.onnx` model file exists in the repository workspace.

### Why this matters

The application cannot run inference without a model artifact. This makes the project non-runnable in the current environment.

## 2. Label mismatch between app and dataset

### Issue

The app defines class labels as:

- Calculus
- Dental Caries
- Gingivitis
- Hypodontia
- Mouth Ulcer
- Tooth Discoloration

But the dataset folder names are:

- Calculus
- Data caries
- Gingivitis
- hypodontia
- ulcer original dataset

This mismatch means the web app and the actual dataset are not aligned.

### Why this matters

It can lead to wrong labels, incorrect interpretation, or broken prediction mapping after model inference.

## 3. Hardcoded absolute paths

### Issue

The app contains hardcoded path logic and local environment assumptions.

### Why this matters

The project will not port cleanly to another machine, container, or deployment environment.

## 4. Missing documentation and project structure guidance

### Issue

There is no README, architecture guide, or developer onboarding documentation.

### Why this matters

Anyone trying to run or extend the project must reverse-engineer it from source code alone.

## 5. External API dependency for validation

### Issue

`another.py` depends on Groq’s cloud API for validation and requires `GROQ_API_KEY`.

### Why this matters

The validation step fails without network access or a valid API key. This introduces latency, cost, and a third-party trust dependency into the application flow.

## 6. No environment template or secure configuration management

### Issue

There is no `.env.example`, no deployment config, and no documentation for required environment variables.

### Why this matters

Users cannot easily reproduce the setup, and sensitive keys are not managed in a secure or standard way.

## 7. No tests or validation automation

### Issue

There is no test suite, CI pipeline, or automated validation workflow.

### Why this matters

The project cannot verify correctness or reliably catch regressions during changes.

## 8. Weak backend separation of concerns

### Issue

`app.py` combines file upload handling, validation orchestration, preprocessing, inference, and response formatting in a single file.

### Why this matters

This makes the code harder to scale, modify, and debug as the system grows.

## 9. Minimal error handling and production readiness gaps

### Issue

The backend does minimal validation and simple try/except blocks; there are no service-specific or structured error responses.

### Why this matters

The app lacks observability, robustness, and maintainability for production use.

## 10. Unclear clinical reliability and evaluation status

### Issue

No formal model evaluation metrics, dataset split summary, or training performance report are included in the repo.

### Why this matters

The project cannot substantiate accuracy claims or demonstrate real clinical usefulness.

## 11. Dataset quality and naming inconsistencies

### Issue

The folder naming is inconsistent and some labels are not normalized or standardized.

### Why this matters

This is a common source of label leakage, misclassification, and confusion during model training.

## 12. No deployment or containerization config

### Issue

There is no Dockerfile, docker-compose configuration, or cloud deployment manifest.

### Why this matters

The project is not ready for reproducible deployment or portfolio demonstration in a containerized environment.

## 13. Summary

The project is a valid prototype demonstrating a full-stack AI concept, but it is not yet production-ready. The most critical issues are the missing trained model artifact, hardcoded paths, dataset/app label mismatch, external API dependency, and lack of tests and deployment configuration. These must be addressed before the project can be positioned as a professional portfolio-grade system.
