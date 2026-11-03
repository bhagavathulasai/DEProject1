from __future__ import annotations

from api_app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "model_loaded" in payload
    assert "upload_dir" in payload
    assert "api_version" in payload


def test_models_endpoint_returns_list() -> None:
    response = client.get("/api/v1/models")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1
    assert payload[0]["status"] in {"loaded", "missing"}
