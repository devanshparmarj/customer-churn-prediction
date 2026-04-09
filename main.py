"""
main.py
-------
FastAPI backend for Customer Churn Prediction.
Run from project root:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import os
import logging
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schema import CustomerData, PredictionResponse, HealthResponse

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# MODEL PATH  – tries model/churn_model.pkl first,
#               falls back to ./pipeline.pkl in root
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_CANDIDATES = [
    os.path.join(BASE_DIR, "model", "churn_model.pkl"),
    os.path.join(BASE_DIR, "churn_model.pkl"),
    os.path.join(BASE_DIR, "pipeline.pkl"),          # legacy root-level file
    os.path.join(BASE_DIR, "model.pkl"),
]

def _find_model_path():
    for p in _CANDIDATES:
        if os.path.exists(p):
            return p
    return None

model_bundle: dict = {}

# ──────────────────────────────────────────────
# LIFESPAN – load model at startup
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Server starting – loading model …")
    path = _find_model_path()
    if path is None:
        logger.error("No model file found. Run train_model.py first.")
    else:
        logger.info(f"Loading model from: {path}")
        raw = joblib.load(path)

        # Support both bundle dict {"pipeline": ...} and bare pipeline object
        if isinstance(raw, dict) and "pipeline" in raw:
            model_bundle["pipeline"]             = raw["pipeline"]
            model_bundle["numeric_features"]     = raw.get("numeric_features",     ["tenure", "monthly_charges", "support_calls"])
            model_bundle["categorical_features"] = raw.get("categorical_features", ["contract_type", "internet_service"])
        else:
            # Bare sklearn pipeline saved directly
            model_bundle["pipeline"]             = raw
            model_bundle["numeric_features"]     = ["tenure", "monthly_charges", "support_calls"]
            model_bundle["categorical_features"] = ["contract_type", "internet_service"]

        logger.info("✅ Model loaded successfully.")

    yield
    logger.info("🛑 Server shutting down.")
    model_bundle.clear()

# ──────────────────────────────────────────────
# APP
# ──────────────────────────────────────────────
app = FastAPI(
    title="Customer Churn Prediction API",
    description="Predict customer churn probability using a RandomForest model.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def _risk_level(probability: float) -> str:
    if probability >= 0.70:
        return "High"
    elif probability >= 0.40:
        return "Medium"
    return "Low"

def _build_dataframe(data: CustomerData) -> pd.DataFrame:
    return pd.DataFrame([{
        "tenure":           data.tenure,
        "monthly_charges":  data.monthly_charges,
        "support_calls":    data.support_calls,
        "contract_type":    data.contract_type,
        "internet_service": data.internet_service,
    }])

# ──────────────────────────────────────────────
# ENDPOINTS
# ──────────────────────────────────────────────
@app.get("/", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(
        status="ok",
        model_loaded=bool(model_bundle),
        version="1.0.0",
    )

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_churn(customer: CustomerData):
    if not model_bundle:
        raise HTTPException(status_code=503, detail="Model not loaded. Run train_model.py first.")

    pipeline = model_bundle["pipeline"]

    try:
        X = _build_dataframe(customer)
        logger.info(f"Prediction request: {customer.model_dump()}")

        prediction  = int(pipeline.predict(X)[0])
        probability = round(float(pipeline.predict_proba(X)[0][1]), 4)
        risk        = _risk_level(probability)

        logger.info(f"Result → prediction={prediction}, prob={probability}, risk={risk}")

        return PredictionResponse(
            churn_prediction=prediction,
            churn_probability=probability,
            risk_level=risk,
        )
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(exc)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)