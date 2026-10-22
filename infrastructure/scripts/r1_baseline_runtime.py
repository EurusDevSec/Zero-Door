"""H-RT1: harness for G-ZER11-RT1 (ZER-11 AC-04 = ZER-39 AC-01), B0 on k3d-zero-door.

One file, two halves, so that the reviewed bytes are exactly what runs in the lab:

  host   Orchestrator: phases P0-P7 of docs/runbooks/dashboard-and-baselines.md section 5 through
         kubectl argv lists (explicit --context, --request-timeout, no shell), the budget and
         deadlines, abort and an always-run cleanup by name + label + UID. Every cluster write goes
         through `Orchestrator.write`, which refuses anything outside ACTIONS. P8 scores the pulled
         exports with the ZER-10 CLI and registers them for serve-results (offline).
  pod    Agent: runs in a temporary pod from an existing ZER-10 image with this file mounted from a
         ConfigMap. It owns the production H/O gateways (event_pipeline.gateway, durable 201 ack), the
         harness/evaluator producers, one ZER-10 ProbeRunner per trial, the effect evaluator, the
         recovery evaluator (measurement.recovery.RecoveryMonitor) and AUDIT_COVERAGE, then seals and
         exports. The host reaches it only with `kubectl exec ... call <json>`.

Importing this module starts nothing and opens no connection. The agent half imports event_pipeline
and measurement lazily. Nothing here decides that a run is allowed: `--execute` with an approval
reference only records who approved; the approval itself is Hoang's, outside this code.
"""
import copy
import hashlib
import io
import json
import math
import os
import re
import secrets
# subprocess runs fixed kubectl argv lists only, never through a shell.
import subprocess  # nosec B404
import sys
import tarfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

CONTEXT = "k3d-zero-door"
RUN_LABEL = "zero-door.io/run"
RESOURCE = {"Namespace": "namespace", "ConfigMap": "configmap", "Pod": "pod", "Deployment": "deploy", "HorizontalPodAutoscaler": "hpa"}
AGENT_POD = "zd-rt1-agent"
LOAD_POD = "zd-rt1-load"
CANARY = "zd-scale-canary"
HARNESS_CM = "zd-rt1-harness"
PROFILES_CM = "zd-r1-baseline-profiles"
HPAS = ("frontend-hpa-r1", "cartservice-hpa-r1")
TARGETS = ("frontend", "cartservice")
ZD_COMPONENTS = ("gaia", "hephaestus")
EFFECT_CRITERIA = "zd-rt1-effect/0: first failing probe sample in [T_req, T_req + W_eff]"
FORM = {"email": "probe@example.invalid", "street_address": "1 Lab Road", "zip_code": "10000", "city": "Local",
        "state": "LC", "country": "Lab", "credit_card_number": "4432801561520454",
        "credit_card_expiration_month": "1", "credit_card_expiration_year": "2030", "credit_card_cvv": "672"}

# The pod's own emptyDir mount (fresh and private to the agent pod), not a shared host temp directory.
AGENT_ROOT = "/tmp/rt1"  # nosec B108
# Execution settings that are not part of the RT1 budget arithmetic. The image is the existing ZER-10
# measurement image (runtime-01 attempt-03): its measurement/ and event_pipeline/ equal this tree's
# files byte for byte (source-manifest.json). Nothing is built.
EXEC = {
    "image": "zero-door/measurement:zer10-574a0c3a2dad",
    "image_id": "sha256:baf75538e5b84408f7d53d55b3c8601cb0f6221b3703d3cf05a877dce82d8932",
    "node": "k3d-zero-door-server-0", "mount": "/app/rt1", "agent_root": AGENT_ROOT, "agent_port": 9140,
    "probe": {"probe_id": "prb-rt1", "probe_version": "p1", "flow": "checkout", "clock_id": "clk-rt1"},
    "product": "OLJCESPC7Z", "product_marker": "Sunglasses",
    "timeouts": {"step_s": 3, "transaction_s": 10}, "heartbeat_s": 2, "grace_s": 10,
    "provenance": "PILOT", "method_version": "zd-rt1/0 B0 baseline (F-01 PILOT inputs)",
    "poll_s": 2, "watch_gap_s": 10, "ack_stall_s": 15, "call_timeout_s": 20, "agent_call_s": 30,
    "pod_ready_s": 90, "scale_wait_s": 90, "namespace_gone_s": 120, "load_grace_s": 30, "baseline_grace_s": 60,
    "export_tar_s": 60, "kubectl": "kubectl",
}

# The complete list of cluster writes (phase, verb, kind, object, rollback). `Orchestrator.write`
# refuses a write whose (phase, verb, kind, name) is not here; the test checks every recorded write.
ACTIONS = [
    ("P1", "create", "Namespace", "zd-zer11-<nonce>", "P7 delete with uid precondition, then read back absent"),
    ("P1", "create", "ConfigMap", HARNESS_CM, "removed with the namespace"),
    ("P1", "delete", "ConfigMap", HARNESS_CM, "self-test with a WRONG uid: must be refused (Conflict) and the ConfigMap must remain"),
    ("P1", "create", "Pod", AGENT_POD, "removed with the namespace (evidence pulled first)"),
    ("P1", "create", "ConfigMap", PROFILES_CM, "P7 delete with uid precondition"),
    ("P1", "scale", "Deployment", "gaia", "P7 scale back to the P0 replicas (uid, spec and resourceVersion checked)"),
    ("P1", "scale", "Deployment", "hephaestus", "P7 scale back to the P0 replicas (uid, spec and resourceVersion checked)"),
    ("P2", "create", "Deployment", CANARY, "removed with the namespace"),
    ("P2", "scale", "Deployment", CANARY, "0 -> 1 -> 0 inside the namespace"),
    ("P3", "delete", "Pod", "frontend-*", "none: the ReplicaSet controller recreating it is the observation; exactly 1, uid precondition"),
    ("P4", "create", "HorizontalPodAutoscaler", HPAS[0], "P7 delete with uid precondition"),
    ("P4", "create", "HorizontalPodAutoscaler", HPAS[1], "P7 delete with uid precondition"),
    ("P4", "create", "Pod", LOAD_POD, "removed with the namespace; deleted by uid if it outlives the load window"),
    ("P4", "delete", "Pod", LOAD_POD, "same"),
    ("P7", "delete", "HorizontalPodAutoscaler", HPAS[0], "cleanup"),
    ("P7", "delete", "HorizontalPodAutoscaler", HPAS[1], "cleanup"),
    ("P7", "scale", "Deployment", "frontend", "CLEANUP: back to the P0 replicas after the HPA is gone; never evidence of recovery"),
    ("P7", "scale", "Deployment", "cartservice", "CLEANUP: same"),
    ("P7", "scale", "Deployment", "gaia", "CLEANUP: back to the P0 replicas"),
    ("P7", "scale", "Deployment", "hephaestus", "CLEANUP: back to the P0 replicas"),
    ("P7", "delete", "ConfigMap", PROFILES_CM, "cleanup"),
    ("P7", "delete", "Namespace", "zd-zer11-<nonce>", "cleanup"),
]
WRITES = {(p, v, k, n) for p, v, k, n, _ in ACTIONS}


class HarnessError(RuntimeError):
    def __init__(self, reason, detail=None):
        super().__init__(reason if detail is None else f"{reason}: {detail}")
        self.reason, self.detail = reason, detail


class Abort(HarnessError):
    """Section 5.6: stop now, end the open trial at stop point (d), export, clean up."""


class DeadlineExceeded(HarnessError):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def module_sha256():
    return sha256(Path(__file__).read_bytes())


# --------------------------------------------------------------------------- plan arithmetic
def trial_budget(plan, name):
    """Probe plan budget of one trial: the plan-check worst case (warm-up + baseline + W_eff + cap_rec + S + margin)."""
    f, t = plan["f01"], plan["trials"][name]
    window = t["baseline_s"] + plan["w_eff_s"] + f["cap_rec_s"] + f["s_s"] + plan["stop_margin_s"]
    duration = t["warmup_s"] + window
    samples = int(math.floor(duration / f["delta_s"] + 1e-9))
    return {"max_duration_s": duration, "max_samples": samples, "max_requests": samples * plan["requests_per_sample"],
            "trial_window_s": window}


def config(plan, overrides=None):
    """RT1 plan (verify-dashboard-baselines.RT1) + EXEC. Overrides exist for the offline fakes only."""
    cfg = copy.deepcopy(EXEC)
    for key, value in (overrides or {}).items():
        cfg[key] = dict(cfg[key], **value) if isinstance(cfg.get(key), dict) and isinstance(value, dict) else value
    cfg["plan"] = copy.deepcopy(plan)
    cfg["budgets"] = {name: trial_budget(plan, name) for name in plan["trials"]}
    return cfg


def matrix(plan, cfg=None):
    """What `rt1` prints without --execute: phases, every write and its rollback, budgets, image."""
    cfg = cfg or config(plan)
    return {"id": plan["id"], "context": plan["context"], "image": {k: cfg[k] for k in ("image", "image_id", "node")},
            "image_note": "existing ZER-10 image, imagePullPolicy Never, no build; this file mounted read-only from a ConfigMap",
            "f01_pilot": plan["f01"], "w_eff_s": plan["w_eff_s"], "probe_budgets": cfg["budgets"],
            "phases_s": plan["phases_s"], "caps": plan["caps"],
            "writes": [dict(zip(("phase", "verb", "kind", "name", "rollback"), a)) for a in ACTIONS],
            "reads": "get/auth can-i/version/config get-contexts/create --dry-run=client (local conversion); exec into the agent pod",
            "stop_points": {"a": "RECOVERY_VERIFIED evidence_complete_at + stop margin", "b": "samples cover [T_req, T_req + W_eff] without failure",
                            "c": "samples reach T_eff + cap_rec + S + margin without verified recovery (scorer: TIMEOUT if covered)",
                            "d": "abort, total cap, probe budget, coverage gap in W_eff: MISSING_PROBE / UNKNOWN_EFFECT, never TIMEOUT or PASS"},
            "abort": ["wrong context", "foreign HPA on frontend/cartservice", "node NotReady", "Gaia/Hephaestus pod in the B0 window",
                      "accepted O decision/action event", "H/O persistence or ack stall", "budget cap", "positive control failed",
                      "baseline unhealthy", "interrupt"]}


# =========================================================================== pod half
class Agent:
    """In-pod harness. Commands are JSON objects; `handle` never raises (errors come back as reason codes)."""

    def __init__(self, root, http=None, wall=None):
        self.root = Path(root)
        if (self.root / "work").exists():
            raise HarnessError("AGENT_ROOT_NOT_FRESH")
        (self.root / "work").mkdir(parents=True)
        self.http, self.wall = http, wall
        self.lock = threading.Lock()
        self.cfg = self.run = self.pc = None
        self.trials, self.current, self.failure = {}, None, None
        self.servers, self.deliveries = [], []

    # ------------------------------------------------------------- plumbing
    def handle(self, command):
        try:
            with self.lock:
                action = command.get("action")
                method = getattr(self, "cmd_" + str(action), None)
                if method is None:
                    raise HarnessError("UNKNOWN_ACTION")
                answer = method(command)
                # "ok" is transport/dispatch only; a command's own outcome travels in its own fields.
                if "ok" in answer:
                    raise HarnessError("RESULT_SHADOWS_OK", action)
                return dict(answer, ok=True)
        except HarnessError as error:
            return {"ok": False, "error": error.reason, "detail": error.detail}
        except Exception as error:  # reported as a code; the evidence files keep the rest
            return {"ok": False, "error": "AGENT_" + type(error).__name__}

    def now_ms(self):
        return self.clock.now_ms()

    def deliver(self, publisher, event, expect="DELIVERED"):
        """Outbox first (fsync), then the gateway; a control event that is not durably admitted stops the run."""
        from measurement.sink import PersistenceFailure, SinkRefused
        started = time.perf_counter_ns()
        deadline = started + int(self.cfg["grace_s"] * 1e9)
        retries = publisher.counts["retries"]
        record = {"event_type": event["event_type"], "event_id": event["event_id"], "deadline_ms": round(self.cfg["grace_s"] * 1000)}
        self.deliveries.append(record)
        try:
            publisher.put(event, deadline_ns=deadline)
            publisher.flush(max_attempts=3, deadline_ns=deadline)
        except (PersistenceFailure, SinkRefused) as error:
            self.failure = self.failure or "CONTROL_" + type(error).__name__
            raise HarnessError("CONTROL_NOT_DURABLE", type(error).__name__) from None
        finally:
            record.update(ms=round((time.perf_counter_ns() - started) / 1e6, 1), retries=publisher.counts["retries"] - retries,
                          state=publisher.outbox.states.get(event["event_id"]))
        state = record["state"]
        if state != expect:
            if expect == "DELIVERED":
                self.failure = self.failure or "CONTROL_NOT_DURABLE"
            raise HarnessError("CONTROL_NOT_DURABLE" if expect == "DELIVERED" else "UNEXPECTED_ADMISSION",
                               f"{event['event_type']} {state} after {record['ms']} ms, {record['retries']} retries")
        return state

    def publisher(self, name, plane, role):
        from measurement.sink import HttpHSink, Outbox, Publisher
        url = self.urls[plane]
        return Publisher(Outbox(self.root / "work" / f"{name}.outbox.jsonl"), HttpHSink(url, self.keys[plane][role]))

    def emit(self, who, context, typ, payload, stream, target=None, **ids):
        from measurement.clock import stamp
        producer, publisher = self.producers[who]
        event = producer.event(context, typ, payload, stream, target=target, ts_event=stamp(self.now_ms()), **ids)
        self.deliver(publisher, event)
        return event

    # ------------------------------------------------------------- commands
    def cmd_hello(self, command):
        return {"module_sha256": module_sha256(), "python": sys.version.split()[0]}

    def cmd_start_run(self, command):
        from event_pipeline.contract import Producer, new_id
        from event_pipeline.gateway import Gateway, server
        from event_pipeline.store import Archive
        from measurement.clock import ProbeClock
        if self.run:
            raise HarnessError("RUN_ALREADY_STARTED")
        self.cfg = command["config"]
        probe = self.cfg["probe"]
        self.clock = ProbeClock(probe["clock_id"], "HOST_SHARED", **({"wall": self.wall} if self.wall else {}))
        roles = {"H": ("harness", "probe", "effect_evaluator", "recovery_evaluator", "evaluator"),
                 "O": ("harness", "decision_rules", "evaluator")}
        # Fresh random keys held in memory only; H and O are separate archives, roots and key sets.
        self.keys = {plane: {role: secrets.token_hex(32) for role in names} for plane, names in roles.items()}
        self.archives, self.gateways, self.urls = {}, {}, {}
        for plane in ("H", "O"):
            archive = Archive(self.root / ("archive-" + plane), plane)
            gateway = Gateway(archive, self.keys[plane])
            http = server(gateway, ("127.0.0.1", 0))
            threading.Thread(target=http.serve_forever, daemon=True).start()
            self.servers.append(http)
            self.archives[plane], self.gateways[plane] = archive, gateway
            self.urls[plane] = f"http://127.0.0.1:{http.server_address[1]}"
        version = "zd-rt1/" + module_sha256()[:12]
        env = self.clock.envelope()
        self.producers = {
            "harness": (Producer("harness", version, env), self.publisher("harness-h", "H", "harness")),
            "context": (Producer("harness", version, env), self.publisher("harness-o", "O", "harness")),
            "effect": (Producer("effect_evaluator", version, env), self.publisher("effect", "H", "effect_evaluator")),
            "recovery": (Producer("recovery_evaluator", version, env), self.publisher("recovery", "H", "recovery_evaluator")),
        }
        self.run = {"run_id": new_id("run"), "trial_id": None, "group": "B0",
                    "method_version": self.cfg["method_version"], "config_ref": self.cfg["config_ref"]}
        self.emit("harness", self.run, "RUN_STARTED", {
            "canary_token": "rt1-" + secrets.token_hex(16), "protocol_ref": self.cfg["protocol_ref"],
            "schedule_ref": self.cfg["schedule_ref"], "f01_params": self.cfg["plan"]["f01"],
            "reference_clock_id": probe["clock_id"]}, "h.control")
        self.emit("context", self.run, "RUN_CONTEXT", {}, "o.context")
        return {"run_id": self.run["run_id"], "clock": env}

    def cmd_positive_control(self, command):
        """P2 (1)+(2) in a separate B0 run, outside the main cohort: a valid O event is recorded and a
        RULES decision for B0 is durably quarantined as MODE_VIOLATION by the production gateway."""
        from event_pipeline.contract import Producer, new_id
        from measurement.clock import stamp
        env = self.clock.envelope()
        harness = Producer("harness", "zd-rt1-positive-control", env)
        h_pub, o_pub = self.publisher("pc-harness-h", "H", "harness"), self.publisher("pc-harness-o", "O", "harness")
        run = dict(self.run, run_id=new_id("run"))
        trial = dict(run, trial_id=new_id("trl"))
        mk = lambda ctx, typ, payload, stream: harness.event(ctx, typ, payload, stream, ts_event=stamp(self.now_ms()))
        self.deliver(h_pub, mk(run, "RUN_STARTED", {"canary_token": "rt1-pc-" + secrets.token_hex(8),
                     "protocol_ref": self.cfg["protocol_ref"] + " positive control", "schedule_ref": self.cfg["schedule_ref"],
                     "f01_params": self.cfg["plan"]["f01"], "reference_clock_id": env["clock_id"]}, "h.control"))
        self.deliver(o_pub, mk(run, "RUN_CONTEXT", {}, "o.context"))
        start = self.now_ms()
        self.deliver(h_pub, mk(trial, "TRIAL_STARTED", {"warmup_end": stamp(start),
                     "planned_window": {"start": stamp(start), "end": stamp(start)}, "probes": []}, "h.control"))
        context_event = mk(trial, "TRIAL_CONTEXT", {}, "o.context")
        self.deliver(o_pub, context_event)
        recorded = any(r["envelope"]["event_id"] == context_event["event_id"] for r in self.archives["O"].records(run["run_id"]))
        # Built as a valid B1 decision, then put in the B0 run: the gateway's validator must refuse it.
        rules = Producer("decision_rules", "zd-rt1-positive-control", env)
        decision = rules.event(dict(trial, group="B1"), "DECISION", {
            "stage": "PROPOSAL", "decision_source": "RULES", "inputs": [], "response_kind": "NO_ACTION", "proposal": None,
            "fallback": False, "fallback_of": None, "prompt_version": None, "prompt_sha256": None,
            "evidence_package_version": "rt1-positive-control"}, "o.decision", ts_event=stamp(self.now_ms()),
            decision_id=new_id("dec"))
        decision["group"] = "B0"
        from measurement.sink import HttpHSink, Outbox, Publisher
        d_pub = Publisher(Outbox(self.root / "work" / "pc-decision.outbox.jsonl"), HttpHSink(self.urls["O"], self.keys["O"]["decision_rules"]))
        d_deadline = time.perf_counter_ns() + int(self.cfg["grace_s"] * 1e9)
        d_pub.put(decision, deadline_ns=d_deadline)
        d_pub.flush(max_attempts=3, deadline_ns=d_deadline)  # still pending after this: the control fails below
        state = d_pub.outbox.states.get(decision["event_id"])
        detail = None
        for line in (d_pub.outbox.path.read_text().splitlines()):
            record = json.loads(line)
            if record.get("op") == "state" and record.get("event_id") == decision["event_id"]:
                detail = record.get("detail")
        self.deliver(h_pub, mk(trial, "TRIAL_ENDED", {"end_reason": "PLANNED"}, "h.control"))
        self.deliver(h_pub, mk(run, "RUN_CLOSED", {"close_reason": "COMPLETED", "recorder_manifest_ref": "export-H/manifest.json"}, "h.control"))
        self.pc = {"run_id": run["run_id"], "trial_id": trial["trial_id"], "valid_o_event_recorded": recorded,
                   "decision_state": state, "decision_classification": detail}
        self.pc["passed"] = control_passed(self.pc)
        return {"control": dict(self.pc)}

    def cmd_start_trial(self, command):
        from event_pipeline.contract import new_id
        from measurement.clock import stamp
        from measurement.config import plan as check_plan
        from measurement.flows import Flow, boutique_spec
        from measurement.probe import ProbeRunner
        from measurement.sink import HttpHSink, Journal, Outbox
        name = command["name"]
        if self.current is not None or name in self.trials or name not in self.cfg["budgets"]:
            raise HarnessError("TRIAL_REFUSED")
        if self.failure:
            raise HarnessError("AGENT_FAILED", self.failure)
        budget = self.cfg["budgets"][name]
        p = self.cfg["probe"]
        origin = self.cfg["origin"]
        plan = check_plan({"plan_version": "zd-measurement-plan/0", "provenance": self.cfg["provenance"], "f01": self.cfg["plan"]["f01"],
                           "probe": dict(p, clock_source="HOST_SHARED"), "timeouts": self.cfg["timeouts"],
                           "budget": {"max_duration_s": budget["max_duration_s"], "max_samples": budget["max_samples"],
                                      "max_requests": budget["max_requests"], "grace_s": self.cfg["grace_s"]},
                           "heartbeat_s": self.cfg["heartbeat_s"], "target": {"origin": origin, "allowed_origins": [origin]}})
        spec = boutique_spec(self.cfg["product"], self.cfg["product_marker"], FORM)
        flow = Flow(spec, plan["target"]["origin"], plan["target"]["allowed_origins"])
        context = dict(self.run, trial_id=new_id("trl"))
        trial = Trial(self, name, context, plan)
        publisher = tap_publisher(Outbox(self.root / "work" / f"{name}.probe.outbox.jsonl"),
                                 HttpHSink(self.urls["H"], self.keys["H"]["probe"]), trial)
        target = {"namespace": "target-app", "service": "frontend", "flow": p["flow"]}
        trial.runner = ProbeRunner(plan, flow, context, self.clock, publisher,
                                   journal=Journal(self.root / "work" / f"{name}.journal.jsonl"), target=target,
                                   **({"http": self.http} if self.http else {}))
        start = self.now_ms()
        t = self.cfg["plan"]["trials"][name]
        trial.start_ms = start
        trial.ready_ms = start + (t["warmup_s"] + t["baseline_s"]) * 1000
        self.emit("context", context, "TRIAL_CONTEXT", {}, "o.context")
        self.emit("harness", context, "TRIAL_STARTED", {
            "warmup_end": stamp(start + t["warmup_s"] * 1000),
            "planned_window": {"start": stamp(start + t["warmup_s"] * 1000), "end": stamp(start + budget["max_duration_s"] * 1000)},
            "probes": [trial.runner.registration()]}, "h.control")
        self.trials[name], self.current = trial, trial
        trial.thread = threading.Thread(target=trial.run_probe, daemon=True)
        trial.thread.start()
        return {"trial_id": context["trial_id"], "budget": budget}

    def active(self, name):
        trial = self.trials.get(name)
        if trial is None or trial is not self.current:
            raise HarnessError("NO_ACTIVE_TRIAL")
        return trial

    def cmd_status(self, command):
        trial = self.current
        if trial is not None and command.get("watch") is not None:
            trial.tick(command["watch"])
        out = {"failure": self.failure, "o_actions": self.o_actions(), "trial": trial.status() if trial else None}
        return out

    def o_actions(self):
        """Accepted O events of the main run other than RUN/TRIAL_CONTEXT (B0 must have none)."""
        if not self.run:
            return 0
        try:
            return sum(1 for r in self.archives["O"].records(self.run["run_id"])
                       if r["envelope"]["event_type"] not in {"RUN_CONTEXT", "TRIAL_CONTEXT"})
        except Exception:
            self.failure = self.failure or "O_ARCHIVE_UNREADABLE"
            return None

    def cmd_attack_requested(self, command):
        trial = self.active(command["name"])
        return trial.request(command)

    def cmd_attack_stopped(self, command):
        trial = self.active(command["name"])
        return trial.stopped(command["stop_reason"], bool(command["executor_confirmed"]), command.get("evidence"))

    def cmd_end_trial(self, command):
        trial = self.active(command["name"])
        if command.get("watch") is not None:
            trial.tick(command["watch"])
        summary = trial.finish(command.get("reason"))
        self.current = None
        return summary

    def cmd_abort(self, command):
        trial = self.current
        if trial is None:
            return {"trial": None}
        if trial.incident and not trial.attack_stopped:
            try:
                trial.stopped("ABORTED", bool(command.get("fault_ended")), {"abort_reason": command.get("reason")})
            except HarnessError:
                pass  # the summary's unrecorded list and the outbox keep it; the trial still ends
        summary = trial.finish("ABORTED:" + str(command.get("reason")))
        self.current = None
        return {"trial": summary}

    def cmd_close(self, command):
        """RUN_CLOSED, seal and export both planes of the main and positive-control runs into out/."""
        out = self.root / "out"
        if out.exists():
            raise HarnessError("ALREADY_CLOSED")
        out.mkdir()
        result = {"exports": {}, "errors": {}}
        if self.run:
            try:
                self.emit("harness", self.run, "RUN_CLOSED", {"close_reason": command.get("close_reason", "COMPLETED"),
                                                             "recorder_manifest_ref": "export-H/manifest.json"}, "h.control")
            except HarnessError as error:
                result["errors"]["RUN_CLOSED"] = error.reason
            runs = [("", self.run["run_id"])] + ([("pc-", self.pc["run_id"])] if self.pc else [])
            for prefix, run in runs:
                for plane in ("H", "O"):
                    name = f"{prefix}export-{plane}"
                    try:
                        self.gateways[plane].seal(run)
                        manifest = self.archives[plane].export(run, out / name)
                        result["exports"][name] = {"run_id": run, "raw_sha256": manifest["sha256"],
                                                   "export_json_sha256": sha256((out / name / "export.json").read_bytes())}
                    except Exception as error:
                        result["errors"][name] = type(error).__name__
        (out / "work").mkdir()
        for path in sorted((self.root / "work").iterdir()):
            (out / "work" / path.name).write_bytes(path.read_bytes())
        receipt = {"module_sha256": module_sha256(), "run": self.run, "positive_control": self.pc, "failure": self.failure,
                   "control_deliveries": self.deliveries,
                   "trials": {n: t.summary for n, t in self.trials.items()}, "close": result}
        (out / "agent-receipt.json").write_bytes(canonical(receipt) + b"\n")
        return result

    def shutdown(self):
        for http in self.servers:
            http.shutdown()
            http.server_close()
        for archive in getattr(self, "archives", {}).values():
            archive.close()


def tap_publisher(outbox, sink, trial):
    """The probe's own Publisher; after each put/flush, durably delivered PROBE_SAMPLEs go to the trial in order."""
    from measurement.sink import Publisher

    class Tap(Publisher):
        def put(self, event, deadline_ns=None):
            super().put(event, deadline_ns)
            trial.after_put(self, event)

        def flush(self, max_attempts=1, deadline_ns=None):
            left = super().flush(max_attempts, deadline_ns)
            trial.after_put(self, None)
            return left
    return Tap(outbox, sink)


class Trial:
    """One trial: stop rules of runbook 5.4 on durably recorded samples only."""

    def __init__(self, agent, name, context, plan):
        self.agent, self.name, self.context, self.plan = agent, name, context, plan
        cfg = agent.cfg["plan"]
        self.f = cfg["f01"]
        self.w_ms, self.margin_ms = cfg["w_eff_s"] * 1000, cfg["stop_margin_s"] * 1000
        self.gap_ms = self.f["gap_s"] * 1000
        self.lock = threading.RLock()
        self.pending, self.samples = [], []
        self.incident = None
        self.t_req = self.effect = self.monitor = self.verified = self.stop_point = self.stop_reason = None
        self.attack_stopped = False
        self.ticks = []
        self.undelivered_since = None
        self.summary = None
        self.runner = self.thread = self.probe_summary = None
        self.emitted = []

    # --- probe side (probe thread)
    def run_probe(self):
        try:
            self.probe_summary = self.runner.run()
        except Exception as error:  # never silent: becomes stop point (d)
            self.probe_summary = {"stop_reason": "PROBE_" + type(error).__name__}
        with self.lock:
            if self.stop_point is None:
                self.stop("d", "PROBE_ENDED:" + str(self.probe_summary.get("stop_reason")), stop_runner=False)

    def after_put(self, publisher, event):
        if event is not None and event["event_type"] == "PROBE_SAMPLE":
            self.pending.append(event)
        states = publisher.outbox.states
        with self.lock:
            while self.pending and states.get(self.pending[0]["event_id"]) == "DELIVERED":
                self.on_sample(self.pending.pop(0))
            self.undelivered_since = (self.undelivered_since or time.monotonic()) if publisher.outbox.pending else None

    def on_sample(self, event):
        from measurement.clock import parse
        p = event["payload"]
        s = {"t": parse(p["t_start"]), "end": parse(p["t_end"]), "ok": p["pass"], "seq": p["sequence"], "event_id": event["event_id"],
             "probe_id": p["probe_id"], "probe_version": p["probe_version"], "flow": p["flow"]}
        self.samples.append(s)
        if self.stop_point is not None:
            return
        try:
            if self.t_req is not None and self.effect is None:
                self.evaluate_effect()
            if self.monitor is not None:
                self.monitor.add(s)
                for typ, payload in self.monitor.poll():
                    if typ == "RECOVERY_VERIFIED":
                        self.not_before(payload["evidence_complete_at"])
                    self.emitted.append(self.agent.emit("recovery", self.inc_context(), typ, payload, "h.recovery"))
                    if typ == "RECOVERY_VERIFIED":
                        from measurement.clock import parse as parse_stamp
                        self.verified = parse_stamp(payload["evidence_complete_at"])
            self.check_stop(s)
        except HarnessError as error:
            self.stop("d", error.reason)

    def not_before(self, text):
        """t_end is the wall start plus monotonic elapsed time, so it can lie a little ahead of the next
        wall reading. RECOVERY_VERIFIED must not carry a ts_event before evidence_complete_at (scorer:
        published_before_evidence_complete), so wait until the harness clock has passed it."""
        from measurement.clock import parse
        done, limit = parse(text), time.monotonic() + 2
        while self.agent.now_ms() < done:
            if time.monotonic() > limit:
                raise HarnessError("CLOCK_BEHIND_EVIDENCE")
            time.sleep(0.001)

    def inc_context(self):
        return dict(self.context, incident_id=self.incident)

    def evaluate_effect(self):
        from measurement.clock import stamp
        from measurement.recovery import joined
        after = [x for x in self.samples if x["t"] >= self.t_req]
        end = self.t_req + self.w_ms
        window = [x for x in after if x["t"] <= end]
        fail = next((x for x in window if not x["ok"]), None)
        evidence = {"flow": self.agent.cfg["probe"]["flow"], "first_sample_t": stamp(window[0]["t"]) if window else None,
                    "last_sample_t": stamp(window[-1]["t"]) if window else None,
                    "max_gap_s": round(max([b["t"] - a["t"] for a, b in zip(window, window[1:])] or [0]) / 1000, 3),
                    "sample_seq_range": [window[0]["seq"], window[-1]["seq"]] if window else None}
        if fail is not None:
            status, t_eff, reason = "CONFIRMED", fail["t"], "FIRST_FAILING_SAMPLE"
        elif after and after[-1]["t"] > end:
            covered = bool(window) and window[0]["t"] - self.t_req <= self.gap_ms and end - window[-1]["t"] <= self.gap_ms \
                and all(joined(a, b, self.gap_ms) for a, b in zip(window, window[1:]))
            status, t_eff = ("CONFIRMED_NO_EFFECT", None) if covered else ("UNKNOWN_EFFECT", None)
            reason = "COVERED_WITHOUT_FAILURE" if covered else "W_EFF_NOT_COVERED"
        else:
            return
        self.publish_effect(status, t_eff, evidence, reason)

    def publish_effect(self, status, t_eff, evidence, reason):
        from measurement.clock import stamp
        from measurement.recovery import RecoveryMonitor
        cfg = self.agent.cfg
        self.effect = {"status": status, "t_eff": t_eff, "reason": reason}
        self.emitted.append(self.agent.emit("effect", self.inc_context(), "EFFECT_EVALUATED", {
            "status": status, "t_eff": stamp(t_eff) if t_eff is not None else None,
            "evidence_clock_id": cfg["probe"]["clock_id"], "criteria_version": EFFECT_CRITERIA,
            "w_eff_s": cfg["plan"]["w_eff_s"], "evidence": evidence, "reason": reason}, "h.effect"))
        if status == "CONFIRMED":
            p = cfg["probe"]
            self.monitor = RecoveryMonitor(t_eff, self.f, {"probe_id": p["probe_id"], "probe_version": p["probe_version"],
                                                           "flow": p["flow"]}, p["clock_id"])
            for x in self.samples:
                self.monitor.add(x)

    def check_stop(self, s):
        if self.effect is None:
            return
        status = self.effect["status"]
        if status == "CONFIRMED_NO_EFFECT":
            self.stop("b", "NO_EFFECT_COVERED")
        elif status == "UNKNOWN_EFFECT":
            self.stop("d", "W_EFF_NOT_COVERED")
        elif self.verified is not None and s["t"] >= self.verified + self.margin_ms:
            self.stop("a", "RECOVERY_VERIFIED")
        elif self.verified is None and s["t"] >= self.effect["t_eff"] + (self.f["cap_rec_s"] + self.f["s_s"]) * 1000 + self.margin_ms:
            self.stop("c", "CAP_REC_REACHED")

    def stop(self, point, reason, stop_runner=True):
        with self.lock:
            if self.stop_point is None:
                self.stop_point, self.stop_reason = point, reason
        if stop_runner and self.runner is not None:
            self.runner.stop(interrupted=False)

    # --- host side (control thread)
    def tick(self, watch):
        with self.lock:
            self.ticks.append({"t": self.agent.now_ms(), "ok": bool(watch.get("ok")), "detail": watch})

    def status(self):
        with self.lock:
            last = self.samples[-1] if self.samples else None
            recent = self.samples[-self.f["k"]:]
            now = self.agent.now_ms()
            healthy = len(recent) == self.f["k"] and all(x["ok"] for x in recent) and now - recent[-1]["t"] <= self.gap_ms * 2
            phase = ("STOPPED" if self.stop_point else "OBSERVING" if self.t_req is not None else
                     "READY_FOR_FAULT" if now >= self.ready_ms and healthy else "BASELINE")
            stall = None if self.undelivered_since is None else round(time.monotonic() - self.undelivered_since, 3)
            return {"name": self.name, "phase": phase, "samples": len(self.samples), "last_ok": last and last["ok"],
                    "effect": self.effect and self.effect["status"], "verified": self.verified is not None,
                    "stop_point": self.stop_point, "stop_reason": self.stop_reason, "undelivered_s": stall,
                    "probe_done": self.probe_summary is not None,
                    "probe_stop": self.probe_summary and self.probe_summary.get("stop_reason")}

    def request(self, command):
        from event_pipeline.contract import new_id
        from measurement.clock import parse
        with self.lock:
            if self.status()["phase"] != "READY_FOR_FAULT" or self.incident:
                raise HarnessError("NOT_READY_FOR_FAULT")
            self.incident = new_id("inc")
        event = self.agent.emit("harness", self.inc_context(), "ATTACK_REQUESTED", {
            "variant_ref": command["variant_ref"], "fault_params": command["fault_params"],
            "attack_command": command["attack_command"], "seed": None,
            "onset_offset_ms": round(self.agent.now_ms() - self.start_ms), "s_att": None, "known_good_revision": None,
            "target_services": command["target_services"]}, "h.control",
            target={"namespace": "target-app", "service": command["target_services"][0], "flow": self.agent.cfg["probe"]["flow"]})
        with self.lock:
            self.t_req = parse(event["ts_event"])
        return {"incident_id": self.incident, "t_req": event["ts_event"]}

    def stopped(self, stop_reason, confirmed, evidence=None):
        if not self.incident or self.attack_stopped:
            raise HarnessError("NO_OPEN_ATTACK")
        payload = {"stop_reason": stop_reason, "executor_confirmed": confirmed}
        if evidence:
            payload["executor_evidence"] = evidence  # additive (MINOR); H only
        event = self.agent.emit("harness", self.inc_context(), "ATTACK_STOPPED", payload, "h.control")
        self.attack_stopped = True
        return {"t_stop": event["ts_event"]}

    def coverage(self, start, end):
        """B0 absence watch: host reads delivered here, stamped on the harness clock."""
        gap = self.agent.cfg["watch_gap_s"] * 1000
        ticks = sorted(self.ticks, key=lambda x: x["t"])
        times = [start] + [x["t"] for x in ticks] + [end]
        max_gap = max(b - a for a, b in zip(times, times[1:]))
        o_actions = self.agent.o_actions()
        ok = bool(ticks) and all(x["ok"] for x in ticks) and max_gap <= gap and o_actions == 0
        failed = [x["detail"] for x in ticks if not x["ok"]][:5]
        return {"complete": ok, "ticks": len(ticks), "max_gap_s": round(max_gap / 1000, 3), "o_actions": o_actions,
                "failed_ticks": failed}

    def finish(self, reason=None):
        from measurement.clock import stamp
        if reason:
            self.stop("d", reason)
        else:
            self.stop(self.stop_point or "d", self.stop_reason or "ENDED_BY_HOST")
        self.thread.join(timeout=self.plan["budget"]["grace_s"] + self.agent.cfg["timeouts"]["transaction_s"] + 5)
        with self.lock:
            if self.incident and self.effect is None:
                # Window not decided (stopped early): explicit UNKNOWN_EFFECT, never NO_EFFECT.
                try:
                    self.publish_effect("UNKNOWN_EFFECT", None, {"flow": self.agent.cfg["probe"]["flow"], "first_sample_t": None,
                                                                 "last_sample_t": None, "max_gap_s": None, "sample_seq_range": None},
                                        "STOPPED_BEFORE_W_EFF_DECIDED")
                except HarnessError:
                    pass
            end = self.agent.now_ms()
            cov = self.coverage(self.start_ms, end)
            unrecorded, ended = [], None
            try:
                if cov["complete"]:
                    self.agent.emit("harness", self.context, "AUDIT_COVERAGE", {
                        "from": stamp(self.start_ms), "to": stamp(end), "complete": True, "scope": "B0_ZERO_DOOR_ABSENCE",
                        "watch": {k: cov[k] for k in ("ticks", "max_gap_s", "o_actions")}}, "h.control")
            except HarnessError:
                unrecorded.append("AUDIT_COVERAGE")
            end_reason = {"a": "PLANNED", "b": "PLANNED", "c": "HORIZON"}.get(self.stop_point, "ABORTED")
            try:
                ended = self.agent.emit("harness", self.context, "TRIAL_ENDED", {"end_reason": end_reason, "stop_point": self.stop_point,
                                                                                 "stop_reason": self.stop_reason}, "h.control")
            except HarnessError:
                unrecorded.append("TRIAL_ENDED")  # H not durable: said here, never assumed recorded
            self.summary = {"name": self.name, "trial_id": self.context["trial_id"], "incident_id": self.incident,
                            "stop_point": self.stop_point, "stop_reason": self.stop_reason, "end_reason": end_reason,
                            "effect": self.effect, "recovery_verified": self.verified is not None,
                            "audit_coverage": cov, "samples": len(self.samples), "probe": self.probe_summary,
                            "t_trial_end": ended and ended["ts_event"], "unrecorded": unrecorded}
            return self.summary


# --- pod entry points
def serve_agent(root, port):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    agent = Agent(root)

    class Control(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            try:
                size = int(self.headers.get("Content-Length", "0"))
                command = json.loads(self.rfile.read(size)) if 0 < size <= 65536 else {}
            except ValueError:
                command = {}
            result = agent.handle(command if isinstance(command, dict) else {})
            raw = canonical(result)
            self.send_response(200 if result.get("ok") else 409)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
    ThreadingHTTPServer(("127.0.0.1", port), Control).serve_forever()


def call_agent(port, raw):
    from http.client import HTTPConnection
    connection = HTTPConnection("127.0.0.1", port, timeout=120)
    connection.request("POST", "/", body=raw.encode(), headers={"Content-Type": "application/json"})
    response = connection.getresponse()
    print(response.read().decode())
    return 0 if response.status == 200 else 1


def run_load(origin, rps, connections, duration_s, max_requests):
    """B0-HPA load: bounded GET / on the frontend with the probe's own HTTP client (no new client)."""
    from measurement.flows import Failure, request
    lock, counts = threading.Lock(), {"sent": 0, "ok": 0, "error": 0}
    stop_at = time.monotonic() + duration_s
    interval = connections / rps

    def worker(offset):
        next_at = time.monotonic() + offset
        while True:
            with lock:
                if counts["sent"] >= max_requests or time.monotonic() >= stop_at:
                    return
                counts["sent"] += 1
            try:
                status = request(origin.rstrip("/") + "/", "GET", [], b"", time.perf_counter_ns() + int(5e9), None).status
                key = "ok" if status == 200 else "error"
            except Failure:
                key = "error"
            with lock:
                counts[key] += 1
            next_at += interval
            time.sleep(max(0.0, min(next_at - time.monotonic(), stop_at - time.monotonic())))
    threads = [threading.Thread(target=worker, args=(i * interval / connections,)) for i in range(connections)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(json.dumps(dict(counts, max_requests=max_requests, duration_s=duration_s), sort_keys=True))
    return 0


# =========================================================================== host half
class Clock:
    def monotonic(self):
        return time.monotonic()

    def sleep(self, seconds):
        if seconds > 0:
            time.sleep(seconds)


def run_argv(argv, stdin=None, timeout=None):
    """Default kubectl runner: argv list, no shell; (exit or None on timeout, stdout bytes, stderr bytes)."""
    try:
        done = subprocess.run(argv, input=stdin, capture_output=True, timeout=timeout)  # nosec B603
        return done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired:
        return None, b"", b"TIMEOUT"


class Kube:
    """kubectl with the context as one argv item and a timeout bounded by the caller's deadline."""

    def __init__(self, context, runner=run_argv, clock=None, binary="kubectl", call_timeout_s=20):
        if context != CONTEXT:
            raise HarnessError("WRONG_CONTEXT", context)
        self.context, self.runner, self.clock, self.binary = context, runner, clock or Clock(), binary
        self.call_timeout_s = call_timeout_s
        self.calls = []

    def run(self, args, deadline, stdin=None, timeout_s=None):
        left = deadline - self.clock.monotonic()
        if left <= 0.5:
            raise DeadlineExceeded("DEADLINE", " ".join(args[:3]))
        timeout = min(timeout_s or self.call_timeout_s, left)
        argv = [self.binary, "--context", self.context, f"--request-timeout={max(1, int(timeout))}s", *args]
        started = self.clock.monotonic()
        code, out, err = self.runner(argv, stdin, timeout)
        self.calls.append({"argv": argv[1:], "exit": code, "s": round(self.clock.monotonic() - started, 3)})
        return code, out, err

    def json(self, args, deadline, missing_ok=False, managed_fields=False):
        # kubectl get drops metadata.managedFields unless asked: field ownership reads must ask.
        code, out, err = self.run(args + ["-o", "json"] + (["--show-managed-fields=true"] if managed_fields else []), deadline)
        if code != 0:
            if missing_ok and b"NotFound" in err:
                return None
            raise HarnessError("KUBECTL_FAILED", " ".join(args[:3]) + ": " + err.decode(errors="replace")[-200:])
        return json.loads(out)


CONTROL_FACTS = ("valid_o_event_recorded", "decision_state", "decision_classification")


def control_passed(pc):
    """P2 (1)+(2): the valid O event is in the O archive and the B0 decision was durably quarantined as MODE_VIOLATION."""
    return pc.get("valid_o_event_recorded") is True and pc.get("decision_state") == "REJECTED" \
        and pc.get("decision_classification") == "MODE_VIOLATION"


def spec_hash(obj):
    spec = dict(obj["spec"])
    spec.pop("replicas", None)
    return sha256(canonical(spec))


def ready(pod):
    return pod.get("metadata", {}).get("deletionTimestamp") is None and any(
        c.get("type") == "Ready" and c.get("status") == "True" for c in pod.get("status", {}).get("conditions", []))


def selector(deploy):
    return ",".join(f"{k}={v}" for k, v in sorted(deploy["spec"]["selector"]["matchLabels"].items()))


def replica_managers(deploy):
    """Field managers owning spec.replicas (positive control: kubectl scale vs horizontal-pod-autoscaler)."""
    out = []
    for entry in deploy["metadata"].get("managedFields", []):
        fields = entry.get("fieldsV1", {})
        if "f:replicas" in fields.get("f:spec", {}):
            out.append({"manager": entry.get("manager"), "operation": entry.get("operation"), "subresource": entry.get("subresource")})
    return out


def event_time(event):
    text = event.get("eventTime") or event.get("lastTimestamp") or event.get("firstTimestamp")
    if not text:
        return None
    return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp() * 1000


def event_source(event):
    return event.get("reportingComponent") or (event.get("source") or {}).get("component")


class Orchestrator:
    def __init__(self, plan, kube, out_dir, approval_ref, cfg=None, clock=None, nonce=None,
                 manifest=None, runbook=None):
        self.plan, self.kube, self.approval = plan, kube, approval_ref
        self.cfg = cfg or config(plan)
        self.clock = clock or kube.clock
        self.out = Path(out_dir)
        self.out.mkdir(parents=True, exist_ok=False)
        root = Path(__file__).resolve().parents[2]
        self.manifest = Path(manifest or root / "infrastructure/manifests/r1-baselines.yaml")
        runbook = Path(runbook or root / "docs/runbooks/dashboard-and-baselines.md")
        self.nonce = nonce or secrets.token_hex(4)
        self.ns = f"zd-zer11-{self.nonce}"
        self.label = {RUN_LABEL: f"rt1-{self.nonce}"}
        self.config_ref = "sha256:" + sha256(self.manifest.read_bytes())
        self.protocol_ref = f"{plan['id']} runbook sha256:{sha256(runbook.read_bytes()) if runbook.exists() else 'absent'}"
        self.writes, self.created, self.phases, self.evidence = [], [], [], {"trials": {}}
        self.deletes = {"frontend_pod": 0}
        self.trials, self.cleanup_log = {}, []
        self.agent_up = self.pulled = False
        self.result = {"verdict": None}

    # ------------------------------------------------------------- helpers
    def now(self):
        return self.clock.monotonic()

    def deadline(self, allowance):
        return min(self.now() + allowance, self.main_deadline)

    def allowed(self, phase, verb, kind, name):
        key_name = "frontend-*" if (phase, kind) == ("P3", "Pod") else ("zd-zer11-<nonce>" if kind == "Namespace" else name)
        allowed_name = name.startswith("frontend-") if key_name == "frontend-*" else (name == self.ns if kind == "Namespace" else True)
        if (phase, verb, kind, key_name) not in WRITES or not allowed_name:
            raise HarnessError("WRITE_NOT_IN_ACTIONS", f"{phase} {verb} {kind} {name}")

    def write(self, phase, verb, kind, name, args, deadline, stdin=None, check=True):
        self.allowed(phase, verb, kind, name)
        code, out, err = self.kube.run(args, deadline, stdin=stdin)
        self.writes.append({"phase": phase, "verb": verb, "kind": kind, "name": name, "exit": code, "at": utc()})
        if check and code != 0:
            raise HarnessError("WRITE_FAILED", f"{verb} {kind} {name}: " + err.decode(errors="replace")[-200:])
        return code, out, err

    def create(self, phase, obj, deadline):
        """Every object this run creates carries the run label. The intent is recorded before the request, so
        a create the API accepted but whose answer was lost (timeout, broken connection) is still found by
        name + namespace + label and removed by uid in P7; it is never deleted by name alone."""
        kind, meta = obj["kind"], obj.setdefault("metadata", {})
        meta.setdefault("labels", {}).update(self.label)
        self.allowed(phase, "create", kind, meta["name"])
        record = {"kind": kind, "namespace": meta.get("namespace"), "name": meta["name"], "uid": None, "phase": phase, "state": "SENT"}
        self.created.append(record)
        code, out, err = self.write(phase, "create", kind, meta["name"], ["create", "-f", "-", "-o", "json"], deadline,
                                    stdin=canonical(obj), check=False)
        try:
            made = json.loads(out) if code == 0 else None
            uid = made and made["metadata"]["uid"]
        except (ValueError, KeyError, TypeError):
            made = uid = None
        if uid:
            record.update(uid=uid, state="CREATED")
            return made
        try:
            self.owned_uid(record, deadline)  # best effort now; P7 asks again for a record without a uid
        except HarnessError:
            pass
        raise HarnessError("WRITE_FAILED", f"create {kind} {meta['name']}: " + (err or b"").decode(errors="replace")[-200:])

    def owned_uid(self, record, deadline):
        """uid of an object this run created, read back by name + namespace + run label when the create's answer
        was lost. None: absent. Raises NOT_OURS when the name is held by an object without this run's label, and
        a kubectl error when ownership cannot be read (the object is then left alone and cleanup is INCOMPLETE)."""
        if record["uid"]:
            return record["uid"]
        args = ["get", RESOURCE[record["kind"]], record["name"]] + (["-n", record["namespace"]] if record["namespace"] else [])
        found = self.kube.json(args, deadline, missing_ok=True)
        if found is None:
            record["state"] = "ABSENT_AFTER_UNANSWERED_CREATE"
            return None
        if (found["metadata"].get("labels") or {}).get(RUN_LABEL) != self.label[RUN_LABEL] or not found["metadata"].get("uid"):
            record["state"] = "NAME_HELD_BY_OTHER_OBJECT"
            raise HarnessError("NOT_OURS", f"{record['kind']} {record['name']}")
        record.update(uid=found["metadata"]["uid"], state="RECONCILED")
        return record["uid"]

    def delete_owned(self, record, path, deadline):
        uid = self.owned_uid(record, deadline)
        if uid is None:
            return "ALREADY_ABSENT"
        return self.delete_exact("P7", record["kind"], path, record["name"], uid, deadline)

    def delete_exact(self, phase, kind, path, name, uid, deadline):
        """DELETE with a uid precondition: a recreated object of the same name is never touched. The
        DeleteOptions body goes on stdin (`-f -`), so no cleanup call depends on the host disk."""
        options = canonical({"kind": "DeleteOptions", "apiVersion": "v1", "preconditions": {"uid": uid},
                             "propagationPolicy": "Background"})
        code, _, err = self.write(phase, "delete", kind, name, ["delete", "--raw", path, "-f", "-"], deadline, stdin=options, check=False)
        if code == 0 or b"NotFound" in err or b"not found" in err:
            return "DELETED" if code == 0 else "ALREADY_ABSENT"
        if b"Precondition" in err or b"precondition" in err or b"Conflict" in err:
            return "UID_CHANGED_NOT_DELETED"
        raise HarnessError("DELETE_FAILED", f"{kind} {name}")

    def scale(self, phase, ns, name, current, target, rv, deadline):
        return self.write(phase, "scale", "Deployment", name, ["scale", f"deployment/{name}", "-n", ns, f"--current-replicas={current}",
                                                                f"--replicas={target}", f"--resource-version={rv}"], deadline)

    def agent(self, command, timeout=None, allow_error=False):
        args = ["exec", "-n", self.ns, AGENT_POD, "--", "python", "-B", f"{self.cfg['mount']}/r1_baseline_runtime.py", "call",
                json.dumps(command, sort_keys=True, separators=(",", ":"))]
        code, out, err = self.kube.run(args, self.call_deadline, timeout_s=timeout or self.cfg["agent_call_s"])
        try:
            answer = json.loads(out)
        except ValueError:
            raise HarnessError("AGENT_UNREACHABLE", err.decode(errors="replace")[-200:]) from None
        if not answer.get("ok") and not allow_error:
            if answer.get("error") in ("CONTROL_NOT_DURABLE", "AGENT_FAILED"):
                raise Abort("PERSISTENCE", answer.get("error") + (f": {answer['detail']}" if answer.get("detail") else ""))
            raise HarnessError("AGENT_" + str(answer.get("error")), answer.get("detail"))
        return answer

    def wait(self, what, check, allowance, interval=None):
        deadline = self.deadline(allowance)
        last = None
        while True:
            try:
                value = check(deadline)
            except DeadlineExceeded:
                raise
            except HarnessError as error:  # not there yet (pod starting, agent not listening): retry until the wait ends
                value, last = None, error.reason
            if value:
                return value
            if self.now() + (interval or self.cfg["poll_s"]) >= deadline:
                raise Abort("WAIT_TIMEOUT", what + (f" (last: {last})" if last else ""))
            self.clock.sleep(interval or self.cfg["poll_s"])

    def phase(self, name, fn, *args):
        entry = {"phase": name, "started": utc(), "t0_s": round(self.now() - self.started, 3)}
        self.phases.append(entry)
        try:
            result = fn(*args)
            entry["status"] = "DONE"
            return result
        except BaseException as error:
            entry["status"] = "FAILED:" + (getattr(error, "reason", None) or type(error).__name__)
            raise
        finally:
            entry["t1_s"] = round(self.now() - self.started, 3)

    # ------------------------------------------------------------- run
    @property
    def call_deadline(self):
        return self.final_deadline if self.cleaning else self.main_deadline

    def run(self):
        self.started = self.now()
        cap = self.plan["caps"]["total_s"]
        self.final_deadline = self.started + cap
        self.main_deadline = self.final_deadline - self.plan["phases_s"]["P7"]
        self.cleaning = False
        abort = None
        try:
            try:
                self.phase("P0", self.p0)
                self.phase("P1", self.p1)
                self.phase("P2", self.p2)
                self.phase("P3", self.trial, "B0-CTRL")
                if self.phase("P4", self.p4):
                    self.phase("P4-trial", self.trial, "B0-HPA")
                self.phase("P5", self.p5, "COMPLETED")
            except KeyboardInterrupt:
                abort = "INTERRUPTED"
            except DeadlineExceeded:
                abort = "TOTAL_CAP"
            except HarnessError as error:
                abort = error.reason + (f" ({error.detail})" if error.detail else "")
            except Exception as error:  # a host bug or I/O error (disk full) is an abort like any other
                abort = f"UNEXPECTED ({type(error).__name__}: {str(error)[:160]})"
            self.cleaning = True
            if abort:
                self.result["abort"] = abort
                self.salvage(abort)
        finally:
            # P7 runs whatever happened above, including an error in salvage itself.
            self.cleaning = True
            self.phase_safe("P7", self.p7)
        self.result["verdict"] = "COMPLETED" if not abort else "ABORTED"
        self.result["cleanup"] = "CLEAN" if all(s["status"] in ("DONE", "SKIPPED") for s in self.cleanup_log) else "INCOMPLETE"
        exports = (self.result.get("p5") or {}).get("exports") or {}
        if not (self.pulled and {"export-H", "export-O"} <= set(exports)):
            self.result["p8"] = {"skipped": "MAIN_EXPORTS_MISSING", "exports": sorted(exports)}  # nothing scored without both planes
        else:
            try:
                self.result["p8"] = score_and_register(self.out / "raw", self.out / "results", self.trials, self.evidence)
            except Exception as error:
                self.result["p8"] = {"error": type(error).__name__, "detail": str(error)[:300]}
        self.write_receipt()
        return self.result

    def phase_safe(self, name, fn):
        try:
            self.phase(name, fn)
        except BaseException as error:  # cleanup reports, never hides
            self.result.setdefault("errors", []).append(f"{name}:{getattr(error, 'reason', type(error).__name__)}")

    def salvage(self, reason):
        """End an open trial at (d), close the run and pull evidence, within the cleanup reserve."""
        if not self.agent_up:
            return
        # Two independent steps, each tried twice: a failed abort never prevents pulling the evidence.
        for name, step in (("abort", lambda: self.end_open_trial(reason)), ("export", lambda: self.pulled or self.p5("ABORTED"))):
            for _ in range(2):
                try:
                    step()
                    break
                except KeyboardInterrupt:
                    self.result.setdefault("errors", []).append(f"SALVAGE_{name.upper()}_INTERRUPTED")
                except Exception as error:
                    self.result.setdefault("errors", []).append(f"SALVAGE_{name.upper()}:{getattr(error, 'reason', type(error).__name__)}")
                    break

    def end_open_trial(self, reason):
        fault_ended = self.stop_fault()
        ended = self.agent({"action": "abort", "reason": reason, "fault_ended": fault_ended})["trial"]
        if ended and ended["name"] in self.trials:
            self.trials[ended["name"]]["summary"] = ended

    def stop_fault(self):
        """True when no fault is still acting (CTRL delete is instant; the load pod is deleted by uid)."""
        load = next((c for c in self.created if c["name"] == LOAD_POD), None)
        if load is None or self.evidence.get("load_finished"):
            return True
        try:
            uid = self.owned_uid(load, self.final_deadline)
            state = "ALREADY_ABSENT" if uid is None else \
                self.delete_exact("P4", "Pod", f"/api/v1/namespaces/{self.ns}/pods/{LOAD_POD}", LOAD_POD, uid, self.final_deadline)
            self.evidence["load_finished"] = state
            return state in ("DELETED", "ALREADY_ABSENT")
        except HarnessError:
            return False

    # ------------------------------------------------------------- P0
    def p0(self):
        d = self.deadline(self.plan["phases_s"]["P0"])
        k = self.kube
        reads = {}
        code, out, _ = k.run(["config", "get-contexts", CONTEXT, "-o", "name"], d)
        if code != 0 or out.decode().strip() != CONTEXT:
            raise Abort("WRONG_CONTEXT")
        version = json.loads(k.run(["version", "--client", "-o", "json"], d)[1])["clientVersion"]
        if (int(version["major"]), int("".join(c for c in version["minor"] if c.isdigit()))) < (1, 22):
            raise Abort("KUBECTL_TOO_OLD")  # delete --raw -f (uid preconditions)
        nodes = k.json(["get", "nodes"], d)["items"]
        reads["nodes"] = [{"name": n["metadata"]["name"], "ready": self.node_ready(n)} for n in nodes]
        if not nodes or not all(x["ready"] for x in reads["nodes"]):
            raise Abort("NODE_NOT_READY")
        images = {name for n in nodes for i in (n.get("status", {}).get("images") or []) for name in (i.get("names") or [])}
        reads["image_present"] = any(name.endswith(self.cfg["image"]) for name in images)
        if not reads["image_present"]:
            raise Abort("IMAGE_ABSENT", self.cfg["image"])
        target = {d_["metadata"]["name"]: d_ for d_ in k.json(["get", "deploy", "-n", "target-app"], d)["items"]}
        zd = {d_["metadata"]["name"]: d_ for d_ in k.json(["get", "deploy", "-n", "zero-door"], d)["items"]}
        if any(t not in target or not target[t]["spec"].get("replicas") for t in TARGETS):
            raise Abort("TARGET_MISSING")
        snap = lambda dep: {"uid": dep["metadata"]["uid"], "replicas": dep["spec"].get("replicas", 1),
                            "generation": dep["metadata"].get("generation"), "spec_sha256": spec_hash(dep),
                            "selector": selector(dep), "resourceVersion": dep["metadata"]["resourceVersion"]}
        self.baseline = {"target-app": {n: snap(dep) for n, dep in target.items()},
                         "zero-door": {n: snap(dep) for n, dep in zd.items() if n in ZD_COMPONENTS}}
        hpas = k.json(["get", "hpa", "-A"], d)["items"]
        foreign = [f"{h['metadata']['namespace']}/{h['metadata']['name']}" for h in hpas
                   if h["metadata"]["namespace"] == "target-app" and (h["spec"]["scaleTargetRef"]["name"] in TARGETS or h["metadata"]["name"] in HPAS)]
        reads["hpa_on_targets"] = foreign
        if foreign:
            raise Abort("FOREIGN_HPA", ",".join(foreign))
        api = k.json(["get", "apiservice", "v1beta1.metrics.k8s.io"], d, missing_ok=True)
        reads["metrics_api"] = bool(api) and any(c.get("type") == "Available" and c.get("status") == "True"
                                                 for c in api.get("status", {}).get("conditions", []))
        cms = [c["metadata"]["name"] for c in k.json(["get", "configmap", "-n", "zero-door"], d)["items"]]
        if PROFILES_CM in cms:
            raise Abort("PROFILES_CONFIGMAP_EXISTS")
        names = {n["metadata"]["name"] for n in k.json(["get", "namespaces"], d)["items"]}
        if self.ns in names:
            raise Abort("NAMESPACE_EXISTS")
        service = k.json(["get", "service", "frontend", "-n", "target-app"], d)
        ip, port = service["spec"]["clusterIP"], service["spec"]["ports"][0]["port"]
        self.origin = f"http://{ip}:{port}"
        can = {}
        for verb, resource in (("patch", "deployments/scale"), ("delete", "pods")):
            code, out, _ = k.run(["auth", "can-i", verb, resource, "-n", "target-app", "--as",
                                  "system:serviceaccount:zero-door:hephaestus-sa"], d)
            can[f"{verb} {resource}"] = out.decode().strip()
        reads["hephaestus_sa_can"] = can  # recorded only; B0's guarantee is 0 pods + no accepted O action
        self.preflight = dict(reads, baseline=self.baseline, origin=self.origin, kubectl_client=version.get("gitVersion"),
                              approval=self.approval, context=CONTEXT, namespace=self.ns, config_ref=self.config_ref)
        (self.out / "preflight.json").write_text(json.dumps(self.preflight, indent=1, sort_keys=True))

    @staticmethod
    def node_ready(node):
        return any(c.get("type") == "Ready" and c.get("status") == "True" for c in node.get("status", {}).get("conditions", []))

    # ------------------------------------------------------------- P1
    def p1(self):
        d = self.deadline(self.plan["phases_s"]["P1"])
        cfg = self.cfg
        self.create("P1", {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": self.ns}}, d)
        source = Path(__file__).read_bytes()
        self.create("P1", {"apiVersion": "v1", "kind": "ConfigMap", "metadata": {"name": HARNESS_CM, "namespace": self.ns},
                           "data": {"r1_baseline_runtime.py": source.decode()}}, d)
        # Before any target object is touched: prove on this cluster that a uid precondition is honoured.
        path = f"/api/v1/namespaces/{self.ns}/configmaps/{HARNESS_CM}"
        wrong = sha256(secrets.token_bytes(16))[:8] + "-0000-4000-8000-000000000000"
        state = self.delete_exact("P1", "ConfigMap", path, HARNESS_CM, wrong, d)
        still = self.kube.json(["get", "configmap", HARNESS_CM, "-n", self.ns], d, missing_ok=True)
        self.evidence["uid_precondition_selftest"] = {"state": state, "configmap_still_present": still is not None}
        if state != "UID_CHANGED_NOT_DELETED" or still is None:
            raise Abort("UID_PRECONDITION_SELFTEST_FAILED", state)
        self.create("P1", self.pod(AGENT_POD, ["python", "-B", f"{cfg['mount']}/r1_baseline_runtime.py", "agent",
                                               "--root", cfg["agent_root"], "--port", str(cfg["agent_port"])],
                                   self.plan["caps"]["total_s"]), d)
        self.wait("agent pod ready", lambda dl: ready(self.kube.json(["get", "pod", AGENT_POD, "-n", self.ns], dl)), cfg["pod_ready_s"])
        self.agent_up = True
        hello = self.wait("agent answers", lambda dl: self.agent({"action": "hello"}, allow_error=True), cfg["pod_ready_s"])
        if hello.get("module_sha256") != sha256(source):
            raise Abort("AGENT_SOURCE_MISMATCH")
        # Converted locally by kubectl (client dry run), so this code needs no YAML parser.
        code, out, err = self.kube.run(["create", "--dry-run=client", "-f", str(self.manifest), "-o", "json"], d)
        if code != 0:
            raise Abort("PROFILE_CONVERSION_FAILED", err.decode(errors="replace")[-200:])
        # kubectl emits a JSON stream for a multi-document YAML manifest, not necessarily one List.
        decoder, remaining, docs = json.JSONDecoder(), out.decode().strip(), []
        while remaining:
            doc, end = decoder.raw_decode(remaining)
            docs.extend(doc.get("items") or [doc])
            remaining = remaining[end:].lstrip()
        self.profile_docs = {i["metadata"]["name"]: i for i in docs}
        self.create("P1", copy.deepcopy(self.profile_docs[PROFILES_CM]), d)
        for name in ZD_COMPONENTS:
            base = self.baseline["zero-door"].get(name)
            if base and base["replicas"]:
                self.scale("P1", "zero-door", name, base["replicas"], 0, base["resourceVersion"], d)
                self.evidence.setdefault("zd_scaled", []).append(name)
        self.wait("gaia/hephaestus at 0 pods", lambda dl: self.zd_pods(dl) == 0, cfg["scale_wait_s"])
        trials = {n: {"warmup_s": t["warmup_s"], "baseline_s": t["baseline_s"]} for n, t in self.plan["trials"].items()}
        agent_cfg = {k: cfg[k] for k in ("probe", "product", "product_marker", "timeouts", "heartbeat_s", "grace_s", "provenance",
                                          "method_version", "watch_gap_s", "budgets")}
        agent_cfg.update(origin=self.origin, config_ref=self.config_ref, protocol_ref=self.protocol_ref,
                         schedule_ref="sha256:" + sha256(canonical(self.plan)),
                         plan={"f01": self.plan["f01"], "w_eff_s": self.plan["w_eff_s"], "stop_margin_s": self.plan["stop_margin_s"],
                               "trials": trials})
        self.run_info = self.agent({"action": "start_run", "config": agent_cfg})

    def pod(self, name, command, deadline_s):
        cfg = self.cfg
        return {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": name, "namespace": self.ns},
                "spec": {"nodeName": cfg["node"], "automountServiceAccountToken": False, "restartPolicy": "Never",
                         "activeDeadlineSeconds": int(deadline_s),
                         "securityContext": {"runAsNonRoot": True, "runAsUser": 65532, "runAsGroup": 65532,
                                             "seccompProfile": {"type": "RuntimeDefault"}},
                         "containers": [{"name": "main", "image": cfg["image"], "imagePullPolicy": "Never", "command": command,
                                         "env": [{"name": "PYTHONPATH", "value": "/app"}],
                                         "resources": {"requests": {"cpu": "100m", "memory": "128Mi"}, "limits": {"cpu": "500m", "memory": "256Mi"}},
                                         "securityContext": {"allowPrivilegeEscalation": False, "capabilities": {"drop": ["ALL"]}},
                                         "volumeMounts": [{"name": "harness", "mountPath": cfg["mount"], "readOnly": True},
                                                          {"name": "work", "mountPath": cfg["agent_root"]}]}],
                         "volumes": [{"name": "harness", "configMap": {"name": HARNESS_CM}}, {"name": "work", "emptyDir": {}}]}}

    def zd_pods(self, deadline):
        total = 0
        for name, base in self.baseline["zero-door"].items():
            pods = self.kube.json(["get", "pods", "-n", "zero-door", "-l", base["selector"]], deadline)["items"]
            total += sum(1 for p in pods if p.get("status", {}).get("phase") in ("Pending", "Running"))
        return total

    # ------------------------------------------------------------- P2
    def p2(self):
        d = self.deadline(self.plan["phases_s"]["P2"])
        pc = self.agent({"action": "positive_control"}).get("control") or {}
        self.evidence["positive_control"] = dict(pc)
        # Decided here from the recorded facts, not from the agent's own verdict or the call's success.
        if not control_passed(pc):
            raise Abort("POSITIVE_CONTROL_FAILED", json.dumps({k: pc.get(k) for k in CONTROL_FACTS}, sort_keys=True))
        spec = self.pod(CANARY, ["python", "-c", "import time; time.sleep(600)"], 600)["spec"]
        del spec["activeDeadlineSeconds"], spec["volumes"], spec["containers"][0]["volumeMounts"]
        spec["restartPolicy"] = "Always"
        canary = {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": CANARY, "namespace": self.ns},
                  "spec": {"replicas": 0, "selector": {"matchLabels": {"app": CANARY}},
                           "template": {"metadata": {"labels": {"app": CANARY}}, "spec": spec}}}
        self.create("P2", canary, d)
        get = lambda dl: self.kube.json(["get", "deploy", CANARY, "-n", self.ns], dl, managed_fields=True)
        scale_observations = []
        for current, target in ((0, 1), (1, 0)):
            dep = get(d)
            self.scale("P2", self.ns, CANARY, current, target, dep["metadata"]["resourceVersion"], d)
            self.wait(f"canary at {target}", lambda dl, t=target: (get(dl)["status"].get("readyReplicas") or 0) == t and
                      (t or not self.kube.json(["get", "pods", "-n", self.ns, "-l", f"app={CANARY}"], dl)["items"]), self.cfg["scale_wait_s"])
            observed = get(d)
            scale_observations.append({"replicas": observed["spec"]["replicas"], "uid": observed["metadata"]["uid"],
                                       "resourceVersion": observed["metadata"]["resourceVersion"], "replica_managers": replica_managers(observed)})
        # On k3s, scaling back to zero can remove field ownership. Preserve evidence at each scale step.
        managers = [m for observation in scale_observations for m in observation["replica_managers"]]
        events = self.kube.json(["get", "events", "-n", self.ns], d)["items"]
        sources = sorted({event_source(e) for e in events if e.get("reason") in ("SuccessfulCreate", "ScalingReplicaSet")} - {None})
        attribution = {"replica_managers": managers, "event_sources": sources, "scale_observations": scale_observations}
        self.evidence["positive_control"]["scale_attribution"] = attribution
        names = {str(m["manager"]) for m in managers}
        # spec.replicas must now be owned through the scale subresource by kubectl scale (no --field-manager flag:
        # the manager comes from the user agent, kubectl or kubectl.exe), not merely by kubectl-create.
        by_scale = {str(m["manager"]) for m in managers if m.get("subresource") == "scale"}
        if not by_scale or not all(n.startswith("kubectl") for n in by_scale) or "horizontal-pod-autoscaler" in names \
                or "replicaset-controller" not in sources:
            raise Abort("ATTRIBUTION_CONTROL_FAILED")

    # ------------------------------------------------------------- P3 / P4 trials
    def watch(self, deadline, hpa=False):
        """One B0 absence read set, sent to the agent and stamped there; a failed read is a failed tick."""
        tick = {"ok": True, "errors": []}
        try:
            tick["zd_pods"] = self.zd_pods(deadline)
            nodes = self.kube.json(["get", "nodes"], deadline)["items"]
            tick["nodes_ready"] = all(self.node_ready(n) for n in nodes)
            if hpa:
                h = self.kube.json(["get", "hpa", HPAS[0], "-n", "target-app"], deadline)
                dep = self.kube.json(["get", "deploy", "frontend", "-n", "target-app"], deadline, managed_fields=True)
                tick["hpa"] = {"desired": h["status"].get("desiredReplicas"), "current": h["status"].get("currentReplicas"),
                               "frontend_replicas": dep["spec"].get("replicas"), "managers": replica_managers(dep)}
        except DeadlineExceeded:
            raise
        except HarnessError as error:
            tick.update(ok=False, errors=[error.reason])
            return tick
        tick["ok"] = tick["zd_pods"] == 0 and tick["nodes_ready"]
        return tick

    def trial(self, name):
        cfg, t = self.cfg, self.plan["trials"][name]
        budget = cfg["budgets"][name]
        info = self.agent({"action": "start_trial", "name": name})
        started = self.now()
        record = {"trial_id": info["trial_id"], "ticks": [], "fault": None}
        self.trials[name] = record
        hard_end = started + budget["max_duration_s"] + cfg["grace_s"] + cfg["timeouts"]["transaction_s"] + 10
        ready_by = started + t["warmup_s"] + t["baseline_s"] + cfg["baseline_grace_s"]
        hpa = name == "B0-HPA"
        while True:
            if self.now() >= self.main_deadline:
                raise DeadlineExceeded("DEADLINE", name)
            if self.now() > hard_end:
                raise Abort("TRIAL_OVERRUN", name)
            tick = self.watch(self.main_deadline, hpa)
            record["ticks"].append({"t_s": round(self.now() - self.started, 3), **tick})
            status = self.agent({"action": "status", "watch": tick})
            st = status["trial"]
            if status["failure"]:
                raise Abort("PERSISTENCE", status["failure"])
            if status["o_actions"]:
                raise Abort("O_ACTION_ACCEPTED")
            if tick["ok"] is False and tick.get("zd_pods"):
                raise Abort("ZERO_DOOR_COMPONENT_RUNNING")
            if tick.get("nodes_ready") is False:
                raise Abort("NODE_NOT_READY")
            if st["undelivered_s"] is not None and st["undelivered_s"] > cfg["ack_stall_s"]:
                raise Abort("H_ACK_STALL", name)
            if st["phase"] == "READY_FOR_FAULT" and record["fault"] is None:
                record["fault"] = self.fault(name)
            elif st["phase"] == "BASELINE" and self.now() > ready_by:
                raise Abort("BASELINE_UNHEALTHY", name)
            if hpa and record["fault"] and not record["fault"].get("stopped"):
                self.check_load(name, record["fault"])
            if st["phase"] == "STOPPED":
                break
            self.clock.sleep(cfg["poll_s"])
        if record["fault"] and not record["fault"].get("stopped"):
            confirmed = self.stop_fault()
            self.agent({"action": "attack_stopped", "name": name, "stop_reason": "HORIZON", "executor_confirmed": confirmed})
            record["fault"]["stopped"] = "HORIZON"
        summary = self.agent({"action": "end_trial", "name": name, "watch": self.watch(self.main_deadline, hpa)})
        record["summary"] = {k: v for k, v in summary.items() if k != "ok"}
        self.collect_events(name)
        if summary["stop_point"] == "d":
            raise Abort("TRIAL_INCOMPLETE", f"{name}: {summary['stop_reason']}")

    def fault(self, name):
        d = self.main_deadline
        if name == "B0-CTRL":
            if self.deletes["frontend_pod"] >= self.plan["caps"]["frontend_pod_deletes"]:
                raise Abort("POD_DELETE_CAP")
            listed = self.kube.json(["get", "pods", "-n", "target-app", "-l", self.baseline["target-app"]["frontend"]["selector"]], d)["items"]
            pods = [p for p in listed if ready(p)]
            if not pods:
                raise Abort("NO_READY_FRONTEND_POD")
            pod = sorted(pods, key=lambda p: p["metadata"]["name"])[0]
            meta = pod["metadata"]
            path = f"/api/v1/namespaces/target-app/pods/{meta['name']}"
            answer = self.agent({"action": "attack_requested", "name": name, "variant_ref": "rt1-b0-ctrl-frontend-pod-delete",
                                 "fault_params": {"pods": 1, "uid_precondition": True}, "target_services": ["frontend"],
                                 "attack_command": f"kubectl delete --raw {path} (preconditions.uid)"}, allow_error=True)
            if not answer.get("ok"):
                return self.not_ready(answer)
            self.deletes["frontend_pod"] += 1
            state = self.delete_exact("P3", "Pod", path, meta["name"], meta["uid"], d)
            evidence = {"deleted_pod": meta["name"], "deleted_uid": meta["uid"], "delete": state,
                        "owner": [o.get("kind") + "/" + o.get("name") for o in meta.get("ownerReferences", [])],
                        "owner_uids": [o.get("uid") for o in meta.get("ownerReferences", []) if o.get("kind") == "ReplicaSet"],
                        "pods_before": [p["metadata"]["uid"] for p in listed]}  # Ready or not: none of them is a replacement
            self.agent({"action": "attack_stopped", "name": name, "stop_reason": "EXECUTOR_ENDED",
                        "executor_confirmed": state == "DELETED", "evidence": evidence})
            return dict(evidence, t_req=answer["t_req"], stopped="EXECUTOR_ENDED")
        load = self.plan["load"]
        load_s = self.plan["trials"][name]["load_s"]
        max_requests = self.plan["caps"]["load_requests"]
        # Replicas at T_req, read just before it: an HPA claim needs a scale-up above this, by this trial's HPA object.
        before = self.kube.json(["get", "deploy", "frontend", "-n", "target-app"], d)["spec"].get("replicas")
        hpa = next((c for c in self.created if c["name"] == HPAS[0]), {})
        answer = self.agent({"action": "attack_requested", "name": name, "variant_ref": "rt1-b0-hpa-http-load",
                             "fault_params": {"rps": load["rps"], "connections": load["connections"], "duration_s": load_s,
                                              "max_requests": max_requests}, "target_services": ["frontend"],
                             "attack_command": f"pod {LOAD_POD}: GET / at {load['rps']} req/s, {load['connections']} connections, {load_s} s"},
                            allow_error=True)
        if not answer.get("ok"):
            return self.not_ready(answer)
        pod = self.pod(LOAD_POD, ["python", "-B", f"{self.cfg['mount']}/r1_baseline_runtime.py", "load", "--origin", self.origin,
                                  "--rps", str(load["rps"]), "--connections", str(load["connections"]), "--duration", str(load_s),
                                  "--max-requests", str(max_requests)], load_s + self.cfg["load_grace_s"])
        pod["spec"]["volumes"] = [pod["spec"]["volumes"][0]]
        pod["spec"]["containers"][0]["volumeMounts"] = [pod["spec"]["containers"][0]["volumeMounts"][0]]
        made = self.create("P4", pod, d)
        return {"t_req": answer["t_req"], "load_uid": made["metadata"]["uid"], "load_started_s": self.now(), "load_s": load_s,
                "frontend_replicas_before": before, "hpa_uid": hpa.get("uid")}

    @staticmethod
    def not_ready(answer):
        """The baseline turned unhealthy between status and request: no fault, try again next tick."""
        if answer.get("error") in ("CONTROL_NOT_DURABLE", "AGENT_FAILED"):
            raise Abort("PERSISTENCE", answer["error"] + (f": {answer['detail']}" if answer.get("detail") else ""))
        if answer.get("error") != "NOT_READY_FOR_FAULT":
            raise HarnessError("AGENT_" + str(answer.get("error")), answer.get("detail"))
        return None

    def check_load(self, name, fault):
        pod = self.kube.json(["get", "pod", LOAD_POD, "-n", self.ns], self.main_deadline, missing_ok=True)
        phase = (pod or {}).get("status", {}).get("phase")
        over = self.now() - fault["load_started_s"] > fault["load_s"] + self.cfg["load_grace_s"]
        if phase in ("Succeeded", "Failed") or over:
            if phase not in ("Succeeded", "Failed"):
                confirmed = self.stop_fault()
                reason = "HORIZON"
            else:
                self.evidence["load_finished"] = phase
                confirmed = phase == "Succeeded"
                reason = "EXECUTOR_ENDED"
                code, out, _ = self.kube.run(["logs", "-n", self.ns, LOAD_POD], self.main_deadline)
                fault["load_result"] = out.decode(errors="replace")[-500:] if code == 0 else None
            self.agent({"action": "attack_stopped", "name": name, "stop_reason": reason, "executor_confirmed": confirmed,
                        "evidence": {"load_pod_phase": phase}})
            fault["stopped"] = reason

    def collect_events(self, name):
        """Events and pods after the trial, with the identities interpret() matches them against: events are
        kept with their object's uid, so an older object of the same name (an earlier run) never counts."""
        fault = self.trials[name].get("fault") or {}
        identity = {"t_req": fault.get("t_req")}
        if name == "B0-CTRL":
            identity.update({k: fault.get(k) for k in ("deleted_uid", "owner_uids", "pods_before")})
        else:
            identity.update({k: fault.get(k) for k in ("hpa_uid", "frontend_replicas_before")})
        try:
            events = self.kube.json(["get", "events", "-n", "target-app"], self.main_deadline)["items"]
            pods = self.kube.json(["get", "pods", "-n", "target-app", "-l", self.baseline["target-app"]["frontend"]["selector"]],
                                  self.main_deadline)["items"]
        except HarnessError as error:
            self.evidence["trials"][name] = {"events_error": error.reason, "identity": identity}
            return
        keep = []
        for e in events:
            obj = e.get("involvedObject", {})
            if obj.get("name", "").startswith(("frontend", "cartservice")) and e.get("reason") in (
                    "SuccessfulCreate", "SuccessfulDelete", "SuccessfulRescale", "Killing", "Scheduled", "Started", "ScalingReplicaSet"):
                keep.append({"reason": e["reason"], "object": f"{obj.get('kind')}/{obj.get('name')}", "object_uid": obj.get("uid"),
                             "source": event_source(e), "t_ms": event_time(e), "message": (e.get("message") or "")[:200]})
        self.evidence["trials"][name] = {"events": keep, "identity": identity, "frontend_pods_after": [
            {"name": p["metadata"]["name"], "uid": p["metadata"]["uid"], "ready": ready(p),
             "owner": [{"kind": o.get("kind"), "uid": o.get("uid")} for o in p["metadata"].get("ownerReferences", [])]} for p in pods]}

    def p4(self):
        d = self.deadline(self.plan["phases_s"]["P4_hpa_ready"])
        if not self.preflight["metrics_api"]:
            self.evidence["hpa"] = "HPA_NOT_MEASURABLE: metrics API not Available at P0"
            return False
        for name in HPAS:
            self.create("P4", copy.deepcopy(self.profile_docs[name]), d)
        def measured(dl):
            h = self.kube.json(["get", "hpa", HPAS[0], "-n", "target-app"], dl)
            return any((m.get("resource") or {}).get("current", {}).get("averageUtilization") is not None
                       for m in h.get("status", {}).get("currentMetrics") or [])
        try:
            self.wait("HPA currentMetrics", measured, self.plan["phases_s"]["P4_hpa_ready"])
        except Abort:
            self.evidence["hpa"] = "HPA_NOT_MEASURABLE: no currentMetrics within the wait"
            return False
        self.evidence["hpa"] = "MEASURABLE"
        return True

    # ------------------------------------------------------------- P5
    def p5(self, close_reason):
        if "p5" not in self.result:  # the run is closed once; a failed pull (host disk, kubectl) is retried on its own
            self.result["p5"] = self.agent({"action": "close", "close_reason": close_reason}, timeout=self.cfg["export_tar_s"])
        code, out, err = self.kube.run(["exec", "-n", self.ns, AGENT_POD, "--", "tar", "-C", self.cfg["agent_root"] + "/out", "-cf", "-", "."],
                                       self.call_deadline, timeout_s=self.cfg["export_tar_s"])
        if code != 0:
            raise HarnessError("EXPORT_PULL_FAILED", err.decode(errors="replace")[-200:])
        partial = self.out / f"raw.partial-{len(self.kube.calls)}"
        extract(out, partial)
        partial.rename(self.out / "raw")
        self.pulled = True

    # ------------------------------------------------------------- P7
    def p7(self):
        d = self.final_deadline
        steps = [("pull evidence", self.cleanup_pull), ("delete HPAs", self.cleanup_hpas),
                 ("restore target replicas", lambda dl: self.restore("target-app", TARGETS, dl)),
                 ("restore gaia/hephaestus replicas", lambda dl: self.restore("zero-door", ZD_COMPONENTS, dl)),
                 ("delete profiles ConfigMap", self.cleanup_profiles), ("delete namespace", self.cleanup_namespace),
                 ("final diff against P0", self.final_diff)]
        for name, fn in steps:
            entry = {"step": name}
            # Each step is tried on its own: a failed step (API, host disk, a bug) never skips the next ones.
            for attempt in (1, 2):  # steps are idempotent (uid preconditions); one retry after an interrupt
                try:
                    entry.update(status="DONE", detail=fn(d), attempts=attempt)
                    break
                except KeyboardInterrupt:
                    entry.update(status="INTERRUPTED", attempts=attempt)
                except Exception as error:
                    detail = error.detail if isinstance(error, HarnessError) else str(error)[:200]
                    entry.update(status="FAILED", detail=getattr(error, "reason", type(error).__name__) + ": " + str(detail or ""),
                                 attempts=attempt)
                    break
            if entry.get("detail") == "SKIPPED":
                entry["status"] = "SKIPPED"
            self.cleanup_log.append(entry)

    def cleanup_pull(self, d):
        if self.pulled or not self.agent_up:
            return "SKIPPED"
        self.salvage("CLEANUP")
        if not self.pulled:
            raise HarnessError("EVIDENCE_NOT_PULLED", ", ".join(e for e in self.result.get("errors", []) if e.startswith("SALVAGE")))
        return "PULLED"

    def cleanup_hpas(self, d):
        out = {}
        for c in [c for c in self.created if c["kind"] == "HorizontalPodAutoscaler"]:  # each HPA on its own
            try:
                out[c["name"]] = self.delete_owned(c, f"/apis/autoscaling/v2/namespaces/target-app/horizontalpodautoscalers/{c['name']}", d)
            except KeyboardInterrupt:
                raise
            except Exception as error:
                out[c["name"]] = "FAILED " + str(getattr(error, "reason", type(error).__name__))
        if any(v not in ("DELETED", "ALREADY_ABSENT") for v in out.values()):
            raise HarnessError("HPA_NOT_REMOVED", json.dumps(out, sort_keys=True))
        return out or "SKIPPED"

    def restore(self, ns, names, d):
        """Back to the P0 replicas only for the same object (uid) with the same spec; otherwise leave it and say so."""
        out = {}
        for name in names:  # one deployment failing does not stop the next one
            base = (getattr(self, "baseline", None) or {}).get(ns, {}).get(name)
            if not base:
                continue
            try:
                dep = self.kube.json(["get", "deploy", name, "-n", ns], d, missing_ok=True)
                if dep is None:
                    out[name] = "ABSENT_NOT_RECREATED"
                elif dep["metadata"]["uid"] != base["uid"]:
                    out[name] = "REFUSED_UID_CHANGED"
                elif spec_hash(dep) != base["spec_sha256"]:
                    out[name] = "REFUSED_SPEC_CHANGED"
                elif dep["spec"].get("replicas") == base["replicas"]:
                    out[name] = "UNCHANGED"
                else:
                    self.scale("P7", ns, name, dep["spec"]["replicas"], base["replicas"], dep["metadata"]["resourceVersion"], d)
                    out[name] = f"CLEANUP_SCALED {dep['spec']['replicas']}->{base['replicas']}"
            except KeyboardInterrupt:
                raise
            except Exception as error:
                out[name] = "FAILED " + str(getattr(error, "reason", type(error).__name__))
        if any(v.startswith(("REFUSED", "ABSENT", "FAILED")) for v in out.values()):
            raise HarnessError("RESTORE_REFUSED", json.dumps(out, sort_keys=True))
        return out

    def cleanup_profiles(self, d):
        c = next((c for c in self.created if c["name"] == PROFILES_CM), None)
        if not c:
            return "SKIPPED"
        state = self.delete_owned(c, f"/api/v1/namespaces/zero-door/configmaps/{PROFILES_CM}", d)
        if state not in ("DELETED", "ALREADY_ABSENT"):
            raise HarnessError("PROFILES_NOT_REMOVED", state)
        return state

    def cleanup_namespace(self, d):
        c = next((c for c in self.created if c["kind"] == "Namespace"), None)
        if not c:
            return "SKIPPED"
        state = self.delete_owned(c, f"/api/v1/namespaces/{self.ns}", d)
        self.agent_up = False
        if state not in ("DELETED", "ALREADY_ABSENT"):
            raise HarnessError("NAMESPACE_NOT_REMOVED", state)
        limit = min(d, self.now() + self.cfg["namespace_gone_s"])
        while self.kube.json(["get", "namespace", self.ns], limit, missing_ok=True) is not None:
            if self.now() + self.cfg["poll_s"] >= limit:
                raise HarnessError("NAMESPACE_STILL_PRESENT")
            self.clock.sleep(self.cfg["poll_s"])
        return state + ", read back absent"

    def final_diff(self, d):
        if not getattr(self, "baseline", None):
            return "SKIPPED"
        diff = {}
        for ns, base in self.baseline.items():
            now = {x["metadata"]["name"]: x for x in self.kube.json(["get", "deploy", "-n", ns], d)["items"]}
            for name, b in base.items():
                x = now.get(name)
                if x is None:
                    diff[f"{ns}/{name}"] = "ABSENT"
                elif x["metadata"]["uid"] != b["uid"]:
                    diff[f"{ns}/{name}"] = "UID_CHANGED"
                elif spec_hash(x) != b["spec_sha256"]:
                    diff[f"{ns}/{name}"] = "SPEC_CHANGED"
                elif x["spec"].get("replicas") != b["replicas"]:
                    diff[f"{ns}/{name}"] = f"REPLICAS {x['spec'].get('replicas')} != {b['replicas']}"
        hpas = [h["metadata"]["name"] for h in self.kube.json(["get", "hpa", "-n", "target-app"], d)["items"] if h["metadata"]["name"] in HPAS]
        cms = [c["metadata"]["name"] for c in self.kube.json(["get", "configmap", "-n", "zero-door"], d)["items"] if c["metadata"]["name"] == PROFILES_CM]
        namespace_left = self.kube.json(["get", "namespace", self.ns], d, missing_ok=True) is not None  # absent at P0
        self.result["final_diff"] = {"deployments": diff, "hpas_left": hpas, "profiles_left": cms, "namespace_left": namespace_left}
        if diff or hpas or cms or namespace_left:
            raise HarnessError("STATE_DIFFERS_FROM_P0", json.dumps(self.result["final_diff"], sort_keys=True))
        return "MATCHES_P0"

    def write_receipt(self):
        receipt = {"package": "H-RT1 / G-ZER11-RT1", "approval": self.approval, "context": CONTEXT, "namespace": self.ns,
                   "nonce": self.nonce, "module_sha256": module_sha256(), "config_ref": self.config_ref, "image": self.cfg["image"],
                   "image_id": self.cfg["image_id"], "elapsed_s": round(self.now() - self.started, 3),
                   "cap_s": self.plan["caps"]["total_s"], "phases": self.phases, "writes": self.writes, "created": self.created,
                   "reads": len(self.kube.calls) - len(self.writes), "pod_deletes": self.deletes, "trials": self.trials,
                   "cleanup_steps": self.cleanup_log, **self.result}
        # Best effort and last: a host that cannot write files gets the result back from run() instead.
        for name, value in (("receipt.json", receipt), ("cluster-evidence.json", self.evidence), ("kubectl-calls.json", self.kube.calls)):
            try:
                (self.out / name).write_text(json.dumps(value, indent=1, sort_keys=True, default=str))
            except Exception as error:
                self.result.setdefault("errors", []).append(f"RECEIPT_NOT_WRITTEN:{name}:{type(error).__name__}")


def extract(data, destination):
    """Unpack the agent's tar: regular files and directories only, no absolute or parent paths, no links."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            name = Path(member.name)
            if name.is_absolute() or ".." in name.parts:
                raise HarnessError("UNSAFE_TAR_MEMBER", member.name)
            target = destination / name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
            else:
                raise HarnessError("UNSAFE_TAR_MEMBER", member.name)


# =========================================================================== P8 (offline)
def score_and_register(raw, root, trials=None, evidence=None):
    """Recompute with the ZER-10 CLI, register for serve-results, then read each trial against the cluster evidence."""
    raw, root = Path(raw), Path(root)
    repo = Path(__file__).resolve().parents[2]
    receipt = json.loads((raw / "agent-receipt.json").read_text())
    run_id = receipt["run"]["run_id"]
    directory = f"rt1-{run_id[4:16]}"
    root.mkdir(parents=True, exist_ok=True)
    others = []
    for prefix in ("pc-export-H", "pc-export-O"):
        if (raw / prefix).exists():
            others += ["--other-export", str(raw / prefix)]
    argv = [sys.executable, "-B", "-m", "measurement", "score", "--h-export", str(raw / "export-H"), "--o-export", str(raw / "export-O"),
            "--output", str(root / directory), "--required-flow", "checkout", *others]
    done = subprocess.run(argv, cwd=repo / "agent-orchestrator", capture_output=True, text=True, timeout=300)  # nosec B603
    if done.returncode != 0:
        return {"score_exit": done.returncode, "stderr": done.stderr[-500:]}
    sys.path.insert(0, str(repo / "agent-orchestrator"))
    from nemesis.measurement_view import register
    entry = register(root, directory)
    document = json.loads((root / directory / "score.json").read_text())
    pc = None
    if (raw / "pc-export-H").exists():
        pc_dir = root.parent / "positive-control-score"
        pc_done = subprocess.run([sys.executable, "-B", "-m", "measurement", "score", "--h-export", str(raw / "pc-export-H"),
                                  "--o-export", str(raw / "pc-export-O"), "--output", str(pc_dir)],
                                 cwd=repo / "agent-orchestrator", capture_output=True, text=True, timeout=300)  # nosec B603
        if pc_done.returncode == 0:
            run = json.loads((pc_dir / "score.json").read_text())["runs"][0]
            pc = {"quarantined_mode_violations": len(run["findings"]["quarantined_mode_violations"]),
                  "mode_findings": run["mode_findings"]}
    verdicts = interpret(document["runs"][0], receipt, evidence or {})
    return {"registered": entry, "directory": directory, "verdicts": verdicts, "positive_control_score": pc,
            "serve": f"verify-dashboard-baselines.sh serve-results --root {root.resolve()} --reader-key-file <new results-reader key file> --receipt <new file>"}


def stamp_ms(text):
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp() * 1000
    except (AttributeError, ValueError):
        return None


def controller_replacement(ev, t_rec):
    """A new Ready pod (uid not there before the delete) owned by the deleted pod's ReplicaSet (same uid), and
    that ReplicaSet's own SuccessfulCreate event naming it, within this trial and before recovery.
    Core Event times are floored to seconds: allow that at T_req, but require a full second before T_rec."""
    ident = ev["identity"]
    t_req = stamp_ms(ident.get("t_req"))
    if t_req is None or t_rec is None:
        return False
    owners, before = set(ident.get("owner_uids") or []) - {None}, set(ident.get("pods_before") or [])
    new = [p for p in ev.get("frontend_pods_after", []) if p.get("ready") and p.get("uid") not in before
           and owners & {o.get("uid") for o in p.get("owner", []) if isinstance(o, dict)}]
    return any(e["reason"] == "SuccessfulCreate" and e["source"] == "replicaset-controller" and e.get("object_uid") in owners
               and e.get("t_ms") is not None and t_req - 1000 < e["t_ms"] and e["t_ms"] + 1000 < t_rec
               and any(p["name"] in (e.get("message") or "") for p in new) for e in ev.get("events", []))


def hpa_scale_ups(ev):
    """SuccessfulRescale events of this trial's HPA object (uid) by the HPA controller, not before T_req, to more
    replicas than the deployment had at T_req. Core events carry second-resolution times (floored), so "not
    before" allows that one second; a scale-up earlier than it is not this trial's."""
    ident = ev["identity"]
    uid, before, t_req = ident.get("hpa_uid"), ident.get("frontend_replicas_before"), stamp_ms(ident.get("t_req"))
    if not uid or before is None or t_req is None:
        return []
    out = []
    for e in ev.get("events", []):
        size = re.search(r"New size: (\d+)", e.get("message") or "")
        if e["reason"] == "SuccessfulRescale" and e.get("object_uid") == uid and e["source"] == "horizontal-pod-autoscaler" \
                and size and int(size.group(1)) > before and e["t_ms"] is not None and e["t_ms"] > t_req - 1000:
            out.append(e)
    return out


def interpret(run, agent_receipt, evidence):
    """Per trial: the scorer label plus what the cluster evidence allows to be claimed (runbook 5.8)."""
    out = {}
    incidents = {i["trial_id"]: i for i in run["incidents"]}
    for name, trial in agent_receipt["trials"].items():
        if trial is None:
            continue
        inc = incidents.get(trial["trial_id"])
        label = inc["label"] if inc else "NO_INCIDENT"
        audit = (trial.get("audit_coverage") or {}).get("complete") is True
        ev = (evidence.get("trials") or {}).get(name, {})
        known = "identity" in ev and "events_error" not in ev  # without them nothing is claimed about the cluster
        events = ev.get("events", []) if known else []
        claim = "INCOMPLETE:" + label
        if label == "CONFIRMED_NO_EFFECT":
            claim = "NO_EFFECT"
        elif label == "TIMEOUT":
            claim = "NOT_RECOVERED_WITHIN_CAP"
        elif label == "RECOVERED_UNDETECTED" and not audit:
            claim = "RECOVERED_BUT_ABSENCE_AUDIT_INCOMPLETE"
        elif label == "RECOVERED_UNDETECTED" and name == "B0-CTRL":
            t_rec = (inc["milestones"].get("t_rec") or {}).get("t_ms")
            claim = "CONTROLLER_RECOVERY_OBSERVED" if known and controller_replacement(ev, t_rec) else "RECOVERED_CONTROLLER_EVIDENCE_MISSING"
        elif label == "RECOVERED_UNDETECTED" and not known:
            claim = "RECOVERED_HPA_EVIDENCE_MISSING"
        elif label == "RECOVERED_UNDETECTED":
            t_rec = (inc["milestones"].get("t_rec") or {}).get("t_ms")
            t_stop = (inc["milestones"].get("t_stop") or {}).get("t_ms")
            named = [e for e in events if e["reason"] == "SuccessfulRescale" and e["object"] == "HorizontalPodAutoscaler/" + HPAS[0]]
            ups = hpa_scale_ups(ev)
            if ups and t_rec is not None and min(e["t_ms"] for e in ups) + 1000 < t_rec:
                claim = "HPA_RECOVERY_OBSERVED"
            elif ups:
                claim = "RESCALE_ORDER_AMBIGUOUS_OR_AFTER_RECOVERY"
            elif any(e.get("object_uid") == ev["identity"].get("hpa_uid") and e["source"] != "horizontal-pod-autoscaler" for e in named):
                claim = "RESCALE_NOT_BY_HPA"
            elif named:  # another object's, older, downscale-only or undated events: not this trial's scale-up
                claim = "HPA_RESCALE_EVIDENCE_MISSING_OR_AMBIGUOUS"
            else:
                claim = "RECOVERED_AFTER_LOAD_STOP_NOT_HPA" if t_stop is not None and t_rec is not None and t_rec >= t_stop else "RECOVERED_WITHOUT_HPA_RESCALE"
        if name == "B0-HPA" and label == "CONFIRMED_NO_EFFECT" and known and not hpa_scale_ups(ev):
            claim = "HPA_NOT_ACTIVATED_NO_EFFECT"
        out[name] = {"label": label, "claim": claim, "absence_audit_complete": audit, "stop_point": trial["stop_point"]}
    return out


# =========================================================================== pod CLI
def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="r1_baseline_runtime.py", description="pod side of H-RT1 (agent, call, load)")
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("agent")
    a.add_argument("--root", required=True)
    a.add_argument("--port", type=int, default=EXEC["agent_port"])
    c = sub.add_parser("call")
    c.add_argument("json")
    c.add_argument("--port", type=int, default=EXEC["agent_port"])
    load = sub.add_parser("load")
    load.add_argument("--origin", required=True)
    load.add_argument("--rps", type=float, required=True)
    load.add_argument("--connections", type=int, required=True)
    load.add_argument("--duration", type=float, required=True)
    load.add_argument("--max-requests", type=int, required=True)
    args = parser.parse_args(argv)
    if args.command == "agent":
        serve_agent(args.root, args.port)
        return 0
    if args.command == "call":
        return call_agent(args.port, args.json)
    return run_load(args.origin, args.rps, args.connections, args.duration, args.max_requests)


if __name__ == "__main__":
    sys.exit(main())
