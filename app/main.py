"""
main.py — FastAPI application entry point.

Registers all routes, startup/shutdown lifecycle hooks, and global
exception handlers.  Keep this file thin — business logic lives in
predictor.py, data contracts in schema.py.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.logger import get_logger
from app.predictor import predictor
from app.schema import (
    CustomerFeatures,
    ErrorResponse,
    HealthResponse,
    PredictionResponse,
    RootResponse,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifespan context — runs startup & shutdown logic once per process
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Load model on startup; log clean shutdown on exit."""
    logger.info("Starting %s v%s…", settings.app_name, settings.app_version)
    try:
        predictor.load()
        logger.info("Application ready to serve requests.")
    except RuntimeError as exc:
        # A missing model file is a fatal misconfiguration — exit loudly.
        logger.error("FATAL: could not load model artefacts. %s", exc)
        raise

    yield  # application runs here

    logger.info("Shutting down %s.", settings.app_name)


# ---------------------------------------------------------------------------
# FastAPI app instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
    # Serve Swagger UI at /docs and ReDoc at /redoc
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (adjust origins for production) ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Lock down to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler: return a structured JSON error instead of a 500 traceback."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="An unexpected internal error occurred.",
            error_code="INTERNAL_SERVER_ERROR",
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return HTTPExceptions as structured JSON (not FastAPI's default plain dict)."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
        ).model_dump(),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get(
    "/",
    response_model=RootResponse,
    summary="API root",
    tags=["General"],
)
async def root() -> RootResponse:
    """Welcome endpoint — confirms the API is reachable."""
    return RootResponse(
        message=f"Welcome to the {settings.app_name}",
        version=settings.app_version,
        docs_url="/docs",
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["General"],
    responses={
        503: {"description": "Service unavailable — model not loaded", "model": ErrorResponse},
    },
)
async def health_check() -> HealthResponse:
    """
    Kubernetes / load-balancer liveness probe.

    Returns HTTP 200 when the model is loaded and ready to serve.
    Returns HTTP 503 if the model failed to load at startup.
    """
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. The service is not ready.",
        )
    return HealthResponse(
        status="healthy",
        model_loaded=predictor.is_loaded,
        app_version=settings.app_version,
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict customer churn",
    tags=["Prediction"],
    status_code=status.HTTP_200_OK,
    responses={
        422: {"description": "Validation error — invalid input fields", "model": ErrorResponse},
        503: {"description": "Model not available", "model": ErrorResponse},
    },
)
async def predict_churn(customer: CustomerFeatures) -> PredictionResponse:
    """
    Predict whether a customer is likely to churn.

    ### Returns
    - **prediction** – `"Churn"` or `"No Churn"`
    - **churn_probability** – probability score between 0 and 1
    - **risk_level** – `"Low"` (< 0.35) / `"Medium"` (0.35–0.65) / `"High"` (> 0.65)
    - **model_version** – version tag of the serving model
    """
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction service is temporarily unavailable.",
        )

    try:
        result: PredictionResponse = predictor.predict(customer)
    except Exception as exc:
        logger.exception("Prediction failed for request payload.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(exc)}",
        ) from exc

    return result


# ---------------------------------------------------------------------------
# Dev entry point (not used by Docker / Gunicorn)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers,
    )
