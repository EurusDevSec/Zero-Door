# ZER-41 SQLi catalog fixture. Pure Python standard library + SQLite: no third-party dependency, so no
# requirements.lock and no build stage. Base image pinned by digest, same distroless runtime and nonroot
# user as the agent images (agent-orchestrator/*/Dockerfile). NOT_BUILT in this package: offline recipe only.
FROM gcr.io/distroless/python3-debian12:nonroot@sha256:0f8ca62dea61023c1fe02e445bd154ee02b2d97aec377f965ae3c641ec838e61

WORKDIR /app

COPY app.py .
COPY containment.py .
COPY seed.json .

# /data is the only writable path (the SQLite file), supplied as a volume; the image root stays read-only.
ENV ZD_SQLI_DB_DIR=/data \
    ZD_SQLI_SEED=/app/seed.json \
    ZD_SQLI_HOST=0.0.0.0 \
    ZD_SQLI_PORT=9140 \
    ZD_SQLI_PROFILE=safe \
    PYTHONUNBUFFERED=1

EXPOSE 9140

# Direct interpreter, no shell. The default profile is safe; the vulnerable profile is turned on only by
# overriding ZD_SQLI_PROFILE in a lab run that has been approved for it.
ENTRYPOINT ["/usr/bin/python3", "/app/app.py"]
