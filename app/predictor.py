"""
predictor.py — ML model loading and inference logic.

This module owns the entire ML lifecycle inside the API:
  1. Load model artefacts from disk at startup (singleton pattern).
  2. Transform raw Pydantic input into a feature-aligned DataFrame.
  3. Run inference and map probabilities to human-readable risk levels.

Design principles
-----------------
* The predictor is a class (ChurnPredictor) so it can carry state (the
  loaded model + feature list) without relying on global variables.
* A module-level `predictor` singleton is created at import time so
  FastAPI's lifespan handler can validate it once on boot.
* All heavy imports (pandas, numpy, joblib) stay inside this module;
  the rest of the app never touches them directly.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.config import settings
from app.logger import get_logger
from app.schema import CustomerFeatures, PredictionResponse

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helper: map raw CustomerFeatures to a flat dict with column names that
# match the dataset (capital letters, spaces) that was used during training.
# ---------------------------------------------------------------------------

_FIELD_TO_COLUMN: dict[str, str] = {
    "gender": "gender",
    "senior_citizen": "SeniorCitizen",
    "partner": "Partner",
    "dependents": "Dependents",
    "tenure": "tenure",
    "phone_service": "PhoneService",
    "multiple_lines": "MultipleLines",
    "internet_service": "InternetService",
    "online_security": "OnlineSecurity",
    "online_backup": "OnlineBackup",
    "device_protection": "DeviceProtection",
    "tech_support": "TechSupport",
    "streaming_tv": "StreamingTV",
    "streaming_movies": "StreamingMovies",
    "contract": "Contract",
    "paperless_billing": "PaperlessBilling",
    "payment_method": "PaymentMethod",
    "monthly_charges": "MonthlyCharges",
    "total_charges": "TotalCharges",
}


class ChurnPredictor:
    """
    Loads and serves the churn prediction model.

    Parameters
    ----------
    model_path : Path
        Path to the serialised sklearn model (.pkl).
    features_path : Path
        Path to the list of feature names used during training (.pkl).
    """

    def __init__(self, model_path: Path, features_path: Path) -> None:
        self._model_path = model_path
        self._features_path = features_path
        self._model: Any = None
        self._features: list[str] = []
        self._is_loaded: bool = False

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def load(self) -> None:
        """
        Deserialise model and feature list from disk.

        Called once during application startup.  Raises RuntimeError if
        either artefact is missing so the process fails fast.
        """
        logger.info("Loading model artefacts…")
        t0 = time.perf_counter()

        if not self._model_path.exists():
            raise RuntimeError(f"Model file not found: {self._model_path}")
        if not self._features_path.exists():
            raise RuntimeError(f"Features file not found: {self._features_path}")

        self._model = joblib.load(self._model_path)
        self._features = joblib.load(self._features_path)

        elapsed = time.perf_counter() - t0
        logger.info(
            "Model loaded successfully",
            extra={
                "elapsed_ms": round(elapsed * 1000, 2),
                "n_features": len(self._features),
            },
        )
        self._is_loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    # ── Inference ─────────────────────────────────────────────────────────

    def predict(self, customer: CustomerFeatures) -> PredictionResponse:
        """
        Run inference for a single customer.

        Steps:
          1. Convert Pydantic model → flat dict with training column names.
          2. Build a one-row DataFrame.
          3. Align columns to the exact feature order stored in features.pkl
             (fills missing columns with 0 so the pipeline never errors).
          4. Call model.predict_proba → extract churn probability.
          5. Map probability → risk level and prediction label.

        Returns a fully-populated PredictionResponse.
        """
        if not self._is_loaded:
            raise RuntimeError("Model is not loaded. Call .load() first.")

        # 1 & 2 — Build DataFrame with correct column names
        raw: dict[str, Any] = {
            _FIELD_TO_COLUMN[field]: value
            for field, value in customer.model_dump().items()
        }
        df = pd.DataFrame([raw])

        # 3 — One-hot-encode categoricals (same strategy used at training time)
        df_encoded = pd.get_dummies(df)

        # Align to training feature order:
        #   • Columns present in training but missing here → fill with 0
        #   • Extra columns in input (shouldn't happen) → drop silently
        df_aligned = df_encoded.reindex(columns=self._features, fill_value=0)

        logger.debug(
            "Feature alignment complete",
            extra={"input_cols": list(df_encoded.columns), "aligned_cols": list(df_aligned.columns)},
        )

        # 4 — Inference
        t0 = time.perf_counter()
        proba: np.ndarray = self._model.predict_proba(df_aligned)
        churn_prob: float = float(proba[0][1])  # probability of class=1 (Churn)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)

        # 5 — Derive prediction label and risk level
        prediction_label = "Churn" if churn_prob >= 0.5 else "No Churn"
        risk_level = self._map_risk_level(churn_prob)

        logger.info(
            "Prediction complete",
            extra={
                "prediction": prediction_label,
                "churn_probability": round(churn_prob, 4),
                "risk_level": risk_level,
                "inference_ms": elapsed_ms,
            },
        )

        return PredictionResponse(
            prediction=prediction_label,
            churn_probability=round(churn_prob, 4),
            risk_level=risk_level,
            model_version=settings.app_version,
            status="success",
        )

    # ── Internal helpers ──────────────────────────────────────────────────

    def _map_risk_level(self, probability: float) -> str:
        """Convert a churn probability to a Low / Medium / High bucket."""
        if probability < settings.low_risk_threshold:
            return "Low"
        if probability < settings.high_risk_threshold:
            return "Medium"
        return "High"


# ---------------------------------------------------------------------------
# Module-level singleton
# The FastAPI app imports and uses this object directly.
# ---------------------------------------------------------------------------

predictor = ChurnPredictor(
    model_path=settings.model_path,
    features_path=settings.features_path,
)
