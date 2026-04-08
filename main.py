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
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# MODEL PATH (FIXED)
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "churn_model.pkl")

logger.info(f"📁 Looking for model at: {MODEL_PATH}")

# Global model container
model_bundle = {}

# ──────────────────────────────────────────────
# LIFESPAN
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Server starting – loading model...")

    if not os.path.exists(MODEL_PATH):
        logger.error(f"❌ Model file NOT found at: {MODEL_PATH}")
    else:
        try:
            bundle = joblib.load(MODEL_PATH)

            model_bundle["pipeline"] = bundle["pipeline"]
            model_bundle["numeric_features"] = bundle["numeric_features"]
            model_bundle["categorical_features"] = bundle["categorical_features"]

            logger.info("✅ Model loaded successfully")

        except Exception as e:
            logger.error(f"❌ MODEL LOAD ERROR: {e}")

    yield

    logger.info("🛑 Server shutting down")
    model_bundle.clear()

# ──────────────────────────────────────────────
# APP
# ──────────────────────────────────────────────
app = FastAPI(
    title="Customer Churn Prediction API",
    version="1.0.0",
    lifespan=lifespan
)

# ──────────────────────────────────────────────
# CORS
# ──────────────────────────────────────────────
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
        "tenure": data.tenure,
        "monthly_charges": data.monthly_charges,
        "support_calls": data.support_calls,
        "contract_type": data.contract_type,
        "internet_service": data.internet_service,
    }])

# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────
@app.get("/", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        model_loaded=bool(model_bundle),
        version="1.0.0",
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(customer: CustomerData):

    if not model_bundle:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        X = _build_dataframe(customer)
        pipeline = model_bundle["pipeline"]

        prediction = int(pipeline.predict(X)[0])
        probability = float(pipeline.predict_proba(X)[0][1])
        probability = round(probability, 4)

        return PredictionResponse(
            churn_prediction=prediction,
            churn_probability=probability,
            risk_level=_risk_level(probability),
        )

    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────
# LOCAL RUN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)