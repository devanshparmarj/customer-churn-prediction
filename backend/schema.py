"""
schema.py  —  Pydantic models for the 11-feature churn API
"""
from pydantic import BaseModel, Field, field_validator
from typing import Literal


class CustomerData(BaseModel):
    # ── Numeric ──────────────────────────────────────────────
    tenure: int = Field(..., ge=0, le=120,
        description="Months the customer has been with the company.",
        examples=[12])

    monthly_charges: float = Field(..., ge=0, le=500,
        description="Monthly subscription cost in USD.",
        examples=[70.5])

    total_charges: float = Field(..., ge=0,
        description="Total revenue from the customer to date.",
        examples=[846.0])

    support_calls: int = Field(..., ge=0, le=50,
        description="Number of support/complaint calls in the past year.",
        examples=[2])

    # ── Categorical ───────────────────────────────────────────
    contract_type: Literal["Month-to-month", "One year", "Two year"] = Field(
        ..., examples=["Month-to-month"])

    internet_service: Literal["DSL", "Fiber optic", "No"] = Field(
        ..., examples=["Fiber optic"])

    payment_method: Literal[
        "Credit card", "Bank transfer", "Electronic check", "Mailed check"
    ] = Field(..., examples=["Electronic check"])

    tech_support: Literal["Yes", "No"] = Field(..., examples=["No"])

    online_security: Literal["Yes", "No"] = Field(..., examples=["No"])

    streaming_services: Literal["Yes", "No"] = Field(..., examples=["Yes"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenure": 12,
                "monthly_charges": 70.5,
                "total_charges": 846.0,
                "support_calls": 2,
                "contract_type": "Month-to-month",
                "internet_service": "Fiber optic",
                "payment_method": "Electronic check",
                "tech_support": "No",
                "online_security": "No",
                "streaming_services": "Yes",
            }
        }
    }


class PredictionResponse(BaseModel):
    churn_prediction: int
    churn_probability: float
    risk_level: Literal["Low", "Medium", "High"]

    model_config = {
        "json_schema_extra": {
            "example": {
                "churn_prediction": 1,
                "churn_probability": 0.87,
                "risk_level": "High",
            }
        }
    }


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str
    features: int
