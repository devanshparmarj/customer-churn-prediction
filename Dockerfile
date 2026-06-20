# ─────────────────────────────────────────────────────────────────────────
# Stage 1 — Builder
# Install Python dependencies in an isolated layer so that the final image
# doesn't contain build tools (gcc, pip cache, etc.).
# ─────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Set working directory for the build stage
WORKDIR /build

# Copy only the dependency manifest first (Docker layer-cache optimisation:
# this layer is rebuilt only when requirements.txt changes).
COPY requirements.txt .

# Install dependencies into a prefix directory we'll copy to the final stage
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ─────────────────────────────────────────────────────────────────────────
# Stage 2 — Runtime image
# ─────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# ── Security: run as a non-root user ─────────────────────────────────────
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Working directory inside the container
WORKDIR /app

# Pull in installed packages from the builder stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY app/       ./app/
COPY models/    ./models/

# ── Runtime environment variables ────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# ── Health check (used by Docker Compose / Kubernetes) ───────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# ── Start the server with Gunicorn + Uvicorn workers ─────────────────────
# Gunicorn manages worker processes; each worker runs an async Uvicorn loop.
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
