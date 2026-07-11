# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final minimal image
# Use Google Distroless Python image for strict hardening (no bash/sh, no package manager)
FROM gcr.io/distroless/python3-debian12:nonroot

WORKDIR /app

# Copy dependencies and source code
COPY --from=builder /install /usr/local
COPY main.py .

# Configure python path to find copied site-packages
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Start application directly via python interpreter (no shell execution)
ENTRYPOINT ["/usr/bin/python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

