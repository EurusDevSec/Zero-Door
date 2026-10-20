"""Explicit measurement parameters and probe plans. No value here is a locked formal parameter.

F-01 values (delta, K, S, L, gap, epsilon, caps) are inputs. A plan states its provenance
(SYNTHETIC, PILOT, LOCKED); this code never upgrades an illustrative value to a locked one.
"""
import math
import re
from urllib.parse import urlsplit

PROVENANCE = {"SYNTHETIC", "PILOT", "LOCKED"}
# RUN_STARTED.payload.f01_params keys, aligned with the RECOVERY_VERIFIED field names (contract 5.3).
F01 = {"delta_s": "pos", "k": "int", "s_s": "nonneg", "l_ms": "pos", "gap_s": "pos", "eps_s": "nonneg",
       "cap_det_s": "pos", "cap_rec_s": "pos"}
PLAN_VERSION = "zd-measurement-plan/0"
CLOCK_SOURCES = {"HOST_SHARED", "OFF_HOST", "UNKNOWN"}
NEUTRAL = re.compile(r"^[a-z][a-z0-9_-]{0,62}$")  # e.g. prb-0, clk_host_lab (contract 4.3 example)


class ConfigError(ValueError):
    """Every problem found, not only the first one."""
    def __init__(self, problems):
        super().__init__("; ".join(problems))
        self.problems = list(problems)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def check_f01(params, problems, prefix="f01"):
    if not isinstance(params, dict):
        problems.append(prefix + " must be an object")
        return
    for key, kind in F01.items():
        value = params.get(key)
        if kind == "int":
            ok = type(value) is int and value >= 1
        elif kind == "pos":
            ok = number(value) and value > 0
        else:
            ok = number(value) and value >= 0
        if not ok:
            problems.append(f"{prefix}.{key} missing or invalid")
    if not problems and params["gap_s"] < params["delta_s"]:
        problems.append(prefix + ".gap_s below delta_s makes every sample a gap")


def f01(params):
    """Validated F-01 parameter set; raises ConfigError. Unknown keys are kept, never interpreted."""
    problems = []
    check_f01(params, problems)
    if problems:
        raise ConfigError(problems)
    return dict(params)


def origin(url):
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
        raise ValueError("origin must be http(s)://host[:port] without credentials")
    port = parts.port or (443 if parts.scheme == "https" else 80)
    return f"{parts.scheme}://{parts.hostname.lower()}:{port}"


def plan(value):
    """Validate a probe plan (see docs/design/r1-measurement.md). Returns a normalized copy."""
    problems = []
    if not isinstance(value, dict):
        raise ConfigError(["plan must be a JSON object"])
    if value.get("plan_version") != PLAN_VERSION:
        problems.append("plan_version must be " + PLAN_VERSION)
    if value.get("provenance") not in PROVENANCE:
        problems.append("provenance must be one of " + ", ".join(sorted(PROVENANCE)))
    check_f01(value.get("f01"), problems)
    probe = value.get("probe")
    if not isinstance(probe, dict):
        problems.append("probe must be an object")
        probe = {}
    for key in ("probe_id", "probe_version", "flow", "clock_id"):
        if not isinstance(probe.get(key), str) or not NEUTRAL.fullmatch(probe.get(key, "")):
            problems.append(f"probe.{key} must be a short neutral lowercase name")
    if probe.get("clock_source") not in CLOCK_SOURCES:
        problems.append("probe.clock_source must be HOST_SHARED, OFF_HOST or UNKNOWN")
    timeouts = value.get("timeouts") if isinstance(value.get("timeouts"), dict) else {}
    step, total = timeouts.get("step_s"), timeouts.get("transaction_s")
    if not (number(step) and step > 0 and number(total) and total > 0 and step <= total):
        problems.append("timeouts.step_s and timeouts.transaction_s must be positive, step <= transaction")
    budget = value.get("budget") if isinstance(value.get("budget"), dict) else {}
    for key in ("max_duration_s", "max_samples", "max_requests"):
        if not (number(budget.get(key)) and budget[key] > 0):
            problems.append(f"budget.{key} must be positive (no unbounded runs)")
    # Cleanup and the last delivery run after the workload cap; their bound is declared, never implied.
    if not (number(budget.get("grace_s")) and 0 < budget["grace_s"] <= 60):
        problems.append("budget.grace_s (cleanup/delivery after the cap) must be in (0, 60]")
    heartbeat = value.get("heartbeat_s")
    if not (number(heartbeat) and heartbeat > 0):
        problems.append("heartbeat_s must be positive")
    target = value.get("target") if isinstance(value.get("target"), dict) else {}
    try:
        base = origin(target.get("origin", ""))
        allowed = {origin(o) for o in target.get("allowed_origins", [])}
        if base not in allowed:
            problems.append("target.origin must be listed in target.allowed_origins")
    except (ValueError, TypeError, AttributeError):
        problems.append("target.origin/allowed_origins must be http(s) origins")
    sync = value.get("clock_sync")
    if probe.get("clock_source") in {"OFF_HOST", "UNKNOWN"}:
        if not isinstance(sync, dict) or not isinstance(sync.get("method"), str) or not (number(sync.get("interval_s")) and sync["interval_s"] > 0):
            problems.append("an OFF_HOST/UNKNOWN probe clock needs clock_sync {method, interval_s, ...}")
    if not problems:
        f = value["f01"]
        if total * 1000 < f["l_ms"]:
            problems.append("timeouts.transaction_s below L: SLOW could never be observed, only TIMEOUT")
        if heartbeat > f["gap_s"] * 10:
            problems.append("heartbeat_s too coarse to tell a dead probe from a gap")
    if problems:
        raise ConfigError(problems)
    return dict(value, target=dict(target, origin=base, allowed_origins=sorted(allowed)))
