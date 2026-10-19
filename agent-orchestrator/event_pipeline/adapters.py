"""Adapters for the existing Gaia rules and Hephaestus decision matrix.

No R1 action is executed until a separate approved guard/executor is wired in.
No action status is synthesized from the legacy API-only success messages.
"""
from .client import permanent
from .contract import new_id, now, validate


class Detector:
    def __init__(self, client):
        self.client, self.pending = client, {}

    def publish(self, alert_type, service, metric, value, threshold, description, severity):
        key = (service, alert_type)
        if key not in self.pending:
            self.pending[key] = self.client.producer.event(self.client.context(), "DETECTED", {
                "rule_id": alert_type, "rule_version": "gaia-legacy-rules/r1-transport-1",
                "signature": alert_type + "/" + service, "metric": metric, "value": value,
                "threshold": threshold, "severity": severity, "description": description,
            }, "o.alert", target={"namespace": "target-app", "service": service, "flow": None}, alert_id=new_id("alt"))
        event = self.pending[key]
        try:
            self.client.publish(event)
        except Exception as error:
            # Unknown outcome: keep the SAME envelope for resend. Final refusal: drop it, so the
            # next alert gets a new ID, timestamp and observed value (ZR9-08).
            if permanent(error):
                del self.pending[key]
            raise
        del self.pending[key]
        return event


class RulesConsumer:
    def __init__(self, client, decide):
        self.client, self.decide = client, decide
        self.pending, self.refused = {}, set()

    def poll(self):
        records = list(self.client.records())
        events = [record["envelope"] for record in records]
        # Durable dedup survives consumer restarts. This adapter emits decisions only.
        done = {item["event_id"] for event in events if event["event_type"] == "DECISION"
                for item in event["payload"]["inputs"] if event["source_component"] == "decision_rules"}
        for event_id in done:
            self.pending.pop(event_id, None)
        for event in events:
            if event["event_type"] != "DETECTED" or event["trial_id"] != self.client.trial \
                    or event["event_id"] in done or event["event_id"] in self.refused:
                continue
            if validate(event, "O", "detector"):
                raise ValueError("invalid detector envelope")
            if event["group"] != "B1":
                continue  # B2/B3 need a genuine LLM result/fallback; B0/BM never auto-decide.
            if event["event_id"] not in self.pending:
                received_at = now()
                p = event["payload"]
                action = self.decide(p["rule_id"], p["severity"])
                ctx = {key: event[key] for key in ("run_id", "trial_id", "group", "method_version", "config_ref", "incident_id") if key in event}
                self.pending[event["event_id"]] = self.client.producer.event(ctx, "DECISION", {
                    "stage": "PROPOSAL", "decision_source": "RULES",
                    "inputs": [{"event_id": event["event_id"], "received_at": received_at}],
                    "response_kind": "ACTION" if action else "NO_ACTION",
                    "proposal": {"action_type": action, "params": {"service": event["target"]["service"]}} if action else None,
                    "fallback": False, "fallback_of": None, "prompt_version": None, "prompt_sha256": None,
                    "evidence_package_version": "o-envelope/1.0.0",
                }, "o.decision", target=event["target"], decision_id=new_id("dec"), causation_id=event["event_id"])
            try:
                self.client.publish(self.pending[event["event_id"]])
            except Exception as error:
                if permanent(error):
                    # Quarantined by the gateway; do not regenerate a new DECISION every poll.
                    del self.pending[event["event_id"]]
                    self.refused.add(event["event_id"])
                raise
            del self.pending[event["event_id"]]
            done.add(event["event_id"])
