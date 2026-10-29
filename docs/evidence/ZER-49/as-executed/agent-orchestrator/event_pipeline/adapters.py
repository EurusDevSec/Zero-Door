"""Adapters for the existing Gaia rules and Hephaestus decision matrix.

No R1 action is executed until a separate approved guard/executor is wired in.
No action status is synthesized from the legacy API-only success messages.
"""
from .client import permanent
from .contract import canonical, new_id, now, validate
from .decision_journal import DecisionJournal


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
    def __init__(self, client, decide, *, journal_path=None, clock=None):
        self.client, self.decide = client, decide
        self.journal = DecisionJournal(journal_path, **({"clock": clock} if clock else {}))

    def close(self):
        self.journal.close()

    def poll(self):
        records = list(self.client.records())
        events, errors = [], []
        for record in records:
            event = record.get("envelope") if isinstance(record, dict) else None
            if not isinstance(event, dict) or validate(event, "O"):
                errors.append(ValueError("invalid archive envelope"))
                continue
            events.append(event)
        # Durable dedup survives consumer restarts. This adapter emits decisions only.
        completed = [event for event in events if event.get("event_type") == "DECISION"
                and event.get("trial_id") == self.client.trial and event.get("group") == "B1"
                and not validate(event, "O", "decision_rules") and event["payload"]["stage"] == "PROPOSAL"]
        done = {item["event_id"] for event in completed for item in event["payload"]["inputs"]}
        for event in completed:
            for item in event["payload"]["inputs"]:
                row = self.journal.get(item["event_id"])
                if row and canonical(event).decode() == row["envelope"]:
                    self.journal.finish(item["event_id"], "RECORDED")
        sent = False  # One bounded HTTP publish per tick; no batch can monopolize the owner.
        for event in events:
            if event["event_type"] != "DETECTED" or event["trial_id"] != self.client.trial \
                    or event["event_id"] in done:
                continue
            if validate(event, "O", "detector"):
                errors.append(ValueError("invalid detector envelope"))
                continue
            if event["group"] != "B1":
                continue  # B2/B3 need a genuine LLM result/fallback; B0/BM never auto-decide.
            def build():
                received_at = now()
                p = event["payload"]
                action = self.decide(p["rule_id"], p["severity"])
                ctx = {key: event[key] for key in ("run_id", "trial_id", "group", "method_version", "config_ref", "incident_id") if key in event}
                return self.client.producer.event(ctx, "DECISION", {
                    "stage": "PROPOSAL", "decision_source": "RULES",
                    "inputs": [{"event_id": event["event_id"], "received_at": received_at}],
                    "response_kind": "ACTION" if action else "NO_ACTION",
                    "proposal": {"action_type": action, "params": {"service": event["target"]["service"]}} if action else None,
                    "fallback": False, "fallback_of": None, "prompt_version": None, "prompt_sha256": None,
                    "evidence_package_version": "o-envelope/1.0.0",
                }, "o.decision", target=event["target"], decision_id=new_id("dec"), causation_id=event["event_id"])
            try:
                row = self.journal.reserve(event, build)
            except ValueError as error:
                errors.append(error)
                continue
            if sent:
                continue
            pending = self.journal.attempt(event["event_id"])
            if pending is None:
                continue
            sent = True
            try:
                receipt = self.client.publish(pending)
                if (not isinstance(receipt, dict) or receipt.get("status") not in {"RECORDED", "DUPLICATE", "SEALED_DUPLICATE"}
                        or receipt.get("event_id") != pending["event_id"]):
                    raise TimeoutError("DECISION_RECEIPT_UNKNOWN")
            except Exception as error:
                if permanent(error):
                    self.journal.finish(event["event_id"], "REFUSED", str(error.code))
                elif row["attempts"] + 1 >= self.journal.MAX_ATTEMPTS:
                    self.journal.finish(event["event_id"], "UNKNOWN", type(error).__name__)
                errors.append(error)
            else:
                self.journal.finish(event["event_id"], "RECORDED")
                done.add(event["event_id"])
        if errors:
            raise errors[0]
