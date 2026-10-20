"""Bounded R1 acceptance harness, run only in the approved temporary lab pod.

Real Online Boutique and a file-backed SQLite CRUD fixture. No fake transport, healer,
LLM, SQL injection or load generator. The SQLite fixture is a ZER-10 prerequisite slice,
not completion of ZER-41's attack scenario. Tokens and session cookies are never exported.
"""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import sqlite3
import sys
import threading
import time
from urllib.request import Request, urlopen
import uuid

from event_pipeline.contract import Producer, canonical, new_id
from event_pipeline.gateway import Gateway, server
from event_pipeline.store import Archive
from measurement.clock import ProbeClock, stamp
from measurement.config import plan as validate_plan
from measurement.flows import Flow, Memory, boutique_spec, fixture_spec, request
from measurement.probe import ProbeRunner
from measurement.sink import HttpHSink, Journal, Outbox, Publisher

ROOT = Path("/tmp/zer10")
DB = ROOT / "fixture.sqlite"
PORT = 9133
PRODUCT = "OLJCESPC7Z"
FORM = {"email": "probe@example.invalid", "street_address": "1 Lab Road", "zip_code": "10000", "city": "Local",
        "state": "LC", "country": "Lab", "credit_card_number": "4432801561520454",
        "credit_card_expiration_month": "1", "credit_card_expiration_year": "2030", "credit_card_cvv": "672"}
F01 = {"delta_s": 1, "k": 3, "s_s": 2, "l_ms": 2000, "gap_s": 2, "eps_s": 1, "cap_det_s": 30, "cap_rec_s": 30}


class Fixture(BaseHTTPRequestHandler):
    """Actual HTTP -> SQLite transaction -> separate-connection read, then owned cleanup."""
    def log_message(self, *_args):
        pass

    def reply(self, code, value):
        raw = canonical(value)
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def handle_api(self):
        if self.command == "GET" and self.path == "/health":
            return self.reply(200, {"http_process": "UP"})  # process health does not prove a working DB
        ref = self.path.rsplit("/", 1)[-1]
        try:
            with sqlite3.connect(DB, timeout=0.1) as db:
                db.row_factory = sqlite3.Row
                if self.command == "POST" and self.path == "/fixture/orders":
                    size = int(self.headers.get("Content-Length", 0))
                    if not 0 < size < 4096:
                        return self.reply(400, {"error": "size"})
                    value = json.loads(self.rfile.read(size))
                    ref = uuid.uuid4().hex
                    db.execute("INSERT INTO orders VALUES (?, ?, ?, ?)", (ref, value["item"], value["note"], "STORED"))
                    db.commit()
                    row = db.execute("SELECT * FROM orders WHERE order_ref = ?", (ref,)).fetchone()
                    return self.reply(201, dict(row))
                if not self.path.startswith("/fixture/orders/"):
                    return self.reply(404, {})
                if self.command == "DELETE":
                    db.execute("DELETE FROM orders WHERE order_ref = ?", (ref,))
                    db.commit()
                    return self.reply(204, {})
                row = db.execute("SELECT * FROM orders WHERE order_ref = ?", (ref,)).fetchone()
                return self.reply(200 if row else 404, dict(row) if row else {})
        except sqlite3.OperationalError as error:
            return self.reply(503, {"error": type(error).__name__})  # real lock contention, no scripted response

    do_POST = do_GET = do_DELETE = handle_api


class Acceptance:
    def __init__(self):
        ROOT.mkdir(exist_ok=False)
        self.started = time.monotonic()
        with sqlite3.connect(DB) as db:
            db.execute("CREATE TABLE orders (order_ref TEXT PRIMARY KEY, item TEXT, note TEXT, status TEXT)")
        self.clock = ProbeClock("clk-acceptance", "HOST_SHARED")
        self.harness = Producer("harness", "zer10-runtime-01", self.clock.envelope())
        self.context = {"run_id": new_id("run"), "trial_id": None, "group": "B0",
                        "method_version": "acceptance-only-not-benchmark",
                        "config_ref": "sha256:" + hashlib.sha256(Path("/app/live/source-manifest.json").read_bytes()).hexdigest()}
        self.archive = Archive(ROOT / "archive", "H")
        self.keys = {role: secrets.token_hex(32) for role in ("harness", "probe", "evaluator")}
        gateway = Gateway(self.archive, self.keys)
        self.h_http = server(gateway, ("127.0.0.1", 9131))
        self.fixture_http = ThreadingHTTPServer(("127.0.0.1", 9132), Fixture)
        for http in (self.h_http, self.fixture_http):
            threading.Thread(target=http.serve_forever, daemon=True).start()
        self.control_sink = HttpHSink("http://127.0.0.1:9131", self.keys["harness"])
        self.control("RUN_STARTED", {"canary_token": "acceptance-" + uuid.uuid4().hex,
                     "protocol_ref": "ZER-10/runtime-01; real service acceptance only, not research dataset",
                     "schedule_ref": "approved-fixed-phase-order", "f01_params": F01,
                     "reference_clock_id": self.clock.clock_id})
        self.results, self.transactions = {}, {"checkout": 0, "fixture": 0}
        self.lock = threading.Lock()

    def control(self, typ, payload, context=None):
        event = self.harness.event(context or self.context, typ, payload, "h.control", ts_event=stamp(self.clock.now_ms()))
        state, _ = self.control_sink.deliver(event, deadline_ns=time.perf_counter_ns() + int(3e9))
        if state != "DELIVERED":
            raise RuntimeError("harness event not durably admitted")

    def check_budget(self):
        if time.monotonic() - self.started > 840:
            raise RuntimeError("acceptance time cap reached")

    def plan(self, origin, flow):
        return validate_plan({"plan_version": "zd-measurement-plan/0", "provenance": "PILOT", "f01": F01,
            "probe": {"probe_id": "prb-acceptance", "probe_version": "p1", "flow": flow,
                      "clock_id": self.clock.clock_id, "clock_source": "HOST_SHARED"},
            "timeouts": {"step_s": 3, "transaction_s": 10},
            "budget": {"max_duration_s": 20, "max_samples": 3, "max_requests": 27, "grace_s": 3},
            "heartbeat_s": 2, "target": {"origin": origin, "allowed_origins": [origin]}})

    def phase(self, name, origin):
        self.check_budget()
        allowed = {"boutique-healthy", "checkout-unavailable", "checkout-restored", "frontend-unavailable",
                   "frontend-restored", "fixture-healthy", "fixture-locked", "fixture-restored"}
        if name not in allowed or name in self.results:
            raise ValueError("unknown or repeated phase")
        fixture = name.startswith("fixture-")
        flow_name = "fixture" if fixture else "checkout"
        if self.transactions[flow_name] + 3 > 30:
            raise RuntimeError("transaction cap reached")
        spec = fixture_spec() if fixture else boutique_spec(PRODUCT, "Sunglasses", FORM)
        spec["provenance"] = "OBSERVED runtime-01: real SQLite CRUD" if fixture else "OBSERVED runtime-01/observation.json"
        if fixture:
            spec["spec_version"] = "fixture-sqlite-crud/1"
        flow = Flow(spec, origin, [origin])
        warmup = None
        if not fixture and not name.endswith("unavailable"):
            # Explicit warm-up is outside the measured window, including after a cold deployment restart.
            # Keep its actual timeout/failure, count the transaction and never turn it into a passed sample.
            if self.transactions[flow_name] + 4 > 30:
                raise RuntimeError("transaction cap reached")
            warmup = flow.run(time.perf_counter_ns() + int(30e9), threading.Event(), Memory())
            self.transactions[flow_name] += 1
            (ROOT / (name + ".warmup.json")).write_bytes(canonical(warmup))
            if not warmup["ok"]:
                raise RuntimeError("warm-up did not complete; do not start measured phase")
        plan = self.plan(origin, flow_name)
        context = dict(self.context, trial_id=new_id("trl"))
        outbox = Outbox(ROOT / (name + ".outbox.jsonl"))
        journal = Journal(ROOT / (name + ".journal.jsonl"))
        runner = ProbeRunner(plan, flow, context, self.clock,
                   Publisher(outbox, HttpHSink("http://127.0.0.1:9131", self.keys["probe"])), journal=journal)
        began = self.clock.now_ms()
        self.control("TRIAL_STARTED", {"warmup_end": stamp(began),
            "planned_window": {"start": stamp(began), "end": stamp(began + 20000)}, "probes": [runner.registration()]}, context)
        blocker = sqlite3.connect(DB) if name == "fixture-locked" else None
        try:
            if blocker:
                blocker.execute("BEGIN EXCLUSIVE")
            summary = runner.run()
        finally:
            if blocker:
                blocker.rollback()
                blocker.close()
        self.control("TRIAL_ENDED", {"end_reason": "PLANNED"}, context)
        self.transactions[flow_name] += summary["samples"] + summary["cancelled"]
        rows = [record["envelope"] for record in self.archive.records(self.context["run_id"])]
        events = [e for e in rows if e.get("trial_id") == context["trial_id"] and e["event_type"] == "PROBE_SAMPLE"]
        expected = not name.endswith(("unavailable", "locked"))
        actual = [e["payload"]["pass"] for e in events]
        facts = {"name": name, "trial_id": context["trial_id"], "plan": plan, "spec": spec,
                 "summary": summary, "warmup": warmup, "expected_pass": expected, "actual_pass": actual,
                 "samples": [e["event_id"] for e in events], "verdict": "PASS" if actual == [expected] * 3 else "FAIL"}
        if name in ("checkout-unavailable", "fixture-locked"):
            health = request(origin + ("/health" if fixture else "/"), deadline_ns=time.perf_counter_ns() + int(3e9))
            facts["independent_home_status"] = health.status
            if health.status != 200:
                facts["verdict"] = "FAIL"
        self.results[name] = facts
        (ROOT / (name + ".json")).write_bytes(canonical(facts))
        if facts["verdict"] != "PASS":
            raise RuntimeError("phase expectation failed; preserve evidence")
        return facts

    def observe(self, origin):
        self.check_budget()
        if "observation" in self.results:
            raise ValueError("observation already run")
        pages = {}
        def observing(url, method, headers, body, deadline, cancel):
            response = request(url, method, headers, body, deadline, cancel)
            if method == "GET" and url.endswith("/cart"):
                text = response.body.decode()
                import re
                pages["cart_markers"] = [m.group(0) for m in re.finditer(r"SKU #[^<\n]{0,60}|Quantity:[^\n]{0,120}", text)]
            if url.endswith("/cart/checkout"):
                text = response.body.decode()
                pages["order_complete"] = "order is complete" in text.lower()
                pages["confirmation_present"] = "Confirmation" in text
            return response
        result = Flow(boutique_spec(PRODUCT, "Sunglasses", FORM), origin, [origin]).run(
            time.perf_counter_ns() + int(30e9), threading.Event(), Memory(), http=observing)
        self.transactions["checkout"] += 1
        facts = {"utc": stamp(self.clock.now_ms()), "result": result, "observed": pages,
                 "scope": "one real marker observation; counted toward 30 transaction cap"}
        self.results["observation"] = facts
        (ROOT / "observation.json").write_bytes(canonical(facts))
        if not result["ok"]:
            raise RuntimeError("business marker observation failed")
        return facts

    def finish(self):
        self.check_budget()
        if len(self.results) != 9:
            raise RuntimeError("missing acceptance phases")
        self.control("RUN_CLOSED", {"close_reason": "ACCEPTANCE_COMPLETE", "recorder_manifest_ref": "export-H/manifest.json"})
        self.archive.export(self.context["run_id"], ROOT / "export-H")
        with sqlite3.connect(DB) as db:
            remaining = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        result = {"run_id": self.context["run_id"], "transactions": self.transactions,
                  "sqlite_rows_remaining": remaining, "wall_s": time.monotonic() - self.started,
                  "phases": {k: v.get("verdict", "OBSERVED") for k, v in self.results.items()},
                  "clock": self.clock.envelope(), "scope": "real AC-01 acceptance; no detector/healer/LLM or research KPI claim",
                  "verdict": "PASS" if remaining == 0 else "FAIL"}
        (ROOT / "receipt.json").write_bytes(canonical(result))
        return result


def serve_acceptance():
    acceptance = Acceptance()
    class Control(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            try:
                command = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                with acceptance.lock:
                    action = command["action"]
                    if action == "observe":
                        result = acceptance.observe(command["origin"])
                    elif action == "phase":
                        result = acceptance.phase(command["name"], command["origin"])
                    elif action == "finish":
                        result = acceptance.finish()
                    else:
                        raise ValueError("unknown action")
                code = 200
            except Exception as error:
                code, result = 500, {"error": type(error).__name__, "detail": str(error)}
            raw = canonical(result)
            self.send_response(code)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
    ThreadingHTTPServer(("127.0.0.1", PORT), Control).serve_forever()


if __name__ == "__main__":
    if sys.argv[1] == "serve":
        serve_acceptance()
    else:
        command = json.loads(sys.argv[1])
        with urlopen(Request(f"http://127.0.0.1:{PORT}/", data=canonical(command)), timeout=60) as response:
            print(response.read().decode())
