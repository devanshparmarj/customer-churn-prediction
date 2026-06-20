"""
tests/test_predict.py — Unit & integration tests for the prediction endpoint.

Run with:
    pytest tests/ -v

The test suite uses pytest-asyncio + httpx.AsyncClient so every request
goes through the full FastAPI stack (middleware, validation, exception
handlers) without hitting a real network port.

Model artefacts are mocked via pytest fixtures so tests pass even when
`models/` is absent — e.g. in a bare CI environment.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch

from fastapi import status
from httpx import AsyncClient, ASGITransport

# ── Shared valid payload ──────────────────────────────────────────────────

VALID_PAYLOAD: dict = {
    "gender": "Male",
    "senior_citizen": 0,
    "partner": "Yes",
    "dependents": "No",
    "tenure": 12,
    "phone_service": "Yes",
    "multiple_lines": "No",
    "internet_service": "Fiber optic",
    "online_security": "No",
    "online_backup": "No",
    "device_protection": "No",
    "tech_support": "No",
    "streaming_tv": "Yes",
    "streaming_movies": "Yes",
    "contract": "Month-to-month",
    "paperless_billing": "Yes",
    "payment_method": "Electronic check",
    "monthly_charges": 65.50,
    "total_charges": 786.0,
}


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_predictor_load():
    """
    Patch ChurnPredictor.load so no .pkl files are needed during tests.
    The mock sets `_is_loaded = True` and injects a minimal feature list
    and a fake sklearn model that always returns a fixed probability.
    """
    import numpy as np

    fake_model = MagicMock()
    fake_model.predict_proba.return_value = np.array([[0.30, 0.70]])

    with patch("app.predictor.predictor") as mock_pred:
        mock_pred.is_loaded = True
        mock_pred.predict.return_value = MagicMock(
            prediction="Churn",
            churn_probability=0.70,
            risk_level="High",
            model_version="1.0.0",
            status="success",
            model_dump=lambda: {
                "prediction": "Churn",
                "churn_probability": 0.70,
                "risk_level": "High",
                "model_version": "1.0.0",
                "status": "success",
            },
        )
        yield mock_pred


@pytest_asyncio.fixture
async def client(mock_predictor_load):
    """Async HTTP client wired directly to the FastAPI app (no server needed)."""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


# ── Tests: GET / ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_root_returns_200(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_root_contains_docs_url(client: AsyncClient):
    data = response = await client.get("/")
    body = response.json()
    assert "docs_url" in body
    assert body["docs_url"] == "/docs"


# ── Tests: GET /health ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_returns_200_when_model_loaded(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_health_body_structure(client: AsyncClient):
    body = (await client.get("/health")).json()
    assert body["status"] == "healthy"
    assert body["model_loaded"] is True
    assert "app_version" in body


@pytest.mark.asyncio
async def test_health_returns_503_when_model_not_loaded(mock_predictor_load):
    mock_predictor_load.is_loaded = False
    from app.main import app
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.get("/health")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


# ── Tests: POST /predict — happy path ────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_returns_200_for_valid_payload(client: AsyncClient):
    response = await client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_predict_response_schema(client: AsyncClient):
    body = (await client.post("/predict", json=VALID_PAYLOAD)).json()
    assert "prediction" in body
    assert "churn_probability" in body
    assert "risk_level" in body
    assert "model_version" in body
    assert "status" in body


@pytest.mark.asyncio
async def test_predict_churn_label_is_valid(client: AsyncClient):
    body = (await client.post("/predict", json=VALID_PAYLOAD)).json()
    assert body["prediction"] in ("Churn", "No Churn")


@pytest.mark.asyncio
async def test_predict_risk_level_is_valid(client: AsyncClient):
    body = (await client.post("/predict", json=VALID_PAYLOAD)).json()
    assert body["risk_level"] in ("Low", "Medium", "High")


@pytest.mark.asyncio
async def test_predict_probability_in_range(client: AsyncClient):
    body = (await client.post("/predict", json=VALID_PAYLOAD)).json()
    assert 0.0 <= body["churn_probability"] <= 1.0


# ── Tests: POST /predict — validation errors ─────────────────────────────

@pytest.mark.asyncio
async def test_predict_returns_422_for_missing_field(client: AsyncClient):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "tenure"}
    response = await client.post("/predict", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_predict_returns_422_for_invalid_gender(client: AsyncClient):
    payload = {**VALID_PAYLOAD, "gender": "Unknown"}
    response = await client.post("/predict", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_predict_returns_422_for_negative_tenure(client: AsyncClient):
    payload = {**VALID_PAYLOAD, "tenure": -1}
    response = await client.post("/predict", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_predict_returns_422_when_total_less_than_monthly(client: AsyncClient):
    payload = {**VALID_PAYLOAD, "monthly_charges": 100.0, "total_charges": 50.0}
    response = await client.post("/predict", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ── Tests: POST /predict — service unavailable ────────────────────────────

@pytest.mark.asyncio
async def test_predict_returns_503_when_model_not_loaded(mock_predictor_load):
    mock_predictor_load.is_loaded = False
    from app.main import app
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        response = await ac.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
