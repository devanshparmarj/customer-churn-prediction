"""
schema.py — Pydantic request / response models.

Every field that flows in or out of the API is validated and documented here.
FastAPI reads these models to auto-generate the OpenAPI / Swagger spec.
"""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# REQUEST
# ---------------------------------------------------------------------------

class CustomerFeatures(BaseModel):
    """
    Raw customer attributes sent to POST /predict.

    Field names and allowed values mirror the IBM Telco Customer Churn
    dataset.  Numeric fields that were one-hot-encoded during training are
    kept as raw strings here; the predictor handles the transformation so
    the caller never has to think about feature engineering.
    """

    # ── Demographics ──────────────────────────────────────────────────────
    gender: Literal["Male", "Female"] = Field(
        ..., example="Male", description="Customer gender"
    )
    senior_citizen: Literal[0, 1] = Field(
        ..., example=0, description="1 if the customer is 65 or older, else 0"
    )
    partner: Literal["Yes", "No"] = Field(
        ..., example="Yes", description="Whether the customer has a partner"
    )
    dependents: Literal["Yes", "No"] = Field(
        ..., example="No", description="Whether the customer has dependents"
    )

    # ── Account info ──────────────────────────────────────────────────────
    tenure: int = Field(
        ..., ge=0, le=72, example=12,
        description="Number of months the customer has been with the company"
    )
    contract: Literal["Month-to-month", "One year", "Two year"] = Field(
        ..., example="Month-to-month", description="Contract type"
    )
    paperless_billing: Literal["Yes", "No"] = Field(
        ..., example="Yes", description="Whether the customer uses paperless billing"
    )
    payment_method: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ] = Field(..., example="Electronic check", description="Payment method")
    monthly_charges: float = Field(
        ..., ge=0, example=65.50, description="Monthly charge amount (USD)"
    )
    total_charges: float = Field(
        ..., ge=0, example=786.0, description="Total amount charged to date (USD)"
    )

    # ── Services ──────────────────────────────────────────────────────────
    phone_service: Literal["Yes", "No"] = Field(
        ..., example="Yes", description="Whether the customer has phone service"
    )
    multiple_lines: Literal["Yes", "No", "No phone service"] = Field(
        ..., example="No", description="Whether the customer has multiple lines"
    )
    internet_service: Literal["DSL", "Fiber optic", "No"] = Field(
        ..., example="Fiber optic", description="Internet service type"
    )
    online_security: Literal["Yes", "No", "No internet service"] = Field(
        ..., example="No", description="Whether the customer has online security"
    )
    online_backup: Literal["Yes", "No", "No internet service"] = Field(
        ..., example="No", description="Whether the customer has online backup"
    )
    device_protection: Literal["Yes", "No", "No internet service"] = Field(
        ..., example="No", description="Whether the customer has device protection"
    )
    tech_support: Literal["Yes", "No", "No internet service"] = Field(
        ..., example="No", description="Whether the customer has tech support"
    )
    streaming_tv: Literal["Yes", "No", "No internet service"] = Field(
        ..., example="Yes", description="Whether the customer streams TV"
    )
    streaming_movies: Literal["Yes", "No", "No internet service"] = Field(
        ..., example="Yes", description="Whether the customer streams movies"
    )

    # ── Custom validator: ensure total_charges >= monthly_charges ────────
    @field_validator("total_charges")
    @classmethod
    def total_must_exceed_monthly(cls, v: float, info) -> float:
        monthly = info.data.get("monthly_charges", 0)
        if monthly and v < monthly:
            raise ValueError(
                "total_charges must be >= monthly_charges "
                f"(got total={v}, monthly={monthly})"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
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
        }
    }


# ---------------------------------------------------------------------------
# RESPONSE
# ---------------------------------------------------------------------------

class PredictionResponse(BaseModel):
    """Structured prediction result returned by POST /predict."""

    prediction: Literal["Churn", "No Churn"] = Field(
        ..., description="Binary prediction outcome"
    )
    churn_probability: float = Field(
        ..., ge=0.0, le=1.0,
        description="Probability that the customer will churn (0–1)"
    )
    risk_level: Literal["Low", "Medium", "High"] = Field(
        ..., description="Human-readable churn risk bucket"
    )
    model_version: str = Field(
        ..., description="Version of the model that produced this result"
    )
    status: str = Field(default="success", description="Request outcome status")


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str = Field(..., example="healthy")
    model_loaded: bool = Field(..., description="True if the ML model is ready")
    app_version: str = Field(..., description="Running application version")


class RootResponse(BaseModel):
    """Response body for GET /."""

    message: str
    version: str
    docs_url: str


class ErrorResponse(BaseModel):
    """Standardised error payload."""

    status: str = Field(default="error")
    detail: str
    error_code: str
