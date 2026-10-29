import os
import sys
import math
from pathlib import Path
import json
import time
import asyncio
import logging
import uuid
import threading
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from kafka import KafkaProducer, KafkaConsumer
from openai import OpenAI
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nemesis.command_guard import CommandGuard, Refused, strict_json, sign, fields, identifier
from nemesis.measurement_view import ResultError, ResultsStore, authorize_reader

# ---- Logging Buffer for Dashboard ----
NEMESIS_LOG_BUFFER = []

class BufferHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            NEMESIS_LOG_BUFFER.insert(0, msg)
            if len(NEMESIS_LOG_BUFFER) > 50:
                NEMESIS_LOG_BUFFER.pop()
        except Exception:
            self.handleError(record)

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger("nemesis-agent")

# Attach buffer handler to catch logs in memory
buf_handler = BufferHandler()
buf_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"))
logger.addHandler(buf_handler)

# ---- Configuration ----
KAFKA_BOOTSTRAP_SERVERS   = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka.zero-door.svc.cluster.local:9092")
KAFKA_COMMANDS_TOPIC      = os.getenv("KAFKA_COMMANDS_TOPIC", "attack.commands")
KAFKA_RESULTS_TOPIC       = os.getenv("KAFKA_RESULTS_TOPIC", "attack.results")
KAFKA_GROUP_ID            = os.getenv("KAFKA_GROUP_ID", "nemesis-group")
PROMETHEUS_URL            = os.getenv("PROMETHEUS_URL", "http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090")
HEPHAESTUS_URL            = os.getenv("HEPHAESTUS_URL", "http://hephaestus.zero-door.svc.cluster.local:8000")

LLM_PROVIDER              = os.getenv("NEMESIS_LLM_PROVIDER", "openai")   # openai | ollama | gemini
OPENAI_API_KEY            = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL              = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_BASE_URL           = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL              = os.getenv("OLLAMA_MODEL", "llama3")

# Gemini Round Robin config
GEMINI_API_KEYS_RAW       = os.getenv("GEMINI_API_KEYS", "")
GEMINI_API_KEYS           = [k.strip() for k in GEMINI_API_KEYS_RAW.split(",") if k.strip()]
GEMINI_MODEL              = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

ALLOWED_NAMESPACES        = ["target-app"]
MAX_ATTACK_DURATION_SEC   = int(os.getenv("MAX_ATTACK_DURATION_SEC", "60"))
MAX_LLM_TOKENS            = 500
LLM_REQUEST_INTERVAL_SEC  = 6  # max 10 calls/min

app = FastAPI(title="Nemesis Agent — AI Attack Strategist")

# ---- Kafka clients ----
kafka_producer: Optional[KafkaProducer] = None
kafka_consumer: Optional[KafkaConsumer] = None

# ---- LLM client ----
llm_client: Optional[OpenAI] = None

# ---- Gemini API Round Robin State ----
gemini_keys_lock = threading.Lock()
gemini_key_index = 0

def get_next_gemini_key() -> str:
    global gemini_key_index
    if not GEMINI_API_KEYS:
        return OPENAI_API_KEY
    with gemini_keys_lock:
        key = GEMINI_API_KEYS[gemini_key_index]
        gemini_key_index = (gemini_key_index + 1) % len(GEMINI_API_KEYS)
        return key

def get_kafka_producer() -> KafkaProducer:
    global kafka_producer
    if kafka_producer is None:
        try:
            kafka_producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks="all",
                retries=3,
                request_timeout_ms=10000,
            )
            logger.info("Kafka producer initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
    return kafka_producer


def get_llm_client(api_key: Optional[str] = None) -> OpenAI:
    global llm_client
    if LLM_PROVIDER == "ollama":
        if llm_client is None:
            llm_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama", max_retries=0, timeout=10.0)
            logger.info(f"LLM client initialized (Ollama) — model: {OLLAMA_MODEL}")
        return llm_client
    elif LLM_PROVIDER == "gemini":
        key = api_key or get_next_gemini_key()
        if not key:
            raise RuntimeError("Gemini API key is not set. Set GEMINI_API_KEYS environment variable.")
        # Google Generative Language API supports OpenAI compatibility endpoint
        return OpenAI(api_key=key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/", max_retries=0, timeout=10.0)
    else:
        if llm_client is None:
            if not OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY is not set. Set it or use NEMESIS_LLM_PROVIDER=ollama.")
            llm_client = OpenAI(api_key=OPENAI_API_KEY, max_retries=0, timeout=10.0)
            logger.info(f"LLM client initialized (OpenAI) — model: {OPENAI_MODEL}")
        return llm_client


# ---- Pydantic models ----

class AttackCommand(BaseModel):
    commandId: str
    timestamp: str
    source: str = "nemesis"
    attackType: str
    target: dict
    parameters: dict
    safetyLimits: dict


class TriggerAttackRequest(BaseModel):
    attackType: str                  # HTTP_FLOOD | CPU_STRESS | MEMORY_STRESS | POD_KILL
    targetService: str               # e.g. "frontend"
    targetNamespace: str = "target-app"
    targetURL: str = ""
    durationSec: int = 30
    intensity: str = "LOW"           # LOW | MEDIUM | HIGH
    concurrency: int = 10


# ---- Helper: build AttackCommand dict ----

def build_attack_command(
    attack_type: str,
    target_service: str,
    target_namespace: str,
    target_url: str,
    duration_sec: int,
    intensity: str,
    concurrency: int,
) -> dict:
    return {
        "commandId": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "nemesis",
        "attackType": attack_type,
        "target": {
            "namespace": target_namespace,
            "service": target_service,
            "url": target_url,
        },
        "parameters": {
            "duration": duration_sec,
            "intensity": intensity,
            "concurrency": concurrency,
            "customParams": {},
        },
        "safetyLimits": {
            "maxDuration": MAX_ATTACK_DURATION_SEC,
            "allowedNamespaces": ALLOWED_NAMESPACES,
        },
    }


# ---- Prometheus helper ----

async def get_system_summary() -> str:
    """Fetch a brief metrics summary from Prometheus to feed the LLM context."""
    import httpx
    summary_lines = []

    queries = {
        "cpu_total": 'sum(rate(container_cpu_usage_seconds_total{namespace="target-app", container!=""}[2m]))',
        "mem_total_mb": 'sum(container_memory_working_set_bytes{namespace="target-app", container!=""})/1024/1024',
        # Requests through the Traefik ingress to target-app backends (target-app-<service>-<port>@kubernetes)
        "http_rps": 'sum(rate(traefik_service_requests_total{service=~"target-app-.+@kubernetes"}[2m]))',
        "error_rate": 'sum(rate(traefik_service_requests_total{service=~"target-app-.+@kubernetes", code=~"5.."}[2m])) / sum(rate(traefik_service_requests_total{service=~"target-app-.+@kubernetes"}[2m]))',
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            for name, query in queries.items():
                r = await client.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
                if r.status_code == 200:
                    data = r.json().get("data", {}).get("result", [])
                    if data:
                        val = float(data[0].get("value", [0, "0"])[1])
                        summary_lines.append(f"- {name}: {round(val, 4)}")
    except Exception as e:
        logger.warning(f"Could not fetch Prometheus metrics for LLM context: {e}")

    if not summary_lines:
        return "No metrics available. Target app may be idle."
    return "\n".join(summary_lines)


# ---- LLM Attack Plan Generator ----

ATTACK_PLAN_SYSTEM_PROMPT = """You are Nemesis, an AI red-team agent for a security chaos engineering platform called Zero Door.
Your job is to generate ONE attack command targeting the microservices application running in the 'target-app' Kubernetes namespace.

You MUST respond ONLY with a valid JSON object matching this exact schema (no markdown, no explanation):
{
  "attackType": "<HTTP_FLOOD|CPU_STRESS|MEMORY_STRESS|POD_KILL>",
  "targetService": "<kubernetes service name, e.g. frontend>",
  "targetNamespace": "target-app",
  "targetURL": "<cluster-internal URL if HTTP attack, else empty string>",
  "durationSec": <integer 10-60>,
  "intensity": "<LOW|MEDIUM|HIGH>",
  "concurrency": <integer 1-100>,
  "reasoning": "<A brief 1-2 sentence explanation in Vietnamese of why you targeted this service and attack type based on the metrics>"
}

Rules:
- targetNamespace MUST be "target-app"
- targetURL MUST end with ".target-app.svc.cluster.local" or be empty
- durationSec MUST be between 10 and 60
- Only choose from these services: frontend, cartservice, productcatalogservice, currencyservice, checkoutservice, redis-cart
- Choose the most interesting attack based on current system metrics
"""

async def call_gemini_native(api_key: str, model: str, system_prompt: str, user_prompt: str) -> str:
    import httpx
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": MAX_LLM_TOKENS
        }
    }
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            logger.error("Model HTTP failure: %s", response.status_code)
            raise RuntimeError(f"Gemini API returned status {response.status_code}")
        res_json = response.json()
        try:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error("Unexpected model response structure")
            raise RuntimeError("Failed to parse response from Gemini API")


async def generate_attack_plan_from_llm() -> Optional[dict]:
    """Use OpenAI/Ollama/Gemini to generate an intelligent attack plan."""
    if LLM_PROVIDER == "ollama":
        model = OLLAMA_MODEL
    elif LLM_PROVIDER == "gemini":
        model = GEMINI_MODEL
    else:
        model = OPENAI_MODEL

    try:
        metrics_ctx = await get_system_summary()
        user_message = f"""Current system metrics from Prometheus:
{metrics_ctx}

Based on these metrics, generate ONE attack command to stress-test the weakest component.
Remember to only target the 'target-app' namespace. Respond ONLY with valid JSON."""

        raw_output = None
        if LLM_PROVIDER == "gemini":
            # Attempt failover round robin over all available keys
            keys_to_try = list(GEMINI_API_KEYS) if GEMINI_API_KEYS else [OPENAI_API_KEY]
            global gemini_key_index
            with gemini_keys_lock:
                start_idx = gemini_key_index
                # advance index for the next call sequence
                gemini_key_index = (gemini_key_index + 1) % len(keys_to_try) if keys_to_try else 0

            # Order keys starting from start_idx
            ordered_keys = keys_to_try[start_idx:] + keys_to_try[:start_idx]

            last_err = None
            for idx, key in enumerate(ordered_keys[:1]):
                if not key:
                    continue
                logger.info("Starting one bounded model attempt.")
                try:
                    raw_output = await call_gemini_native(
                        api_key=key,
                        model=model,
                        system_prompt=ATTACK_PLAN_SYSTEM_PROMPT,
                        user_prompt=user_message
                    )
                    # If call succeeds, break out of retry loop
                    break
                except Exception as e:
                    logger.warning("Model attempt failed: %s", type(e).__name__)
                    last_err = e
                    continue

            if raw_output is None:
                raise RuntimeError(f"All Gemini API keys failed. Last error: {last_err}")
        else:
            client = get_llm_client()
            logger.info(f"Sending request to LLM ({LLM_PROVIDER} / {model})...")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": ATTACK_PLAN_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=MAX_LLM_TOKENS,
                temperature=0.7,
            )
            raw_output = response.choices[0].message.content.strip()

        logger.info("Model response received; raw plan is not written to the dashboard log.")

        # Strip markdown code fences if present
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```")[1]
            if raw_output.startswith("json"):
                raw_output = raw_output[4:]

        plan = strict_json(raw_output.encode())
        return plan

    except json.JSONDecodeError as e:
        logger.error(f"LLM output was not valid JSON: {e}")
        return None
    except Exception as e:
        logger.error("Model call failed: %s", type(e).__name__)
        return None


# ---- Attack result consumer loop ----

async def consume_results_loop():
    """Keep blocking Kafka I/O off FastAPI's event loop, with one consumer owner."""
    logger.info("Starting Kafka results consumer loop...")
    stop = threading.Event()

    def run_consumer():
        # KafkaConsumer is not thread-safe: construct, poll and close on this worker.
        while not stop.is_set():
            consumer = None
            try:
                consumer = KafkaConsumer(
                    KAFKA_RESULTS_TOPIC,
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
                    group_id=KAFKA_GROUP_ID,
                    auto_offset_reset="latest",
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    consumer_timeout_ms=1000,
                )
                while not stop.is_set():
                    try:
                        records = consumer.poll(timeout_ms=1000)
                        for batch in records.values():
                            for msg in batch:
                                result = msg.value
                                status = result.get("status", "UNKNOWN")
                                cmd_id = result.get("commandId", "?")
                                atype = result.get("attackType", "?")
                                dur_ms = result.get("duration", 0)
                                details = result.get("details", {})
                                log_fn = logger.info if status == "SUCCESS" else logger.warning
                                log_fn(f"[RESULT] commandId={cmd_id} type={atype} status={status} "
                                       f"durationMs={dur_ms} details={details}")
                    except Exception as e:
                        logger.error(f"Error in results consumer: {e}")
                        stop.wait(1)
            except Exception as e:
                logger.error(f"Failed to initialize results consumer: {e}")
                stop.wait(1)
            finally:
                if consumer is not None:
                    try:
                        consumer.close()
                    except Exception as e:
                        logger.error(f"Error closing results consumer: {e}")

    worker = asyncio.create_task(asyncio.to_thread(run_consumer))
    try:
        await asyncio.shield(worker)
    finally:
        stop.set()
        # Do not close the consumer concurrently with an outstanding poll.
        await worker


# ---- FastAPI startup ----

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_results_loop())
    logger.info("Nemesis Agent started. Results consumer loop running.")


# ---- REST API Endpoints ----

@app.get("/")
def root():
    return {
        "status": "UP",
        "agent": "nemesis",
        "llm_provider": LLM_PROVIDER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/healthz")
def healthz():
    try:
        producer = get_kafka_producer()
        kafka_ok = producer is not None
    except Exception:
        kafka_ok = False
    return {
        "status": "UP",
        "kafka_connected": kafka_ok,
        "llm_provider": LLM_PROVIDER,
    }


@app.middleware("http")
async def command_boundary(request: Request, call_next):
    if request.url.path.startswith("/api/results"):
        # S results: read-only, and only with the separate results-reader key. The operator key is
        # refused here, so the O console cannot open labels or scores while a run is in progress.
        if request.method != "GET":
            return JSONResponse({"detail": "READ_ONLY"}, status_code=405, headers=NO_STORE)
        try:
            authorize_reader(request.headers.get("Authorization"))
        except Refused as error:
            return JSONResponse({"detail": error.reason}, status_code=error.status, headers=NO_STORE)
        return await call_next(request)
    if request.method == "GET" and (request.url.path.startswith("/api/") or request.url.path == "/attack/status"):
        try:
            CommandGuard.from_env().authorize(request.headers.get("Authorization"))
        except Refused as error:
            return JSONResponse({"detail": error.reason}, status_code=error.status)
    if request.method == "POST":
        try:
            guard = CommandGuard.from_env()
            request.state.operator = guard.authorize(request.headers.get("Authorization"))
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 16384:
                    raise Refused("PAYLOAD_SIZE", 413)
            request.state.command_body = strict_json(bytes(body) or b"{}")
            request.state.command_guard = guard
            # All legacy writes are covered, including reset/chat routes.
            if request.url.path not in {"/attack/trigger", "/attack/llm-plan", "/api/chat/clear"}:
                raise Refused("RESET_REQUIRES_HARNESS", 409)
        except Refused as error:
            logger.warning("Command refused: %s", error.reason)
            return JSONResponse({"detail": error.reason}, status_code=error.status)
    response = await call_next(request)
    if request.url.path.startswith("/dashboard"):
        # Revalidate pages/scripts on every load (ETag/304), so a browser never runs an old KPI script.
        response.headers["Cache-Control"] = "no-cache"
    return response


def publish_command(guard, command, key):
    producer = get_kafka_producer()
    if producer is None:
        raise Refused("PRODUCER_UNAVAILABLE", 503)
    # Wait for broker acknowledgement. A failure leaves a durable unknown claim.
    producer.send(KAFKA_COMMANDS_TOPIC, sign(command, key)).get(timeout=10)
    return {"status": "PUBLISHED", "commandId": command["commandId"]}


@app.post("/attack/trigger", summary="Submit an authenticated bounded command")
def trigger_attack(request: Request):
    ledger, claimed, sent = None, False, False
    try:
        guard = request.state.command_guard
        guard.enabled()
        request_id = identifier(request.headers.get("Idempotency-Key"))
        command = guard.command(request.state.command_body, request_id)
        key = guard.signer()  # Validate before taking a durable claim.
        ledger = guard.ledger()
        previous = ledger.claim(request_id, {"path": request.url.path, "body": request.state.command_body, "policy": guard.policy})
        if previous is not None:
            if previous.get("status") == "REFUSED":
                raise Refused(previous["reason"], previous["http_status"])
            return previous
        claimed = True
        producer = get_kafka_producer()
        if producer is None:
            raise Refused("PRODUCER_UNAVAILABLE", 503)
        envelope = sign(command, key)
        # A send invocation is the uncertainty boundary, even if it raises.
        sent = True
        producer.send(KAFKA_COMMANDS_TOPIC, envelope).get(timeout=10)
        result = {"status": "PUBLISHED", "commandId": command["commandId"]}
        ledger.complete(request_id, result)
        return result
    except Refused as error:
        if sent:
            logger.error("Command outcome unknown after send: %s", error.reason)
            raise HTTPException(503, "OUTCOME_UNKNOWN")
        if claimed and not sent:
            try:
                ledger.complete(request_id, {"status": "REFUSED", "reason": error.reason, "http_status": error.status, "commandId": request_id})
            except Refused:
                raise HTTPException(503, "OUTCOME_UNKNOWN")
        logger.warning("Command refused: %s", error.reason)
        raise HTTPException(error.status, error.reason)
    except Exception as error:
        if claimed and not sent:
            try:
                ledger.complete(request_id, {"status": "REFUSED", "reason": "PRE_PUBLISH_FAILED", "http_status": 503, "commandId": request_id})
            except Refused:
                raise HTTPException(503, "OUTCOME_UNKNOWN")
            logger.error("Command refused before send: %s", type(error).__name__)
            raise HTTPException(503, "PRE_PUBLISH_FAILED")
        logger.error("Command outcome unknown: %s", type(error).__name__)
        raise HTTPException(503, "OUTCOME_UNKNOWN")


@app.post("/attack/llm-plan", summary="Plan only after authenticated, bounded admission")
async def llm_attack_plan(request: Request):
    ledger, claimed, published = None, False, False
    try:
        guard = request.state.command_guard
        guard.enabled()
        guard.allow_model()
        fields(request.state.command_body, set())
        request_id = identifier(request.headers.get("Idempotency-Key"))
        key = guard.signer()
        ledger = guard.ledger()
        previous = ledger.claim(request_id, {"path": request.url.path, "body": {}, "policy": guard.policy})
        if previous is not None:
            if previous.get("status") == "REFUSED":
                raise Refused(previous["reason"], previous["http_status"])
            return previous
        claimed = True
        plan = await generate_attack_plan_from_llm()
        if type(plan) is not dict:
            raise Refused("PLAN_INVALID", 503)
        # The model has no power to expand target/budget/schema. Reasoning is not executed.
        candidate = dict(plan)
        candidate.pop("reasoning", None)
        command = guard.command(candidate, request_id)
        result = publish_command(guard, command, key)
        published = True
        ledger.complete(request_id, result)
        return result
    except Refused as error:
        if claimed and not published:
            try:
                ledger.complete(request_id, {"status": "REFUSED", "reason": error.reason, "http_status": error.status, "commandId": request_id})
            except Refused:
                raise HTTPException(503, "OUTCOME_UNKNOWN")
        logger.warning("Command refused: %s", error.reason)
        raise HTTPException(error.status, error.reason)
    except Exception as error:
        logger.error("Plan outcome unknown: %s", type(error).__name__)
        raise HTTPException(503, "OUTCOME_UNKNOWN")


@app.get("/attack/status", summary="Check pending and recent attack results")
def attack_status():
    """Returns a brief status summary (placeholder — full tracking via Kafka logs)."""
    return {
        "message": "Use Kafka topic 'attack.results' or check Grafana/Elasticsearch for detailed attack results.",
        "kafkaResultsTopic": KAFKA_RESULTS_TOPIC,
        "kafkaCommandsTopic": KAFKA_COMMANDS_TOPIC,
    }


# ---- Dashboard Support REST APIs ----

def get_service_name(pod_name: str) -> str:
    if "-stress-" in pod_name:
        return pod_name.split("-stress-")[0]
    parts = pod_name.split("-")
    if len(parts) >= 3:
        return "-".join(parts[:-2])
    return pod_name


DASHBOARD_SERVICES = ("frontend", "cartservice", "productcatalogservice", "currencyservice", "checkoutservice",
                      "redis-cart", "shippingservice", "paymentservice", "emailservice")
NO_STORE = {"Cache-Control": "no-store"}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sample_value(result):
    """A finite Prometheus sample value, or None: an unparsable sample is no data, never 0."""
    try:
        value = float(result.get("value", [None, None])[1])
    except (TypeError, ValueError, IndexError, AttributeError):
        return None
    return value if math.isfinite(value) else None


@app.get("/api/status", summary="Live O telemetry: replicas and CPU per service, with the source state")
async def get_api_status():
    # null is no data for that service; 0 is reported only when Prometheus answered 0.
    services_status = {name: {"replicas": None, "cpu": None} for name in DASHBOARD_SERVICES}
    errors = []
    queries = {
        "replicas": 'kube_deployment_status_replicas{namespace="target-app"}',
        # include zero-door for stress pods
        "cpu": 'sum(rate(container_cpu_usage_seconds_total{namespace=~"target-app|zero-door", container!=""}[2m])) by (pod)',
    }
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            for name, query in queries.items():
                r = await client.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
                if r.status_code != 200:
                    errors.append(f"{name.upper()}_HTTP_{r.status_code}")
                    continue
                try:
                    results = r.json().get("data", {}).get("result", [])
                except (ValueError, AttributeError):
                    errors.append(f"{name.upper()}_MALFORMED")
                    continue
                for res in results if isinstance(results, list) else []:
                    value = sample_value(res) if isinstance(res, dict) else None
                    if value is None:
                        continue
                    labels = res.get("metric") if isinstance(res.get("metric"), dict) else {}
                    if name == "replicas":
                        if labels.get("deployment") in services_status:
                            services_status[labels["deployment"]]["replicas"] = int(value)
                    else:
                        svc_name = get_service_name(str(labels.get("pod") or ""))
                        if svc_name in services_status:
                            services_status[svc_name]["cpu"] = (services_status[svc_name]["cpu"] or 0.0) + value
    except Exception as e:
        logger.warning("Error querying Prometheus for dashboard: %s", type(e).__name__)
        errors.append("UPSTREAM_UNREACHABLE")
    state = "OK" if not errors else "PARTIAL" if len(errors) < len(queries) and "UPSTREAM_UNREACHABLE" not in errors else "ERROR"
    return {"services": services_status,
            "source": {"name": "prometheus", "status": state, "errors": errors, "fetched_at": utc_now(),
                       "note": "live O telemetry, not a KPI"}}


@app.get("/api/logs", summary="Get combined real-time logs from Nemesis and Hephaestus")
async def get_api_logs():
    combined_logs = []

    # Add local Nemesis logs
    for log in NEMESIS_LOG_BUFFER:
        if len(log) > 24:
            combined_logs.append({
                "timestamp": log[:19].replace(" ", "T") + "Z",
                "message": log[24:]
            })

    # Fetch Hephaestus logs; a failed fetch is reported, not shown as "no actions".
    hephaestus_state = "OK"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{HEPHAESTUS_URL}/heal/history")
            if r.status_code == 200:
                resp_json = r.json()
                # /heal/history returns {"total": N, "history": [...]}
                if isinstance(resp_json, dict):
                    heal_history = resp_json.get("history", [])
                elif isinstance(resp_json, list):
                    heal_history = resp_json
                else:
                    heal_history = []
                for event in heal_history:
                    if not isinstance(event, dict):
                        continue
                    ts = str(event.get("timestamp", ""))[:19]
                    svc = event.get("service", "")
                    act = event.get("action", "")
                    status = event.get("status", "")
                    msg = f"[HEPHAESTUS] Action={act} | Service={svc} | Status={status}"
                    combined_logs.append({
                        "timestamp": ts if ts.endswith("Z") else ts + "Z",
                        "message": msg
                    })
            else:
                hephaestus_state = f"HTTP_{r.status_code}"
    except Exception as e:
        logger.warning("Could not fetch Hephaestus logs: %s", type(e).__name__)
        hephaestus_state = "UNREACHABLE"

    # Sort logs descending (newest first)
    combined_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    # Operational text only: not KPI evidence and not LLM decisions.
    return {"logs": combined_logs[:50], "sources": {"nemesis": "OK", "hephaestus": hephaestus_state}, "fetched_at": utc_now()}


@app.get("/api/chat", summary="Decision reasoning stream: unavailable in R1")
async def get_api_chat():
    # The former stream wrote fixed sentences from heal history and CPU readings and showed them as
    # agent reasoning. R1 has no LLM decision producer, so nothing is shown and nothing is generated.
    return {"chat": [], "status": "UNAVAILABLE", "reason": "NO_DECISION_PRODUCER_IN_R1",
            "note": "no AI reasoning is generated or replayed; decisions are read from scored results only"}


@app.post("/api/chat/clear", summary="Compatibility no-op: there is no reasoning history to clear")
def clear_reasoning_chat():
    return {"status": "UNAVAILABLE", "reason": "NO_DECISION_PRODUCER_IN_R1"}


@app.post("/api/reset", summary="Reset experiment and clean log buffers")
async def api_reset():
    # No proxy using an operator's token as Hephaestus authority, and no false success.
    raise HTTPException(409, "RESET_REQUIRES_HARNESS")


@app.get("/api/heal-history", summary="Proxy: Hephaestus heal history (legacy audit, never a KPI source)")
async def get_heal_history_proxy():
    """Proxy endpoint — an unreachable or failing Hephaestus is an error, not an empty history."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{HEPHAESTUS_URL}/heal/history")
    except Exception as e:
        logger.warning("Could not proxy Hephaestus heal history: %s", type(e).__name__)
        raise HTTPException(503, "UPSTREAM_UNAVAILABLE")
    if r.status_code != 200:
        raise HTTPException(502, f"UPSTREAM_HTTP_{r.status_code}")
    try:
        return r.json()
    except ValueError:
        raise HTTPException(502, "UPSTREAM_MALFORMED")


# ---- S results: registered runs only, read-only (nemesis/measurement_view.py) ----

def result_error(error):
    # Reason codes only: no filesystem path, key or exception text leaves the server.
    return JSONResponse({"detail": error.reason}, status_code=error.status, headers=NO_STORE)


@app.get("/api/results/runs", summary="Registered, closed runs with scorer artifacts")
def results_runs():
    try:
        return JSONResponse({"runs": ResultsStore.from_env().runs(), "checked_at": utc_now()}, headers=NO_STORE)
    except ResultError as error:
        return result_error(error)


@app.get("/api/results/runs/{run_id}", summary="KPI view of one registered run, passed through from score.json")
def results_run(run_id: str):
    try:
        view = ResultsStore.from_env().view(run_id)
    except ResultError as error:
        return result_error(error)
    view["served_at"] = utc_now()
    return JSONResponse(view, headers=NO_STORE)


@app.get("/api/results/runs/{run_id}/files/{name}", summary="The same export files the view was read from")
def results_file(run_id: str, name: str):
    try:
        data, digest = ResultsStore.from_env().file(run_id, name)
    except ResultError as error:
        return result_error(error)
    media = "application/json" if name.endswith(".json") else "text/csv; charset=utf-8"
    return Response(content=data, media_type=media, headers=dict(NO_STORE, **{
        "X-ZD-SHA256": digest, "Content-Disposition": f'attachment; filename="{run_id}-{name}"'}))


# ---- Mount Dashboard Static Files ----
try:
    app.mount("/dashboard", StaticFiles(directory="static", html=True), name="dashboard")
except Exception as e:
    logger.warning(f"Failed to mount static directory: {e}")
