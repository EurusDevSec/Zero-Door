"""Configuration for formal decision evidence, scoped to the observer plane."""
import hashlib
import ipaddress
import json
import os
from pathlib import Path

from .client import Client
from .contract import canonical, forbidden_keys, valid_id, validate
from .formal_capture import METHOD

TTL_S = 180
MAX_OBSERVATION_BYTES = 8192
CONTEXT_FIELDS = ("run_id", "trial_id", "incident_id", "group", "method_version", "config_ref")


def rules_resolver_sha256():
    """Pin the exact reader source and the TTL applied to its output."""
    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashlib.sha256(canonical({"source_sha256": source_sha256, "ttl_s": TTL_S})).hexdigest()


class RulesResolver:
    """Read a producer-owned O access observation named by its detection event ID."""

    def __init__(self, directory, *, run_id, trial_id):
        self.directory = Path(directory)
        if (not self.directory.is_absolute() or self.directory.is_symlink() or not self.directory.is_dir()
                or not valid_id(run_id, "run") or not valid_id(trial_id, "trl")):
            raise ValueError("FORMAL_O_RESOLVER_CONFIGURATION")
        self.run_id, self.trial_id = run_id, trial_id

    def __call__(self, event):
        if (validate(event, "O", "detector") or event["event_type"] != "DETECTED"
                or (event["run_id"], event["trial_id"], event["group"], event["method_version"])
                != (self.run_id, self.trial_id, "B1", METHOD)):
            raise ValueError("FORMAL_O_RESOLVER_CONTEXT")

        path = self.directory / (event["event_id"] + ".json")
        try:
            if path.is_symlink():
                raise ValueError("FORMAL_O_OBSERVATION_SYMLINK")
            with path.open("rb") as stream:
                raw = stream.read(MAX_OBSERVATION_BYTES + 1)
            if len(raw) > MAX_OBSERVATION_BYTES:
                raise ValueError("FORMAL_O_OBSERVATION_TOO_LARGE")
            access = json.loads(raw)
            if (not isinstance(access, dict) or forbidden_keys(access)
                    or (access.get("run_id"), access.get("trial_id"), access.get("detection_event_id"))
                    != (self.run_id, self.trial_id, event["event_id"])
                    or access.get("source_method") != "XFF_AFTER_TRUSTED"
                    or access.get("source_confidence") != "PROXY_CHAIN"
                    or not isinstance(access.get("client_ip"), str)
                    or not isinstance(access.get("fixture_uid"), str)
                    or not access["fixture_uid"].strip() or len(access["fixture_uid"]) > 128):
                raise ValueError("FORMAL_O_OBSERVATION_INVALID")
            source = str(ipaddress.ip_address(access["client_ip"]))
        except FileNotFoundError:
            return {"status": "OBSERVATION_MISSING"}
        except (OSError, ValueError):
            return {"status": "RESOLVER_ERROR"}

        return {"status": "RESOLVED", "source": source, "fixture_uid": access["fixture_uid"], "ttl_s": TTL_S}


def rules_options_from_env(client):
    directory = os.getenv("ZD_FORMAL_O_OBSERVATION_DIR")
    expected_pin = os.getenv("ZD_FORMAL_RULES_RESOLVER_SHA256")
    if not directory and not expected_pin:
        return {}
    if not directory or expected_pin != rules_resolver_sha256():
        raise ValueError("FORMAL_RULES_RESOLVER_PIN_MISMATCH")
    resolver = RulesResolver(directory, run_id=client.run, trial_id=client.trial)
    return {"resolve_o": resolver, "resolver_sha256": expected_pin}


def open_formal_o_sink(context, *, keys_file):
    """Bind the B2 O writer to the role and exact context before accepting an event."""
    if (context.get("group") != "B2" or context.get("method_version") != METHOD
            or any(field not in context for field in CONTEXT_FIELDS) or not keys_file):
        raise ValueError("FORMAL_DECISION_O_CONFIGURATION")
    client = Client.from_env("decision_llm", keys_file=keys_file)
    expected = tuple(context[field] for field in CONTEXT_FIELDS)
    if client is None or (client.run, client.trial) != expected[:2]:
        raise ValueError("FORMAL_DECISION_O_CONTEXT")

    def publish(event):
        if (validate(event, "O", "decision_llm") or event["event_type"] != "DECISION"
                or tuple(event.get(field) for field in CONTEXT_FIELDS) != expected):
            raise ValueError("FORMAL_DECISION_O_EVENT")
        return client.publish(event)

    return publish
