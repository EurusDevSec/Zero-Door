# ---- Stage 1: Build dependencies ----
FROM python:3.11-slim@sha256:e529028263dbe6910a2d96f7d2b8f5266385e917fd45d286ef166977c094a51e AS builder

WORKDIR /app

COPY nemesis/requirements.lock .
RUN pip install --no-cache-dir --prefix=/install --require-hashes -r requirements.lock

# ---- Stage 2: Runtime ----
# Use Google Distroless Python image for strict hardening (no bash/sh, no package manager)
FROM gcr.io/distroless/python3-debian12:nonroot@sha256:0f8ca62dea61023c1fe02e445bd154ee02b2d97aec377f965ae3c641ec838e61

WORKDIR /app

# Copy dependencies and source code
COPY --from=builder /install /usr/local
COPY nemesis/main.py .
COPY nemesis/command_guard.py /nemesis/command_guard.py
COPY nemesis/measurement_view.py /nemesis/measurement_view.py
COPY nemesis/session.py /nemesis/session.py
COPY nemesis/session_cli.py /nemesis/session_cli.py
COPY event_pipeline /event_pipeline
COPY nemesis/static ./static

# Configure python path to find copied site-packages
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages:/
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Start application directly via python interpreter (no shell execution)
ENTRYPOINT ["/usr/bin/python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

