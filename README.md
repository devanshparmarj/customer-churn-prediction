# 🔮 Customer Churn Prediction API

> A production-ready Machine Learning REST API that predicts telecom customer churn, built with **FastAPI**, **scikit-learn**, and **Docker**.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Overview

This project demonstrates an end-to-end ML deployment pipeline:

| Component | Technology |
|---|---|
| Dataset | IBM Telco Customer Churn |
| Model | Logistic Regression (sklearn) |
| API Framework | FastAPI + Pydantic v2 |
| Server | Gunicorn + Uvicorn workers |
| Containerisation | Docker multi-stage build |
| Testing | pytest + httpx async client |

**Model Performance**

| Metric | Score |
|---|---|
| Accuracy | 82% |
| Precision (Churn) | 70% |
| Recall (Churn) | 60% |
| F1 Score (Churn) | 64% |

---

## 🗂️ Project Structure

```
customer-churn-prediction/
│
├── app/
│   ├── main.py          # FastAPI app, routes, lifecycle hooks
│   ├── schema.py        # Pydantic request/response models
│   ├── predictor.py     # ML model loading & inference
│   ├── config.py        # Centralised settings (pydantic-settings)
│   └── logger.py        # Structured logging
│
├── models/
│   ├── churn_model.pkl  # Trained Logistic Regression model
│   └── features.pkl     # Ordered feature list for alignment
│
├── notebooks/           # EDA and training notebooks
├── tests/
│   └── test_predict.py  # Async unit & integration tests
│
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1 — Clone & install dependencies

```bash
git clone https://github.com/your-username/customer-churn-prediction.git
cd customer-churn-prediction

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2 — Place model artefacts

Copy your trained model files into `models/`:

```
models/churn_model.pkl
models/features.pkl
```

### 3 — Run locally

```bash
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## 🐳 Docker

### Build the image

```bash
docker build -t churn-prediction-api:latest .
```

### Run the container

```bash
docker run -d \
  --name churn-api \
  -p 8000:8000 \
  churn-prediction-api:latest
```

### Verify it's running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "app_version": "1.0.0"
}
```

### Stop & remove

```bash
docker stop churn-api && docker rm churn-api
```

---

## 🔌 API Reference

### `GET /`

Returns a welcome message and docs URL.

```json
{
  "message": "Welcome to the Customer Churn Prediction API",
  "version": "1.0.0",
  "docs_url": "/docs"
}
```

---

### `GET /health`

Liveness probe — returns `503` if the model isn't loaded.

```json
{
  "status": "healthy",
  "model_loaded": true,
  "app_version": "1.0.0"
}
```

---

### `POST /predict`

Predict churn for a single customer.

**Request body:**

```json
{
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
  "total_charges": 786.0
}
```

**Response:**

```json
{
  "prediction": "Churn",
  "churn_probability": 0.7243,
  "risk_level": "High",
  "model_version": "1.0.0",
  "status": "success"
}
```

**Risk level thresholds:**

| Risk Level | Probability Range |
|---|---|
| Low | < 0.35 |
| Medium | 0.35 – 0.65 |
| High | > 0.65 |

---

## 🧪 Testing

```bash
pytest tests/ -v
```

The test suite covers:
- ✅ Root and health endpoints
- ✅ Valid prediction request (happy path)
- ✅ Response schema validation
- ✅ Missing required fields → 422
- ✅ Invalid enum values → 422
- ✅ Negative tenure → 422
- ✅ total_charges < monthly_charges → 422
- ✅ Model not loaded → 503

---

## 🌐 Postman Collection

Import the following cURL commands into Postman:

**GET /health**
```bash
curl -X GET http://localhost:8000/health
```

**POST /predict**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
    "total_charges": 786.0
  }'
```

---

## ⚙️ Configuration

All settings are managed via environment variables (or `.env` file):

| Variable | Default | Description |
|---|---|---|
| `DEBUG` | `false` | Enable debug logging |
| `MODEL_PATH` | `models/churn_model.pkl` | Path to model artefact |
| `FEATURES_PATH` | `models/features.pkl` | Path to feature list |
| `LOW_RISK_THRESHOLD` | `0.35` | Probability below which risk is "Low" |
| `HIGH_RISK_THRESHOLD` | `0.65` | Probability above which risk is "High" |
| `PORT` | `8000` | Server port |

---

## 🛣️ Recruiter-Facing Improvements (Roadmap)

- [ ] **MLflow / DVC** – experiment tracking and model versioning
- [ ] **CI/CD pipeline** – GitHub Actions: lint → test → build → push to Docker Hub
- [ ] **Model monitoring** – data drift detection with Evidently AI
- [ ] **Batch prediction endpoint** – `POST /predict/batch` for CSV uploads
- [ ] **Feature importance endpoint** – expose SHAP values per prediction
- [ ] **PostgreSQL logging** – persist predictions for audit trails
- [ ] **Redis caching** – cache repeated identical requests
- [ ] **Rate limiting** – `slowapi` middleware
- [ ] **Authentication** – JWT Bearer token via `python-jose`
- [ ] **Kubernetes manifests** – Helm chart for production deployment
- [ ] **Prometheus metrics** – `/metrics` endpoint for observability

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

## 🙋 Author

Built as a portfolio project demonstrating production ML engineering practices.
Feel free to fork, star ⭐, and adapt!
