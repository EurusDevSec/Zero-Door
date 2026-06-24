import os
import json
import time
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kafka import KafkaProducer, KafkaConsumer
from openai import OpenAI

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger("nemesis-agent")

# ---- Configuration ----
KAFKA_BOOTSTRAP_SERVERS   = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka.zero-door.svc.cluster.local:9092")
KAFKA_COMMANDS_TOPIC      = os.getenv("KAFKA_COMMANDS_TOPIC", "attack.commands")
KAFKA_RESULTS_TOPIC       = os.getenv("KAFKA_RESULTS_TOPIC", "attack.results")
KAFKA_GROUP_ID            = os.getenv("KAFKA_GROUP_ID", "nemesis-group")
PROMETHEUS_URL            = os.getenv("PROMETHEUS_URL", "http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090")

LLM_PROVIDER              = os.getenv("NEMESIS_LLM_PROVIDER", "openai")   # openai | ollama
OPENAI_API_KEY            = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL              = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_BASE_URL           = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL              = os.getenv("OLLAMA_MODEL", "llama3")

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


def get_llm_client() -> OpenAI:
    global llm_client
    if llm_client is None:
        if LLM_PROVIDER == "ollama":
            llm_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
            logger.info(f"LLM client initialized (Ollama) — model: {OLLAMA_MODEL}")
        else:
            if not OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY is not set. Set it or use NEMESIS_LLM_PROVIDER=ollama.")
            llm_client = OpenAI(api_key=OPENAI_API_KEY)
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
        "http_rps": 'sum(rate(nginx_ingress_controller_requests{namespace="target-app"}[2m]))',
        "error_rate": 'sum(rate(nginx_ingress_controller_requests{status=~"5..", namespace="target-app"}[2m])) / sum(rate(nginx_ingress_controller_requests{namespace="target-app"}[2m]))',
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
  "concurrency": <integer 1-100>
}

Rules:
- targetNamespace MUST be "target-app"
- targetURL MUST end with ".target-app.svc.cluster.local" or be empty
- durationSec MUST be between 10 and 60
- Only choose from these services: frontend, cartservice, productcatalogservice, currencyservice, checkoutservice, redis-cart
- Choose the most interesting attack based on current system metrics
"""

async def generate_attack_plan_from_llm() -> Optional[dict]:
    """Use OpenAI/Ollama to generate an intelligent attack plan."""
    model = OLLAMA_MODEL if LLM_PROVIDER == "ollama" else OPENAI_MODEL
    try:
        client = get_llm_client()
        metrics_ctx = await get_system_summary()

        user_message = f"""Current system metrics from Prometheus:
{metrics_ctx}

Based on these metrics, generate ONE attack command to stress-test the weakest component.
Remember to only target the 'target-app' namespace. Respond ONLY with valid JSON."""

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
        logger.info(f"LLM raw output: {raw_output}")

        # Strip markdown code fences if present
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```")[1]
            if raw_output.startswith("json"):
                raw_output = raw_output[4:]

        plan = json.loads(raw_output)
        logger.info(f"LLM attack plan parsed: {plan}")
        return plan

    except json.JSONDecodeError as e:
        logger.error(f"LLM output was not valid JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return None


# ---- Attack result consumer loop ----

async def consume_results_loop():
    """Background task: consume attack results from Kafka and log them."""
    logger.info("Starting Kafka results consumer loop...")
    consumer = KafkaConsumer(
        KAFKA_RESULTS_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset="latest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=1000,
    )
    while True:
        try:
            for msg in consumer:
                result = msg.value
                status  = result.get("status", "UNKNOWN")
                cmd_id  = result.get("commandId", "?")
                atype   = result.get("attackType", "?")
                dur_ms  = result.get("duration", 0)
                details = result.get("details", {})

                log_fn = logger.info if status == "SUCCESS" else logger.warning
                log_fn(f"[RESULT] commandId={cmd_id} type={atype} status={status} "
                       f"durationMs={dur_ms} details={details}")
        except Exception as e:
            logger.error(f"Error in results consumer: {e}")
        await asyncio.sleep(1)


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


@app.post("/attack/trigger", summary="Manually trigger a specific attack command")
def trigger_attack(req: TriggerAttackRequest):
    """Manually send an attack command directly (bypasses LLM)."""
    if req.targetNamespace not in ALLOWED_NAMESPACES:
        raise HTTPException(status_code=400, detail=f"Namespace '{req.targetNamespace}' is not allowed.")

    command = build_attack_command(
        attack_type=req.attackType,
        target_service=req.targetService,
        target_namespace=req.targetNamespace,
        target_url=req.targetURL,
        duration_sec=req.durationSec,
        intensity=req.intensity,
        concurrency=req.concurrency,
    )

    producer = get_kafka_producer()
    if producer is None:
        raise HTTPException(status_code=503, detail="Kafka producer not available.")

    producer.send(KAFKA_COMMANDS_TOPIC, command)
    producer.flush()
    logger.info(f"Manual attack command sent: {command}")

    return {"message": "Attack command sent to Kafka.", "commandId": command["commandId"], "command": command}


@app.post("/attack/llm-plan", summary="Use LLM to generate and send an intelligent attack plan")
async def llm_attack_plan():
    """Ask the LLM to generate an attack plan based on current system metrics."""
    plan = await generate_attack_plan_from_llm()
    if plan is None:
        raise HTTPException(status_code=500, detail="LLM failed to generate a valid attack plan.")

    command = build_attack_command(
        attack_type=plan.get("attackType", "HTTP_FLOOD"),
        target_service=plan.get("targetService", "frontend"),
        target_namespace=plan.get("targetNamespace", "target-app"),
        target_url=plan.get("targetURL", ""),
        duration_sec=min(int(plan.get("durationSec", 30)), MAX_ATTACK_DURATION_SEC),
        intensity=plan.get("intensity", "LOW"),
        concurrency=min(int(plan.get("concurrency", 10)), 100),
    )

    producer = get_kafka_producer()
    if producer is None:
        raise HTTPException(status_code=503, detail="Kafka producer not available.")

    producer.send(KAFKA_COMMANDS_TOPIC, command)
    producer.flush()
    logger.info(f"LLM-generated attack command sent: {command}")

    return {"message": "LLM attack plan sent to Kafka.", "commandId": command["commandId"], "plan": plan, "command": command}


@app.get("/attack/status", summary="Check pending and recent attack results")
def attack_status():
    """Returns a brief status summary (placeholder — full tracking via Kafka logs)."""
    return {
        "message": "Use Kafka topic 'attack.results' or check Grafana/Elasticsearch for detailed attack results.",
        "kafkaResultsTopic": KAFKA_RESULTS_TOPIC,
        "kafkaCommandsTopic": KAFKA_COMMANDS_TOPIC,
    }
