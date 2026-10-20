FROM zero-door/events:zer-9-cd87da425168
WORKDIR /app
ENV PYTHONPATH=/app
COPY measurement /app/measurement
COPY event_pipeline /app/event_pipeline
COPY live /app/live
ENTRYPOINT ["python", "-B", "/app/live/acceptance.py", "serve"]
