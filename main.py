import os
import sys
import logging
from contextlib import asynccontextmanager

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import our Pydantic models
from schema import CustomerData, PredictionResponse, HealthResponse

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# MODEL PATH  (relative to project root)
# ──────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "churn_model.pkl")

# Global container for the loaded model bundle
model_bundle: dict = {}


# ──────────────────────────────────────────────
# LIFESPAN  –  load model at startup
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the ML model when the server starts; clean up on shutdown."""
    logger.info("🚀  Server starting – loading model …")
    if not os.path.exists(MODEL_PATH):
        logger.error(f"Model file not found at {MODEL_PATH}. Run train_model.py first.")
        # Allow server to start even without model (health check will report it)
    else:
        bundle = joblib.load(MODEL_PATH)
        model_bundle["pipeline"]            = bundle["pipeline"]
        model_bundle["numeric_features"]    = bundle["numeric_features"]
        model_bundle["categorical_features"] = bundle["categorical_features"]
        logger.info("✅  Model loaded successfully.")
    yield
    logger.info("🛑  Server shutting down.")
    model_bundle.clear()


# ──────────────────────────────────────────────
# APP INSTANCE
# ──────────────────────────────────────────────
app = FastAPI(
    title="Customer Churn Prediction API",
    description=(
        "Send customer data to **/predict** and get back a churn probability "
        "plus a risk-level label (Low / Medium / High). "
        "Powered by a RandomForestClassifier trained on telecom data."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ──────────────────────────────────────────────
# CORS  –  allow any frontend origin (tighten for production)
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # replace with your UI's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# HELPER
# ──────────────────────────────────────────────
def _risk_level(probability: float) -> str:
    """Convert raw probability to a human-readable risk bucket."""
    if probability >= 0.70:
        return "High"
    elif probability >= 0.40:
        return "Medium"
    return "Low"


def _build_dataframe(data: CustomerData) -> pd.DataFrame:
    """Convert the Pydantic request model into a single-row DataFrame."""
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
def health_check() -> HealthResponse:
    """
    Basic health check.
    Returns server status and whether the ML model is loaded.
    """
    return HealthResponse(
        status="ok",
        model_loaded=bool(model_bundle),
        version="1.0.0",
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_churn(customer: CustomerData) -> PredictionResponse:
   
    # Guard: model must be loaded
    if not model_bundle:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please run model/train_model.py first.",
        )

    pipeline = model_bundle["pipeline"]

    try:
        # Build input DataFrame from validated request body
        X = _build_dataframe(customer)
        logger.info(f"Prediction request: {customer.model_dump()}")

        # Run inference
        prediction  = int(pipeline.predict(X)[0])
        probability = float(pipeline.predict_proba(X)[0][1])
        probability = round(probability, 4)
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


# ──────────────────────────────────────────────
# LOCAL DEV ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
