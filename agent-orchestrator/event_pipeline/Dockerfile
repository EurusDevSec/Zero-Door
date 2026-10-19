FROM python:3.11-slim@sha256:e529028263dbe6910a2d96f7d2b8f5266385e917fd45d286ef166977c094a51e
WORKDIR /app
COPY event_pipeline/requirements.lock /app/requirements.lock
RUN pip install --no-cache-dir --require-hashes -r requirements.lock
COPY event_pipeline /app/event_pipeline
USER 65532:65532
ENTRYPOINT ["python", "-m", "event_pipeline.gateway"]
