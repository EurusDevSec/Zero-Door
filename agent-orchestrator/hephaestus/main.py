import os
import json
import time
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Tuple

from fastapi import FastAPI
from kafka import KafkaConsumer, KafkaProducer
from kubernetes import client as k8s_client, config as k8s_config
from kubernetes.client.rest import ApiException

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger("hephaestus-agent")

# ---- Configuration ----
KAFKA_BOOTSTRAP_SERVERS  = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka.zero-door.svc.cluster.local:9092")
KAFKA_ALERTS_TOPIC       = os.getenv("KAFKA_ALERTS_TOPIC", "monitoring.alerts")
KAFKA_HEALING_TOPIC      = os.getenv("KAFKA_HEALING_TOPIC", "healing.actions")
KAFKA_LOGS_TOPIC         = os.getenv("KAFKA_LOGS_TOPIC", "system.logs")
KAFKA_GROUP_ID           = os.getenv("KAFKA_GROUP_ID", "hephaestus-defender-group")
TARGET_NAMESPACE         = os.getenv("TARGET_NAMESPACE", "target-app")
HEALING_COOLDOWN_SEC     = int(os.getenv("HEALING_COOLDOWN_SEC", "90"))
MAX_REPLICAS             = int(os.getenv("MAX_REPLICAS", "3"))
NETWORK_POLICY_TTL_SEC   = int(os.getenv("NETWORK_POLICY_TTL_SEC", "300"))  # 5 min auto-expire

app = FastAPI(title="Hephaestus Agent — Self-Healing Executor")

# ---- State ----
# Key: (service, action), Value: last heal timestamp
heal_cooldowns: Dict[Tuple[str, str], float] = {}

# In-memory audit log — last 200 heal events (for Phase 5 experiment polling)
heal_history: list = []
MAX_HISTORY = 200

# ---- Kafka clients ----
kafka_producer: Optional[KafkaProducer] = None

# ---- K8s clients ----
core_v1: Optional[k8s_client.CoreV1Api] = None
apps_v1: Optional[k8s_client.AppsV1Api] = None
networking_v1: Optional[k8s_client.NetworkingV1Api] = None


def init_k8s():
    """Initialise Kubernetes API clients using in-cluster or local config."""
    global core_v1, apps_v1, networking_v1
    try:
        if os.getenv("KUBERNETES_SERVICE_HOST"):
            k8s_config.load_incluster_config()
            logger.info("Using in-cluster Kubernetes config.")
        else:
            k8s_config.load_kube_config()
            logger.info("Using local kubeconfig.")
        core_v1      = k8s_client.CoreV1Api()
        apps_v1      = k8s_client.AppsV1Api()
        networking_v1 = k8s_client.NetworkingV1Api()
        logger.info("Kubernetes API clients initialized.")
    except Exception as e:
        logger.error(f"Failed to initialise Kubernetes clients: {e}")


def get_kafka_producer() -> Optional[KafkaProducer]:
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
            logger.error(f"Failed to initialise Kafka producer: {e}")
    return kafka_producer


# ---- Healing Decision Matrix ----
# Maps (alert_type, severity) → healing action
DECISION_MATRIX = {
    ("HIGH_CPU",        "WARNING"):  "SCALE_UP",
    ("HIGH_CPU",        "CRITICAL"): "RESTART",
    ("HIGH_MEMORY",     "WARNING"):  "RESTART",
    ("HIGH_MEMORY",     "CRITICAL"): "RESTART",
    ("HIGH_ERROR_RATE", "WARNING"):  "SCALE_UP",
    ("HIGH_ERROR_RATE", "CRITICAL"): "ROLLBACK",
    ("POD_CRASH",       "WARNING"):  "RESTART",
    ("POD_CRASH",       "CRITICAL"): "RESTART",
    ("HIGH_LATENCY",    "WARNING"):  "SCALE_UP",
    ("HIGH_LATENCY",    "CRITICAL"): "SCALE_UP",
    ("SUSPICIOUS_LOG",  "CRITICAL"): "BLOCK_IP",
}


def decide_action(alert_type: str, severity: str) -> Optional[str]:
    """Determine healing action from the decision matrix."""
    action = DECISION_MATRIX.get((alert_type, severity))
    if not action:
        # Fallback: try with WARNING severity
        action = DECISION_MATRIX.get((alert_type, "WARNING"))
    return action


# ---- Cooldown check ----

def is_in_cooldown(service: str, action: str) -> bool:
    key = (service, action)
    last = heal_cooldowns.get(key)
    if last and (time.time() - last) < HEALING_COOLDOWN_SEC:
        remaining = HEALING_COOLDOWN_SEC - (time.time() - last)
        logger.info(f"Cooldown active for ({service}, {action}) — {remaining:.0f}s remaining.")
        return True
    return False


def set_cooldown(service: str, action: str):
    heal_cooldowns[(service, action)] = time.time()


# ---- Kafka publish helpers ----

def publish_healing_log(healing_id: str, trigger_alert_id: str, action: str,
                         resource: str, status: str, details: dict):
    producer = get_kafka_producer()
    if not producer:
        return
    payload = {
        "healingId":      healing_id,
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "source":         "hephaestus",
        "triggerAlertId": trigger_alert_id,
        "action":         action,
        "target": {
            "namespace": TARGET_NAMESPACE,
            "resource":  resource,
        },
        "status":  status,
        "details": details,
    }
    try:
        producer.send(KAFKA_HEALING_TOPIC, payload)
        producer.flush()
        logger.info(f"Healing log published [{action}] on {resource} → {status}")
    except Exception as e:
        logger.error(f"Failed to publish healing log: {e}")


def publish_system_log(level: str, message: str):
    producer = get_kafka_producer()
    if not producer:
        return
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source":    "hephaestus",
        "level":     level,
        "message":   message,
    }
    try:
        producer.send(KAFKA_LOGS_TOPIC, payload)
    except Exception as e:
        logger.error(f"Failed to publish system log: {e}")


# ============================================================
# Healing Action Executors
# ============================================================

def action_scale_up(service: str, alert_id: str) -> str:
    """Scale a Deployment up by +1 replica (capped at MAX_REPLICAS)."""
    healing_id = str(uuid.uuid4())
    start = time.time()
    logger.info(f"[SCALE_UP] Scaling up deployment '{service}' in {TARGET_NAMESPACE}...")

    try:
        dep = apps_v1.read_namespaced_deployment(name=service, namespace=TARGET_NAMESPACE)
        current = dep.spec.replicas or 1
        desired = min(current + 1, MAX_REPLICAS)

        if current >= MAX_REPLICAS:
            msg = f"Already at max replicas ({MAX_REPLICAS}). Skipping scale-up."
            logger.warning(msg)
            publish_healing_log(healing_id, alert_id, "SCALE_UP", service, "PARTIAL",
                                {"previousState": str(current), "newState": str(current),
                                 "durationMs": int((time.time()-start)*1000), "errorMessage": msg})
            return "PARTIAL"

        patch = {"spec": {"replicas": desired}}
        apps_v1.patch_namespaced_deployment_scale(name=service, namespace=TARGET_NAMESPACE, body=patch)
        logger.info(f"[SCALE_UP] {service}: {current} → {desired} replicas")

        publish_healing_log(healing_id, alert_id, "SCALE_UP", service, "SUCCESS",
                            {"previousState": f"{current} replicas",
                             "newState":      f"{desired} replicas",
                             "durationMs":    int((time.time()-start)*1000)})
        publish_system_log("INFO", f"Scaled up '{service}' from {current} to {desired} replicas.")
        return "SUCCESS"

    except ApiException as e:
        err = f"K8s API error during SCALE_UP on '{service}': {e.reason}"
        logger.error(err)
        publish_healing_log(healing_id, alert_id, "SCALE_UP", service, "FAILED",
                            {"durationMs": int((time.time()-start)*1000), "errorMessage": err})
        return "FAILED"


def action_restart_pod(service: str, alert_id: str) -> str:
    """Delete the oldest Running pod of a Deployment; K8s recreates it."""
    healing_id = str(uuid.uuid4())
    start = time.time()
    logger.info(f"[RESTART] Finding pods for service '{service}' in {TARGET_NAMESPACE}...")

    try:
        pods = core_v1.list_namespaced_pod(
            namespace=TARGET_NAMESPACE,
            label_selector=f"app={service}"
        )
        running_pods = [p for p in pods.items if p.status.phase == "Running"
                        and p.metadata.deletion_timestamp is None]

        if not running_pods:
            err = f"No running pods found for service '{service}'."
            logger.warning(err)
            publish_healing_log(healing_id, alert_id, "RESTART", service, "FAILED",
                                {"durationMs": int((time.time()-start)*1000), "errorMessage": err})
            return "FAILED"

        # Pick the oldest pod (most likely the troubled one)
        target_pod = sorted(running_pods, key=lambda p: p.metadata.creation_timestamp)[0]
        pod_name = target_pod.metadata.name

        core_v1.delete_namespaced_pod(
            name=pod_name,
            namespace=TARGET_NAMESPACE,
            grace_period_seconds=0
        )
        logger.info(f"[RESTART] Deleted pod '{pod_name}' for service '{service}'.")

        # Wait up to 60s for a new pod to appear
        elapsed = 0
        new_pod_ready = False
        while elapsed < 60:
            time.sleep(5)
            elapsed += 5
            pods_now = core_v1.list_namespaced_pod(
                namespace=TARGET_NAMESPACE,
                label_selector=f"app={service}"
            )
            ready_pods = [p for p in pods_now.items
                          if p.metadata.name != pod_name
                          and p.status.phase == "Running"
                          and all(c.ready for c in (p.status.container_statuses or []))]
            if ready_pods:
                new_pod_ready = True
                logger.info(f"[RESTART] New pod ready for '{service}': {ready_pods[0].metadata.name}")
                break

        status = "SUCCESS" if new_pod_ready else "PARTIAL"
        publish_healing_log(healing_id, alert_id, "RESTART", pod_name, status,
                            {"previousState": f"pod/{pod_name} Running",
                             "newState":      "pod replaced" if new_pod_ready else "replacement pending",
                             "durationMs":    int((time.time()-start)*1000)})
        publish_system_log("INFO", f"Restarted pod '{pod_name}' for service '{service}'. Status: {status}")
        return status

    except ApiException as e:
        err = f"K8s API error during RESTART on '{service}': {e.reason}"
        logger.error(err)
        publish_healing_log(healing_id, alert_id, "RESTART", service, "FAILED",
                            {"durationMs": int((time.time()-start)*1000), "errorMessage": err})
        return "FAILED"


def action_rollback(service: str, alert_id: str) -> str:
    """Rollback a Deployment by patching it to trigger a rollout (annotation bump)."""
    healing_id = str(uuid.uuid4())
    start = time.time()
    logger.info(f"[ROLLBACK] Rolling back deployment '{service}' in {TARGET_NAMESPACE}...")

    try:
        dep = apps_v1.read_namespaced_deployment(name=service, namespace=TARGET_NAMESPACE)
        prev_revision = dep.metadata.annotations.get("deployment.kubernetes.io/revision", "?")

        # Trigger rollback by patching the rollout annotation
        # (kubernetes.io/change-cause triggers a new rollout from previous ReplicaSet)
        patch = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "hephaestus.io/rollback-triggered": datetime.now(timezone.utc).isoformat()
                        }
                    }
                }
            }
        }
        apps_v1.patch_namespaced_deployment(name=service, namespace=TARGET_NAMESPACE, body=patch)
        logger.info(f"[ROLLBACK] Rollback triggered for '{service}' (was revision {prev_revision}).")

        publish_healing_log(healing_id, alert_id, "ROLLBACK", service, "SUCCESS",
                            {"previousState": f"revision {prev_revision}",
                             "newState":      "rollback triggered",
                             "durationMs":    int((time.time()-start)*1000)})
        publish_system_log("WARNING", f"Rollback triggered for deployment '{service}'.")
        return "SUCCESS"

    except ApiException as e:
        err = f"K8s API error during ROLLBACK on '{service}': {e.reason}"
        logger.error(err)
        publish_healing_log(healing_id, alert_id, "ROLLBACK", service, "FAILED",
                            {"durationMs": int((time.time()-start)*1000), "errorMessage": err})
        return "FAILED"


def action_block_ip(service: str, source_ip: str, alert_id: str) -> str:
    """Create a NetworkPolicy that denies ingress from source_ip to the service."""
    healing_id = str(uuid.uuid4())
    start = time.time()
    policy_name = f"block-{service}-{healing_id[:8]}"
    logger.info(f"[BLOCK_IP] Creating NetworkPolicy '{policy_name}' to block {source_ip} → {service}...")

    try:
        # NetworkPolicy: deny ingress from source_ip to pods with app=service
        body = k8s_client.V1NetworkPolicy(
            api_version="networking.k8s.io/v1",
            kind="NetworkPolicy",
            metadata=k8s_client.V1ObjectMeta(
                name=policy_name,
                namespace=TARGET_NAMESPACE,
                labels={
                    "hephaestus.io/managed": "true",
                    "hephaestus.io/healing-id": healing_id[:8],
                },
                annotations={
                    "hephaestus.io/created-at": datetime.now(timezone.utc).isoformat(),
                    "hephaestus.io/expires-at": datetime.fromtimestamp(
                        time.time() + NETWORK_POLICY_TTL_SEC, tz=timezone.utc).isoformat(),
                    "hephaestus.io/blocked-ip":  source_ip,
                    "hephaestus.io/alert-id":    alert_id,
                }
            ),
            spec=k8s_client.V1NetworkPolicySpec(
                pod_selector=k8s_client.V1LabelSelector(
                    match_labels={"app": service}
                ),
                policy_types=["Ingress"],
                ingress=[
                    # Allow all EXCEPT the blocked IP
                    k8s_client.V1NetworkPolicyIngressRule(
                        _from=[
                            k8s_client.V1NetworkPolicyPeer(
                                ip_block=k8s_client.V1IPBlock(
                                    cidr="0.0.0.0/0",
                                    _except=[f"{source_ip}/32"]
                                )
                            )
                        ]
                    )
                ]
            )
        )

        networking_v1.create_namespaced_network_policy(namespace=TARGET_NAMESPACE, body=body)
        logger.info(f"[BLOCK_IP] NetworkPolicy '{policy_name}' created. Expires in {NETWORK_POLICY_TTL_SEC}s.")

        # Schedule TTL cleanup using threading.Timer — safe from any thread / non-async context
        import threading
        timer = threading.Timer(NETWORK_POLICY_TTL_SEC, _sync_expire_network_policy, args=[policy_name])
        timer.daemon = True
        timer.start()

        publish_healing_log(healing_id, alert_id, "BLOCK_IP", policy_name, "SUCCESS",
                            {"previousState": f"IP {source_ip} allowed",
                             "newState":      f"IP {source_ip} blocked via {policy_name} (TTL {NETWORK_POLICY_TTL_SEC}s)",
                             "durationMs":    int((time.time()-start)*1000)})
        publish_system_log("WARNING",
                           f"Blocked IP {source_ip} for service '{service}' via NetworkPolicy. TTL={NETWORK_POLICY_TTL_SEC}s.")
        return "SUCCESS"

    except ApiException as e:
        err = f"K8s API error during BLOCK_IP on '{service}': {e.reason}"
        logger.error(err)
        publish_healing_log(healing_id, alert_id, "BLOCK_IP", policy_name, "FAILED",
                            {"durationMs": int((time.time()-start)*1000), "errorMessage": err})
        return "FAILED"


def _sync_expire_network_policy(policy_name: str):
    """Synchronous TTL cleanup — runs in a threading.Timer daemon thread (no asyncio needed)."""
    try:
        networking_v1.delete_namespaced_network_policy(
            name=policy_name, namespace=TARGET_NAMESPACE
        )
        logger.info(f"[BLOCK_IP] NetworkPolicy '{policy_name}' TTL expired — auto-deleted.")
        publish_system_log("INFO", f"NetworkPolicy '{policy_name}' TTL expired — auto-deleted.")
    except ApiException as e:
        if e.status == 404:
            logger.info(f"[BLOCK_IP] NetworkPolicy '{policy_name}' already gone (404).")
        else:
            logger.error(f"[BLOCK_IP] Failed to delete expired NetworkPolicy '{policy_name}': {e.reason}")


# ============================================================
# Alert Processing
# ============================================================

def process_alert(alert: dict):
    """
    Main entry point: receives a Gaia alert dict and decides + executes healing.
    """
    alert_id       = alert.get("alertId", str(uuid.uuid4()))
    alert_type     = alert.get("type", "UNKNOWN")
    severity       = alert.get("severity", "WARNING")
    service        = alert.get("affectedService", "")
    description    = alert.get("description", "")
    suggested      = alert.get("suggestedAction", "")

    logger.info(f"Processing alert [{alert_type}/{severity}] for service '{service}': {description}")

    if not service:
        logger.warning("Alert has no affectedService — skipping.")
        return

    # Decide action
    action = decide_action(alert_type, severity)
    if not action:
        logger.warning(f"No healing action defined for ({alert_type}, {severity}) — skipping.")
        return

    # Cooldown check — prevent thrashing
    if is_in_cooldown(service, action):
        logger.info(f"Cooldown active for '{service}' + '{action}'. Skipping heal.")
        return

    logger.info(f"Decision: {action} on service '{service}'")
    set_cooldown(service, action)

    # Execute healing action
    status = "UNKNOWN"
    if action == "SCALE_UP":
        status = action_scale_up(service, alert_id)

    elif action == "RESTART":
        status = action_restart_pod(service, alert_id)

    elif action == "ROLLBACK":
        status = action_rollback(service, alert_id)

    elif action == "BLOCK_IP":
        # Extract source IP from alert description if available
        source_ip = alert.get("sourceIP", "")
        if not source_ip:
            # Parse from description as fallback
            import re
            match = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})', description)
            source_ip = match.group(1) if match else "0.0.0.0"
        status = action_block_ip(service, source_ip, alert_id)

    else:
        logger.warning(f"Unknown action '{action}' — skipping.")
        status = "SKIPPED"

    # Append to in-memory audit log (capped at MAX_HISTORY)
    heal_history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "alertId":   alert_id,
        "alertType": alert_type,
        "severity":  severity,
        "service":   service,
        "action":    action,
        "status":    status,
    })
    if len(heal_history) > MAX_HISTORY:
        heal_history.pop(0)


# ============================================================
# Kafka Consumer Loop
# ============================================================

def _kafka_consumer_thread():
    """
    Kafka consumer runs in a daemon thread so it never blocks the asyncio
    event loop — uvicorn can always serve /healthz while this runs.
    """
    logger.info(f"Kafka consumer thread starting — topic '{KAFKA_ALERTS_TOPIC}'...")
    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_ALERTS_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
                group_id=KAFKA_GROUP_ID,
                auto_offset_reset="latest",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                enable_auto_commit=True,
            )
            logger.info("Kafka consumer connected. Listening for alerts...")

            for msg in consumer:
                try:
                    process_alert(msg.value)
                except Exception as e:
                    logger.error(f"Error processing alert: {e}")

        except Exception as e:
            logger.error(f"Kafka consumer error — retrying in 5s: {e}")
            time.sleep(5)


async def alert_consumer_loop():
    """Launch Kafka consumer in a background daemon thread."""
    import threading
    t = threading.Thread(target=_kafka_consumer_thread, daemon=True)
    t.start()
    logger.info("Kafka consumer daemon thread launched.")


# ============================================================
# FastAPI lifecycle & REST API
# ============================================================

@app.on_event("startup")
async def startup_event():
    init_k8s()
    get_kafka_producer()
    asyncio.create_task(alert_consumer_loop())
    publish_system_log("INFO", "Hephaestus Agent initialized — self-healing loop started.")
    logger.info("Hephaestus Agent ready.")


@app.get("/")
def root():
    return {
        "status": "UP",
        "agent":  "hephaestus",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/healthz")
def healthz():
    k8s_ok = core_v1 is not None
    kafka_ok = get_kafka_producer() is not None
    return {
        "status":           "UP",
        "k8s_connected":    k8s_ok,
        "kafka_connected":  kafka_ok,
        "cooldowns_active": len(heal_cooldowns),
    }


@app.get("/cooldowns")
def get_cooldowns():
    now = time.time()
    return {
        "cooldowns": [
            {
                "service":    svc,
                "action":     act,
                "remaining_sec": max(0, HEALING_COOLDOWN_SEC - (now - ts)),
            }
            for (svc, act), ts in heal_cooldowns.items()
        ]
    }


@app.post("/heal/trigger")
async def manual_heal(body: dict):
    """
    Manually trigger a healing action for testing purposes.
    Body: { "alertType": "HIGH_CPU", "severity": "WARNING", "affectedService": "frontend" }
    """
    alert = {
        "alertId":         str(uuid.uuid4()),
        "type":            body.get("alertType", "HIGH_CPU"),
        "severity":        body.get("severity", "WARNING"),
        "affectedService": body.get("affectedService", "frontend"),
        "description":     body.get("description", "Manual trigger via REST API"),
        "sourceIP":        body.get("sourceIP", ""),
    }
    await asyncio.get_event_loop().run_in_executor(None, process_alert, alert)
    return {"message": "Healing triggered.", "alert": alert}


@app.get("/network-policies")
def list_managed_network_policies():
    """List all NetworkPolicies created by Hephaestus."""
    try:
        policies = networking_v1.list_namespaced_network_policy(
            namespace=TARGET_NAMESPACE,
            label_selector="hephaestus.io/managed=true"
        )
        return {
            "policies": [
                {
                    "name":        p.metadata.name,
                    "created_at":  p.metadata.annotations.get("hephaestus.io/created-at"),
                    "expires_at":  p.metadata.annotations.get("hephaestus.io/expires-at"),
                    "blocked_ip":  p.metadata.annotations.get("hephaestus.io/blocked-ip"),
                }
                for p in policies.items
            ]
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/heal/history")
def get_heal_history():
    """
    Return the in-memory audit log of all healing events.
    Used by Phase 5 experiment_runner_direct.py to measure MTTD/MTTR
    without requiring direct Kafka access from outside the cluster.
    """
    return {
        "total":   len(heal_history),
        "history": list(reversed(heal_history)),   # newest first
    }


@app.post("/experiment/reset")
def experiment_reset():
    """
    Reset all cooldowns and clear heal_history.
    Called by experiment_runner_direct.py between runs so cooldowns
    from the previous run don't block the next injection.
    """
    heal_cooldowns.clear()
    heal_history.clear()
    logger.info("[EXPERIMENT] Cooldowns and history cleared for new experiment run.")
    return {"message": "Cooldowns and heal history cleared.", "timestamp": datetime.now(timezone.utc).isoformat()}

