# Deployment and local development guide

## Local development

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   . .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate  # Windows PowerShell
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ```
3. Copy environment settings:
   ```bash
   copy .env.example .env
   ```
4. Update `.env` with local values such as `GROQ_API_KEY`, `DENTALVISION_MODEL_PATH`, and database settings.
5. Start the app:
   ```bash
   python app.py
   ```
6. Validate the API:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

## Docker

Build and run the app with Docker:

```bash
docker build -t dentalvision-api .
docker run --rm -p 8000:8000 --env-file .env dentalvision-api
```

## Docker Compose

```bash
docker compose up --build
```

This starts:
- the FastAPI backend on port `8000`
- a PostgreSQL database on port `5432`

To stop the stack:

```bash
docker compose down -v
```

## CI and quality checks

The repository includes a GitHub Actions workflow that runs:
- dependency installation
- Ruff linting
- pytest with coverage

Use the same checks locally:

```bash
make lint
make test
```

## Production deployment notes

For production:
- use a managed PostgreSQL database instead of the local compose service
- store secrets in environment variables or a secret manager
- mount a private storage volume for uploads and model artifacts
- keep `DEBUG` disabled and use a proper `SECRET_KEY`
- configure a reverse proxy or WSGI server in front of FastAPI if needed

## Recommended rollout checklist

- validate `.env` values
- ensure the trained model file exists and is referenced by `DENTALVISION_MODEL_PATH`
- test the `/api/v1/health` and `/api/v1/models` endpoints
- verify image upload and validation flows
- smoke-test the database connection
- confirm logs are captured centrally before production rollout
