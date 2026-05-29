# syntax=docker/dockerfile:1
# ResolveOne — single image: FastAPI serves the /api AND the built React UI on :8000.

# ── stage 1: build the React UI to static files ──────────────────────────────
FROM node:20-alpine AS ui-build
WORKDIR /ui
COPY ui/package*.json ./
RUN npm install
COPY ui/ ./
RUN npm run build

# ── stage 2: python runtime (agent + API + built UI) ─────────────────────────
FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# app code + mock-data fixtures (explicit copies keep the image lean)
COPY server.py models.py config.py util.py ./
COPY core ./core
COPY adapters ./adapters
COPY data ./data
# built frontend from stage 1
COPY --from=ui-build /ui/dist ./ui/dist

# run as non-root (k8s-friendly); /app stays writable for the append-only audit log
RUN useradd -u 10001 -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
# ANTHROPIC_API_KEY (optional) -> live Haiku/Sonnet; absent -> offline deterministic mock
# --no-server-header / --no-date-header: drop the Server and Date response headers
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header", "--no-date-header"]
