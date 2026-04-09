"""
schema.py
---------
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal


class CustomerData(BaseModel):
    tenure: int = Field(..., ge=0, le=120, description="Months with company (0–120).", examples=[12])
    monthly_charges: float = Field(..., ge=0, le=500, description="Monthly bill in USD.", examples=[70.5])
    contract_type: Literal["Month-to-month", "One year", "Two year"] = Field(..., examples=["Month-to-month"])
    internet_service: Literal["DSL", "Fiber optic", "No"] = Field(..., examples=["Fiber optic"])
    support_calls: int = Field(..., ge=0, le=50, description="Support calls in the past year.", examples=[2])

    @field_validator("support_calls")
    @classmethod
    def calls_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("support_calls must be >= 0")
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


class PredictionResponse(BaseModel):
    churn_prediction: int = Field(..., description="1 = will churn, 0 = will not churn.")
    churn_probability: float = Field(..., description="Confidence score (0.0–1.0).")
    risk_level: Literal["Low", "Medium", "High"]

    model_config = {
        "json_schema_extra": {
            "example": {
                "churn_prediction": 1,
                "churn_probability": 0.82,
                "risk_level": "High",
            }
        }
    }


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str