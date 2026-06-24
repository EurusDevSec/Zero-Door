# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final minimal image
FROM python:3.11-slim AS runner

WORKDIR /app

# Create a non-privileged user and group
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser -d /home/appuser -m appuser

# Copy installed python libraries from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source code
COPY main.py .

# Assign ownership to appuser
RUN chown -R appuser:appuser /app

# Configure non-root environment
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8000

# Start application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
