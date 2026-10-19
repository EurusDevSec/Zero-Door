FROM python:3.11-slim
WORKDIR /app
COPY event_pipeline/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY event_pipeline /app/event_pipeline
USER 65532:65532
ENTRYPOINT ["python", "-m", "event_pipeline.gateway"]
