"""
schema.py
---------
Pydantic models for request/response validation in the FastAPI backend.
Pydantic automatically validates types and raises clear HTTP 422 errors
when the client sends invalid data.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal


# ──────────────────────────────────────────────
# REQUEST BODY  –  data sent by the UI / client
# ──────────────────────────────────────────────
class CustomerData(BaseModel):
    """
    Represents one customer record for churn prediction.
    All fields include descriptions that appear in the /docs UI.
    """

    tenure: int = Field(
        ...,
        ge=0, le=120,
        description="Number of months the customer has been with the company (0–120).",
        examples=[12],
    )

    monthly_charges: float = Field(
        ...,
        ge=0, le=500,
        description="Monthly bill in USD.",
        examples=[70.5],
    )

    contract_type: Literal["Month-to-month", "One year", "Two year"] = Field(
        ...,
        description="Customer contract length.",
        examples=["Month-to-month"],
    )

    internet_service: Literal["DSL", "Fiber optic", "No"] = Field(
        ...,
        description="Type of internet service subscribed to.",
        examples=["Fiber optic"],
    )

    support_calls: int = Field(
        ...,
        ge=0, le=50,
        description="Number of calls to customer support in the past year.",
        examples=[2],
    )

    # Extra validation example: support_calls can't be negative
    @field_validator("support_calls")
    @classmethod
    def calls_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("support_calls must be ≥ 0")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenure": 12,
                "monthly_charges": 70.5,
                "contract_type": "Month-to-month",
                "internet_service": "Fiber optic",
                "support_calls": 2,
            }
        }
    }


# ──────────────────────────────────────────────
# RESPONSE BODY  –  data returned to the client
# ──────────────────────────────────────────────
class PredictionResponse(BaseModel):
    """Churn prediction result returned by /predict."""

    churn_prediction: int = Field(
        ...,
        description="Binary prediction: 1 = will churn, 0 = will not churn.",
    )
    churn_probability: float = Field(
        ...,
        description="Model confidence that the customer will churn (0.0–1.0).",
    )
    risk_level: Literal["Low", "Medium", "High"] = Field(
        ...,
        description="Human-readable risk bucket derived from churn_probability.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "churn_prediction": 1,
                "churn_probability": 0.82,
                "risk_level": "High",
            }
        }
    }


# ──────────────────────────────────────────────
# HEALTH CHECK RESPONSE
# ──────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str
