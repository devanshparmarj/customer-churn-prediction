"""
config.py — Centralised application settings.

All environment-driven configuration lives here.  Import `settings`
anywhere in the codebase; never hard-code paths or constants elsewhere.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Resolve the project root regardless of where the process is started from.
# Structure: project_root/app/config.py  →  project_root = parent.parent
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings — values can be overridden via environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── API metadata ──────────────────────────────────────────────────────
    app_name: str = "Customer Churn Prediction API"
    app_version: str = "1.0.0"
    app_description: str = (
        "Production-ready ML API for predicting customer churn "
        "using a Logistic Regression model trained on the IBM Telco dataset."
    )
    debug: bool = False

    # ── Model artefact paths ──────────────────────────────────────────────
    model_path: Path = PROJECT_ROOT / "models" / "churn_model.pkl"
    features_path: Path = PROJECT_ROOT / "models" / "features.pkl"

    # ── Risk-level probability thresholds ─────────────────────────────────
    # Below LOW_THRESHOLD  → "Low"
    # LOW_THRESHOLD to HIGH_THRESHOLD → "Medium"
    # Above HIGH_THRESHOLD → "High"
    low_risk_threshold: float = 0.35
    high_risk_threshold: float = 0.65

    # ── Server (used by Uvicorn if launched via __main__) ─────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1


# Module-level singleton — import this everywhere
settings = Settings()
