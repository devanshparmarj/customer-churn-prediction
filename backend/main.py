"""
main.py  —  FastAPI backend (11-feature churn model)
Run: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""
import os, logging
import joblib, pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schema import CustomerData, PredictionResponse, HealthResponse

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "churn_model.pkl")

model_bundle: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀  Loading model …")
    if os.path.exists(MODEL_PATH):
        bundle = joblib.load(MODEL_PATH)
        model_bundle.update(bundle)
        logger.info("✅  Model loaded.")
    else:
        logger.error(f"Model not found at {MODEL_PATH}. Run train_model.py first.")
    yield
    model_bundle.clear()


app = FastAPI(
    title="Customer Churn Prediction API",
    description="11-feature RandomForest churn predictor. POST to /predict with customer data.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


def _risk(p: float) -> str:
    return "High" if p >= 0.70 else "Medium" if p >= 0.40 else "Low"


def _to_df(data: CustomerData) -> pd.DataFrame:
    return pd.DataFrame([{
        "tenure":             data.tenure,
        "monthly_charges":    data.monthly_charges,
        "total_charges":      data.total_charges,
        "support_calls":      data.support_calls,
        "contract_type":      data.contract_type,
        "internet_service":   data.internet_service,
        "payment_method":     data.payment_method,
        "tech_support":       data.tech_support,
        "online_security":    data.online_security,
        "streaming_services": data.streaming_services,
    }])


@app.get("/", response_model=HealthResponse, tags=["Health"])
def health():
    return HealthResponse(
        status="ok",
        model_loaded=bool(model_bundle),
        version="2.0.0",
        features=10,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(customer: CustomerData):
    if not model_bundle:
        raise HTTPException(503, "Model not loaded. Run model/train_model.py first.")
    try:
        X    = _to_df(customer)
        pred = int(model_bundle["pipeline"].predict(X)[0])
        prob = round(float(model_bundle["pipeline"].predict_proba(X)[0][1]), 4)
        logger.info(f"pred={pred} prob={prob} risk={_risk(prob)}")
        return PredictionResponse(
            churn_prediction=pred,
            churn_probability=prob,
            risk_level=_risk(prob),
        )
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
