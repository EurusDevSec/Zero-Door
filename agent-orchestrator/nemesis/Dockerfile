# ---- Stage 1: Build dependencies ----
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Runtime ----
FROM python:3.11-slim

# Run as non-root (use nobody user already present in slim image)
WORKDIR /app

COPY --from=builder /install /usr/local
COPY main.py .
COPY static ./static

# nobody user (65534) already exists in python:3.11-slim
USER nobody

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
