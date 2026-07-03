import os
import json
import time
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Tuple

from fastapi import FastAPI
import httpx
from elasticsearch import Elasticsearch
from kafka import KafkaProducer

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("gaia-agent")

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka.zero-door.svc.cluster.local:9092")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch.monitoring.svc.cluster.local:9200")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "15"))
COOLDOWN_PERIOD = int(os.getenv("COOLDOWN_PERIOD", "60"))

app = FastAPI(title="Gaia Agent - Observer & Monitor")

# State store for deduplication
# Key: (affectedService, anomalyType), Value: timestamp of last sent alert
alert_cooldowns: Dict[Tuple[str, str], float] = {}

# Clients
kafka_producer = None
es_client = None

def get_kafka_producer():
    global kafka_producer
    if kafka_producer is None:
        try:
            kafka_producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks="all",
                request_timeout_ms=5000,
                retries=3
            )
            logger.info("Kafka Producer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka Producer: {e}")
    return kafka_producer

def get_es_client():
    global es_client
    if es_client is None:
        try:
            es_client = Elasticsearch(ELASTICSEARCH_URL)
            # Ping to verify
            if es_client.ping():
                logger.info("Elasticsearch Client connected successfully.")
            else:
                logger.warning("Elasticsearch ping failed.")
                es_client = None
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            es_client = None
    return es_client

def send_system_log(level: str, message: str):
    producer = get_kafka_producer()
    log_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "gaia-agent",
        "level": level,
        "message": message
    }
    if producer:
        try:
            producer.send("system.logs", log_payload)
            logger.info(f"System log sent to Kafka: {message}")
        except Exception as e:
            logger.error(f"Failed to send system log to Kafka: {e}")
    else:
        logger.info(f"[Local Log - Kafka Offline] {level}: {message}")

def publish_alert(alert_type: str, service: str, metric_name: str, current_value: float, threshold: float, description: str, severity: str = "WARNING", suggested_action: str = "NONE"):
    now = time.time()
    cooldown_key = (service, alert_type)
    
    # Deduplication check
    if cooldown_key in alert_cooldowns:
        last_sent = alert_cooldowns[cooldown_key]
        if now - last_sent < COOLDOWN_PERIOD:
            logger.info(f"Deduplicated alert '{alert_type}' for '{service}' (Cooldown active).")
            return
            
    alert_payload = {
        "alertId": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": severity,
        "type": alert_type,
        "source": "gaia-agent",
        "affectedService": service,
        "affectedNamespace": "target-app",
        "metric": metric_name,
        "currentValue": current_value,
        "threshold": threshold,
        "description": description,
        "suggestedAction": suggested_action
    }
    
    producer = get_kafka_producer()
    if producer:
        try:
            producer.send("monitoring.alerts", alert_payload)
            alert_cooldowns[cooldown_key] = now
            logger.warning(f"ALERT PUBLISHED to Kafka [Topic: monitoring.alerts]: {description}")
            send_system_log("WARNING", f"Alert triggered: {alert_type} on {service}. {description}")
        except Exception as e:
            logger.error(f"Failed to publish alert to Kafka: {e}")
    else:
        logger.warning(f"[Local Alert - Kafka Offline] {description}")

def get_service_name(pod: str, container: str) -> str:
    if not pod:
        return container
    if "-stress" in pod:
        return pod.split("-stress")[0]
    parts = pod.split("-")
    if len(parts) > 2:
        return "-".join(parts[:-2])
    return parts[0]

async def query_prometheus(client: httpx.AsyncClient, query: str):
    try:
        url = f"{PROMETHEUS_URL}/api/v1/query"
        response = await client.get(url, params={"query": query}, timeout=5.0)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Prometheus query returned status {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Error querying Prometheus: {e}")
    return None

async def poll_prometheus_metrics():
    logger.info("Starting Prometheus metrics polling...")
    async with httpx.AsyncClient() as client:
        # 1. Check CPU Spikes (group by pod and container to resolve container name overlap)
        cpu_query = 'sum(rate(container_cpu_usage_seconds_total{namespace="target-app", container!=""}[1m])) by (pod, container)'
        cpu_data = await query_prometheus(client, cpu_query)
        if cpu_data and cpu_data.get("status") == "success":
            results = cpu_data.get("data", {}).get("result", [])
            for res in results:
                pod = res.get("metric", {}).get("pod")
                container = res.get("metric", {}).get("container")
                val = float(res.get("value", [0, "0"])[1])
                
                service = get_service_name(pod, container)
                limit = 0.125 if service == "redis-cart" else 0.200
                threshold = limit * 0.8
                
                if val > threshold:
                    publish_alert(
                        alert_type="HIGH_CPU",
                        service=service,
                        metric_name="cpu_usage_percent",
                        current_value=round(val / limit * 100, 2),
                        threshold=80.0,
                        description=f"CPU utilization of service '{service}' (pod '{pod}') is at {round(val / limit * 100, 1)}% (using {round(val, 3)} cores, limit is {limit} cores).",
                        severity="WARNING",
                        suggested_action="SCALE_UP"
                    )

        # 2. Check Memory Spikes (group by pod and container)
        memory_query = 'sum(container_memory_working_set_bytes{namespace="target-app", container!=""}) by (pod, container)'
        mem_data = await query_prometheus(client, memory_query)
        if mem_data and mem_data.get("status") == "success":
            results = mem_data.get("data", {}).get("result", [])
            for res in results:
                pod = res.get("metric", {}).get("pod")
                container = res.get("metric", {}).get("container")
                val = float(res.get("value", [0, "0"])[1])
                
                service = get_service_name(pod, container)
                limit_bytes = 268435456  # 256Mi
                threshold_bytes = limit_bytes * 0.8
                
                if val > threshold_bytes:
                    publish_alert(
                        alert_type="HIGH_MEMORY",
                        service=service,
                        metric_name="memory_working_set_bytes",
                        current_value=round(val / 1024 / 1024, 2),
                        threshold=204.8,
                        description=f"Memory utilization of service '{service}' (pod '{pod}') is at {round(val / limit_bytes * 100, 1)}% ({round(val / 1024 / 1024, 1)} MiB of {round(limit_bytes / 1024 / 1024, 1)} MiB limit).",
                        severity="WARNING",
                        suggested_action="RESTART"
                    )

        # 3. Check HTTP Error Rates (from nginx ingress controller if available, otherwise frontend metrics)
        # Let's query Prometheus for HTTP 5xx error rate from frontend if available
        # Expr: sum(rate(nginx_ingress_controller_requests{status=~"5..", namespace="target-app"}[1m])) by (service) / sum(rate(nginx_ingress_controller_requests{namespace="target-app"}[1m])) by (service)
        error_rate_query = 'sum(rate(nginx_ingress_controller_requests{status=~"5..", namespace="target-app"}[1m])) by (service) / sum(rate(nginx_ingress_controller_requests{namespace="target-app"}[1m])) by (service)'
        error_data = await query_prometheus(client, error_rate_query)
        if error_data and error_data.get("status") == "success":
            results = error_data.get("data", {}).get("result", [])
            for res in results:
                service = res.get("metric", {}).get("service")
                val = float(res.get("value", [0, "0"])[1])
                if val > 0.05:
                    publish_alert(
                        alert_type="HIGH_ERROR_RATE",
                        service=service,
                        metric_name="http_5xx_rate",
                        current_value=round(val * 100, 2),
                        threshold=5.0,
                        description=f"HTTP 5xx rate on service '{service}' is {round(val * 100, 2)}% (threshold is 5.0%).",
                        severity="CRITICAL",
                        suggested_action="RESTART"
                    )

        # 4. Check Latency Spikes (P99 latency > 1000ms)
        # Expr: histogram_quantile(0.99, sum(rate(nginx_ingress_controller_request_duration_seconds_bucket{namespace="target-app"}[1m])) by (le, service))
        latency_query = 'histogram_quantile(0.99, sum(rate(nginx_ingress_controller_request_duration_seconds_bucket{namespace="target-app"}[1m])) by (le, service))'
        latency_data = await query_prometheus(client, latency_query)
        if latency_data and latency_data.get("status") == "success":
            results = latency_data.get("data", {}).get("result", [])
            for res in results:
                service = res.get("metric", {}).get("service")
                val = float(res.get("value", [0, "0"])[1])
                # val is in seconds, if > 1.0 (1000ms)
                if val > 1.0:
                    publish_alert(
                        alert_type="HIGH_LATENCY",
                        service=service,
                        metric_name="http_p99_latency_ms",
                        current_value=round(val * 1000, 1),
                        threshold=1000.0,
                        description=f"HTTP P99 response latency on service '{service}' is {round(val * 1000, 1)}ms (threshold is 1000ms).",
                        severity="WARNING",
                        suggested_action="SCALE_UP"
                    )

        # 5. Check Pod CrashLooping
        # Expr: sum(increase(kube_pod_container_status_restarts_total{namespace="target-app"}[5m])) by (pod, container)
        crash_query = 'sum(increase(kube_pod_container_status_restarts_total{namespace="target-app"}[5m])) by (pod, container)'
        crash_data = await query_prometheus(client, crash_query)
        if crash_data and crash_data.get("status") == "success":
            results = crash_data.get("data", {}).get("result", [])
            for res in results:
                pod = res.get("metric", {}).get("pod")
                container = res.get("metric", {}).get("container")
                val = float(res.get("value", [0, "0"])[1])
                if val > 3.0:
                    publish_alert(
                        alert_type="POD_CRASH",
                        service=container,
                        metric_name="restart_count_5m",
                        current_value=val,
                        threshold=3.0,
                        description=f"Pod '{pod}' container '{container}' restarted {int(val)} times in the last 5 minutes.",
                        severity="CRITICAL",
                        suggested_action="RESTART"
                    )

async def poll_elasticsearch_logs():
    logger.info("Starting Elasticsearch logs polling...")
    es = get_es_client()
    if es is None:
        logger.warning("Elasticsearch is offline. Skipping log analysis.")
        return

    try:
        # Search zero-door-logs-* for documents in the last interval (using 2x interval to account for propagation lag)
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": f"now-{POLL_INTERVAL * 2}s",
                                    "lte": "now"
                                }
                            }
                        }
                    ],
                    "should": [
                        {"match_phrase": {"message": "ERROR"}},
                        {"match_phrase": {"message": "Exception"}},
                        {"match_phrase": {"message": "OOMKilled"}},
                        {"match_phrase": {"message": "UNION SELECT"}},
                        {"match_phrase": {"message": "OR '1'='1"}}
                    ],
                    "minimum_should_match": 1
                }
            },
            "size": 50
        }
        
        # We index under logstash format: zero-door-logs-*
        res = es.search(index="zero-door-logs-*", body=query_body)
        hits = res.get("hits", {}).get("hits", [])
        logger.info(f"Elasticsearch log query returned {len(hits)} hits.")
        
        # Track matches by pod
        for hit in hits:
            source = hit.get("_source", {})
            log_msg = source.get("message", "")
            kubernetes = source.get("kubernetes", {})
            pod_name = kubernetes.get("pod_name", "unknown")
            namespace = kubernetes.get("namespace_name", "unknown")
            container_name = kubernetes.get("container_name", "unknown")
            
            # Simple signature check
            anomaly_detected = False
            reason = ""
            alert_type = "SUSPICIOUS_LOG"
            severity = "WARNING"
            
            if "OOMKilled" in log_msg:
                anomaly_detected = True
                reason = "OOMKilled event detected in container logs."
                alert_type = "HIGH_MEMORY"
                severity = "CRITICAL"
            elif "UNION SELECT" in log_msg or "OR '1'='1" in log_msg:
                anomaly_detected = True
                reason = "SQL Injection payload pattern detected in container logs."
                severity = "CRITICAL"
            elif "ERROR" in log_msg or "Exception" in log_msg:
                # Basic filter to prevent flooding on standard errors
                # Only flag as anomaly if it occurs in target-app namespace
                if namespace == "target-app":
                    anomaly_detected = True
                    reason = f"Application error/exception occurred: {log_msg[:100]}"
            
            if anomaly_detected:
                publish_alert(
                    alert_type=alert_type,
                    service=container_name,
                    metric_name="log_pattern_match",
                    current_value=1.0,
                    threshold=0.0,
                    description=f"Suspicious activity on pod '{pod_name}' container '{container_name}': {reason}",
                    severity=severity,
                    suggested_action="RESTART" if alert_type == "HIGH_MEMORY" else "BLOCK_IP"
                )
    except Exception as e:
        logger.error(f"Error querying Elasticsearch: {e}")

async def monitoring_loop():
    logger.info("Gaia monitoring loop started.")
    # Send initialization message
    send_system_log("INFO", "Gaia Agent initialized and beginning monitoring loops.")
    
    while True:
        try:
            # Poll metrics and logs concurrently
            await asyncio.gather(
                poll_prometheus_metrics(),
                poll_elasticsearch_logs(),
                return_exceptions=True
            )
        except Exception as e:
            logger.error(f"Error in monitoring loop execution: {e}")
            
        await asyncio.sleep(POLL_INTERVAL)

@app.on_event("startup")
async def startup_event():
    # Start the background loop
    asyncio.create_task(monitoring_loop())

@app.get("/")
def read_root():
    return {
        "status": "UP",
        "agent": "gaia",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/healthz")
def healthz():
    kafka_ok = get_kafka_producer() is not None
    es_ok = get_es_client() is not None
    return {
        "status": "UP",
        "kafka_connected": kafka_ok,
        "elasticsearch_connected": es_ok,
        "prometheus_endpoint": PROMETHEUS_URL
    }
