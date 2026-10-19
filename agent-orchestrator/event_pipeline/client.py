"""O-only producer client. It is never given H credentials or H paths."""
import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .contract import Producer, canonical, valid_id

# Each actor's key file holds exactly its own producer role plus reader (ZR9-04). A file that also
# carries another producer, harness or evaluator key is refused, so one actor cannot write as another.
ACTOR_KEYS = {"detector": {"detector", "reader"}, "decision_rules": {"decision_rules", "reader"},
              "operator_console": {"operator_console", "reader"}}


def permanent(error):
    """A 4xx answer (except 408/429) is final for this envelope: it was refused or quarantined.

    Timeouts, connection errors, 5xx/429 and an ack without durable receipt leave the outcome
    unknown, so the caller must resend the SAME envelope.
    """
    return isinstance(error, HTTPError) and 400 <= error.code < 500 and error.code not in {408, 429}


class Client:
    def __init__(self, url, token, reader_token, run, trial, producer):
        if not valid_id(run, "run") or not valid_id(trial, "trl"):
            raise ValueError("explicit run/trial IDs required")
        self.url, self.token, self.reader_token = url.rstrip("/"), token, reader_token
        self.run, self.trial, self.producer = run, trial, producer

    @classmethod
    def from_env(cls, source):
        url = os.getenv("ZD_EVENT_URL")
        if not url:
            return None
        # Only the O key file is mounted into the producer/consumer container.
        keys = json.loads(Path(os.environ["ZD_O_KEYS_FILE"]).read_text())
        if source not in ACTOR_KEYS or not isinstance(keys, dict) or set(keys) != ACTOR_KEYS[source]:
            raise ValueError("O key file must hold exactly the roles " + str(sorted(ACTOR_KEYS.get(source, ()))))
        producer = Producer(source, os.environ["ZD_PRODUCER_VERSION"], {
            "clock_id": os.environ["ZD_CLOCK_ID"], "clock_source": os.getenv("ZD_CLOCK_SOURCE", "UNKNOWN"),
            "resolution_ms": None,
        })
        return cls(url, keys[source], keys["reader"], os.environ["ZD_RUN_ID"], os.environ["ZD_TRIAL_ID"], producer)

    def request(self, path, event=None):
        token = self.token if event is not None else self.reader_token
        request = Request(self.url + path, data=canonical(event) if event is not None else None,
                          headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
        with urlopen(request, timeout=5) as response:
            return json.load(response)

    def records(self):
        cursor = 0
        while True:
            page = self.request(f"/events?run_id={self.run}&after={cursor}&limit=500")
            yield from page["records"]
            if page["next"] == cursor or len(page["records"]) < 500:
                break
            cursor = page["next"]

    def context(self):
        matches = [r["envelope"] for r in self.records() if r["envelope"]["event_type"] == "TRIAL_CONTEXT" and r["envelope"]["trial_id"] == self.trial]
        if not matches:
            raise ValueError("TRIAL_CONTEXT_MISSING")
        event = matches[0]
        return {key: event[key] for key in ("run_id", "trial_id", "group", "method_version", "config_ref", "incident_id") if key in event}

    def publish(self, event):
        """Caller retains this SAME event on timeout. A Kafka ack isn't a durable receipt."""
        result = self.request("/events", event)
        if result["status"] == "KAFKA_ACKNOWLEDGED":
            until = time.monotonic() + 10
            while time.monotonic() < until:
                if any(r["envelope"]["event_id"] == event["event_id"] for r in self.records()):
                    return {"status": "RECORDED", "event_id": event["event_id"]}
                time.sleep(0.1)
            raise TimeoutError("KAFKA_ACK_WITHOUT_DURABLE_RECEIPT")
        return result
