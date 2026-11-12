"""ZER-27 readiness, offline: formal B2 wiring, durable budget claims, call records and the M12 join.

Real agents, adapter, budget and contract. Fake model transport, fake Kubernetes API, fake probes
and in-memory O writers. Socket connections are forbidden by the inherited fixture.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import unittest.mock

import httpx

import test_gaia_diagnosis as gaia_base
import test_hephaestus_recovery as base

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))

from event_pipeline import formal_b2
from event_pipeline.contract import Producer, canonical, new_id, validate
from event_pipeline.formal_capture import METHOD
from event_pipeline.formal_config import RulesResolver
from event_pipeline.llm import Adapter, BudgetExceeded, Limits
from gaia.diagnosis import Diagnoser
from hephaestus.recovery import Healer, Journal, healer_resolver_sha256
from measurement import containment_join

LIMITS = dict(attempts=1, timeout_s=1, deadline_s=2, retry_delay_s=0, max_output_tokens=256)
SCHEDULE = "5" * 64
RECEIPT = "6" * 64
FULL = {"attempts_dispatched": 2, "reserved_tokens": 4000, "reserved_estimate_usd": 0.002,
        "unknown_usage_attempts": 0, "blocked": False}


class NoUsage(gaia_base.Fake):
    async def send(self, payload, timeout):
        response = await super().send(payload, timeout)
        del response["body"]["usage"]
        return response


class Disconnected(gaia_base.Fake):
    """The connection fails before any HTTP response exists."""
    async def send(self, payload, timeout):
        self.requests.append(payload)
        raise httpx.ConnectError("fake")


class Broken(gaia_base.Fake):
    """The transport fails with an error that is neither a timeout nor a network error."""
    async def send(self, payload, timeout):
        self.requests.append(payload)
        raise RuntimeError("fake")


class Router:
    """One transport for the shared adapter: Gaia and Hephaestus requests go to their own fake."""
    def __init__(self, gaia, heal):
        special = {"NO_USAGE": NoUsage, "NETWORK": Disconnected, "TRANSPORT": Broken}
        self.gaia = special[gaia]() if gaia in special else gaia_base.Fake(gaia)
        self.heal = base.Model(heal)

    async def send(self, payload, timeout):
        properties = payload["text"]["format"]["schema"]["properties"]
        return await (self.gaia if "classification" in properties else self.heal).send(payload, timeout)


class B2Flow(base.Recovery):
    def trial(self, gaia="OK", heal="BLOCK_IP", *, decision_ack=None, trace_ack=None, ledger=None):
        """A fresh formal trial: new context, one traced adapter and one pinned budget for both agents."""
        base.Recovery.setUp(self)
        self.ctx["method_version"] = self.detected["method_version"] = METHOD
        self.router = Router(gaia, heal)
        self.o, self.local, self.writes_at_trace = [], [], []
        self.ledger = ledger or Path(self.tmp.name) / "b2-budget.jsonl"

        def record(event):
            self.o.append(event)
            return {"status": "RECORDED", "event_id": event["event_id"]}

        def trace(event):
            self.writes_at_trace.append(self.api.writes)
            return (trace_ack or record)(event)

        self.record = record
        self.adapter = formal_b2.TracedAdapter(
            Adapter(self.router, formal_b2.trial_budget(self.ctx["run_id"]), limits=Limits(**LIMITS)), trace)
        self.diagnoser = Diagnoser(self.adapter, self.ctx, self.local.append, formal_o_sink=decision_ack or record)
        journal = Journal(self.tmp.name, self.ctx)
        self.addCleanup(journal.close)
        self.healer = Healer(self.adapter, self.ctx, api=self.api, pins=self.pins, fixture_uid=base.POD,
                             journal=journal, probe=self.probe, wall_clock=lambda: self.wall,
                             formal_o_sink=decision_ack or record, resolver_sha256=healer_resolver_sha256())
        payload = self.detected["payload"]
        self.evidence = {"metric": {"name": payload["metric"], "value": payload["value"],
                                    "threshold": payload["threshold"]},
                         "log": {"message": "synthetic access pattern", "observed_at": None}}

    async def run_trial(self, *, block=1, **changes):
        arguments = dict(evidence=self.evidence, access=self.access)
        arguments.update(changes)
        return await formal_b2.run_trial(self.diagnoser, self.healer, self.detected, arguments["evidence"],
                                         arguments["access"], ledger=self.ledger, block=block,
                                         schedule_sha256=SCHEDULE)

    def kinds(self):
        return [(event["event_type"], event["payload"].get("response_kind") or event["payload"].get("outcome"))
                for event in self.o]

    def state(self):
        return formal_b2.ledger_state(formal_b2.read_ledger(self.ledger))[self.ctx["trial_id"]]["state"]

    def replay(self, events=None):
        return formal_b2.call_records(self.o if events is None else events)[(self.ctx["run_id"], self.ctx["trial_id"])]

    def claim(self, trial_id=None, *, block=1, ledger=None, schedule=SCHEDULE, **kw):
        return formal_b2.claim(ledger or self.ledger, schedule_sha256=schedule, block=block,
                               run_id=self.ctx["run_id"], trial_id=trial_id or new_id("trl"), **kw)["status"]

    def full_trial(self, block=1, summary=FULL, coverage="RECORDED"):
        trial_id = new_id("trl")
        self.assertEqual("ADMIT", self.claim(trial_id, block=block))
        formal_b2.settle(self.ledger, trial_id=trial_id, summary=summary, call_coverage=coverage)
        return trial_id

    # ------------------------------------------------------------------ evidence path
    async def test_readiness_trial_archives_one_decision_and_every_call_record(self):
        self.trial()
        self.assertEqual([], formal_b2.preflight(self.adapter))
        summary = await self.run_trial()
        self.assertEqual(("OK", "ACTION_COMPLETED", None, "SETTLED"),
                         (summary["gaia"]["status"], summary["hephaestus"]["status"], summary["stop"],
                          summary["settle"]))
        # Each call record reaches O when its call ends: before the decision and before any API write.
        self.assertEqual([("LLM_CALL", "OK"), ("LLM_CALL", "OK"), ("DECISION", "ACTION")], self.kinds())
        self.assertEqual([0, 0], self.writes_at_trace)
        self.assertEqual(1, self.api.writes)
        self.assertTrue(all(validate(event, "O", "decision_llm") is None for event in self.o))
        decision = self.o[2]["payload"]
        self.assertEqual(("PROPOSAL", "RESOLVED", 180),
                         (decision["stage"], decision["pre_guard"]["status"], decision["pre_guard"]["ttl_s"]))
        self.assertEqual({"status": "RECORDED", "dispatched": 2, "archived": 2, "unarchived": 0},
                         summary["call_coverage"])
        replay = self.replay()
        self.assertEqual((2, 2, 0, 0, []), (replay["calls"], replay["confirmed_calls"], replay["http_errors"],
                                            replay["unknown_usage_attempts"], replay["unverified_attempts"]))
        self.assertEqual(replay, self.replay(self.o + self.o))
        self.assertEqual("SETTLED", self.state())
        self.assertIsNone(summary["session_stop"])
        with self.assertRaises(BudgetExceeded):  # a third call in the trial is refused by the budget itself
            self.adapter.budget.reserve(self.ctx["run_id"], 1, 1)

    async def test_readiness_gaia_ending_stops_before_hephaestus(self):
        for mode, status, decisions in (("TIMEOUT", "TIMEOUT", ["TIMEOUT"]), ("JSON", "SCHEMA_INVALID", ["SCHEMA_INVALID"]),
                                        ("REFUSAL", "REFUSAL", ["REFUSAL"]), ("UNKNOWN", "ABSTAIN", ["ABSTAIN"]),
                                        ("429", "HTTP_ERROR", [])):
            with self.subTest(mode=mode):
                self.trial(gaia=mode)
                summary = await self.run_trial()
                self.assertEqual((status, None, "GAIA_" + status),
                                 (summary["gaia"]["status"], summary["hephaestus"], summary["stop"]))
                self.assertEqual(decisions, [kind for name, kind in self.kinds() if name == "DECISION"])
                self.assertEqual((1, 0, 0), (len(self.router.gaia.requests), len(self.router.heal.requests),
                                             self.api.writes))
                self.assertFalse(self.healer.started)
                self.assertEqual("RECORDED", summary["call_coverage"]["status"])
                self.assertEqual(1, self.replay()["calls"])

    async def test_readiness_call_record_does_not_depend_on_the_decision_receipt(self):
        """Codex P1: Gaia TIMEOUT with a wrong decision ACK left 1 dispatch and 0 LLM_CALL in O."""
        self.trial(gaia="TIMEOUT", decision_ack=lambda event: {"status": "RECORDED", "event_id": new_id("evt")})
        summary = await self.run_trial()
        self.assertEqual(("GAIA_DECISION_ARCHIVE_UNVERIFIED", None), (summary["stop"], summary["hephaestus"]))
        self.assertEqual([("LLM_CALL", "TIMEOUT")], self.kinds())
        self.assertEqual({"status": "RECORDED", "dispatched": 1, "archived": 1, "unarchived": 0},
                         summary["call_coverage"])
        self.assertEqual((1, {"TIMEOUT": 1}), (self.replay()["calls"], self.replay()["outcomes"]))
        self.assertEqual(0, len(self.router.heal.requests))
        # The same wrong ACK at Hephaestus is an evidence-write failure: no guard, no dispatch.
        self.trial(decision_ack=lambda event: {"status": "RECORDED", "event_id": new_id("evt")})
        summary = await self.run_trial()
        self.assertEqual(("FAILED", "FORMAL_DECISION_ARCHIVE_UNVERIFIED"),
                         (summary["hephaestus"]["status"], summary["hephaestus"]["reason"]))
        self.assertEqual("HEPHAESTUS_DECISION_ARCHIVE_UNVERIFIED", summary["session_stop"])
        self.assertEqual("SETTLED", summary["settle"])
        self.assertEqual(([("LLM_CALL", "OK"), ("LLM_CALL", "OK")], 0, "RECORDED"),
                         (self.kinds(), self.api.writes, summary["call_coverage"]["status"]))


    async def test_readiness_unverified_settlement_stops_the_session(self):
        self.trial()
        with unittest.mock.patch.object(formal_b2, "settle", side_effect=OSError("synthetic disk failure")):
            summary = await self.run_trial()
        self.assertEqual(("UNVERIFIED", "BUDGET_SETTLEMENT_UNVERIFIED"),
                         (summary["settle"], summary["session_stop"]))
        self.assertEqual("OPEN", self.state())
        self.assertEqual("HOLD_OPEN_CLAIM", self.claim())

    async def test_readiness_unarchived_call_record_stops_before_decision_and_dispatch(self):
        wrong = lambda event: {"status": "RECORDED", "event_id": new_id("evt")}
        self.trial(trace_ack=wrong)
        summary = await self.run_trial()
        self.assertEqual(("CALL_RECORD_ARCHIVE_UNVERIFIED", None, None),
                         (summary["stop"], summary["gaia"], summary["hephaestus"]))
        self.assertEqual({"status": "UNVERIFIED", "dispatched": 1, "archived": 0, "unarchived": 1},
                         summary["call_coverage"])
        self.assertEqual((0, 0, []), (len(self.router.heal.requests), self.api.writes, self.o))
        self.assertEqual("UNVERIFIED", self.state())
        # Only the Hephaestus record fails: its decision is not archived and nothing is dispatched.
        seen = []
        self.trial(trace_ack=lambda event: seen.append(event) or (self.record(event) if len(seen) == 1 else wrong(event)))
        summary = await self.run_trial()
        self.assertEqual(("CALL_RECORD_ARCHIVE_UNVERIFIED", "FAILED"),
                         (summary["stop"], summary["hephaestus"]["status"]))
        self.assertEqual(([("LLM_CALL", "OK")], 0, 2, 1),
                         (self.kinds(), self.api.writes, summary["call_coverage"]["dispatched"],
                          summary["call_coverage"]["archived"]))

    async def test_readiness_provider_http_error_is_replayable_and_order_independent(self):
        self.trial(gaia="429")
        summary = await self.run_trial()
        record, = [event for event in self.o if event["event_type"] == "LLM_CALL"]
        self.assertEqual(("HTTP_ERROR", "HTTP_429"), (record["payload"]["outcome"], record["payload"]["reason_code"]))
        self.assertEqual((self.ctx["run_id"], self.ctx["trial_id"], summary["gaia"]["decision_id"], 1),
                         (record["run_id"], record["trial_id"], record["decision_id"], record["payload"]["attempt_no"]))
        for events in (self.o, self.o * 3):
            replay = self.replay(events)
            self.assertEqual((1, 1, 1, 0, 1, {"HTTP_429": 1}, []),
                             (replay["calls"], replay["confirmed_calls"], replay["http_errors"],
                              replay["transport_errors"], replay["unknown_usage_attempts"], replay["reasons"],
                              replay["unverified_attempts"]))
        # No decision reached O, so M1 for this cell stays UNKNOWN (locked protocol, section 4).
        self.assertEqual([], [event for event in self.o if event["event_type"] == "DECISION"])
        # Codex P1: a second receipt for the same attempt with another outcome. Either read order
        # gives the same answer: the attempt is one call, and no HTTP error is confirmed.
        other = json.loads(json.dumps(record))
        other["event_id"] = new_id("evt")
        other["payload"].update(outcome="TIMEOUT", reason_code="TIMEOUT")
        self.assertIsNone(validate(other, "O"))
        forward, backward = self.replay([record, other]), self.replay([other, record])
        self.assertEqual(forward, backward)
        self.assertEqual((1, 0, 0, 0, {}, [{"call_id": record["call_id"], "attempt_no": 1, "records": 2}]),
                         (forward["calls"], forward["confirmed_calls"], forward["http_errors"],
                          forward["transport_errors"], forward["outcomes"], forward["unverified_attempts"]))
        # A record from another trial never changes this trial's numbers.
        foreign = json.loads(json.dumps(record))
        foreign.update(event_id=new_id("evt"), trial_id=new_id("trl"))
        self.assertEqual(self.replay([record]), self.replay([foreign, record]))

    async def test_readiness_lost_connection_is_not_counted_as_an_http_error(self):
        """Codex P2: a request without any HTTP response is a transport error, not an HTTP error."""
        for mode, reason in (("NETWORK", "NETWORK"), ("TRANSPORT", "TRANSPORT_ERROR")):
            with self.subTest(mode):
                self.trial(gaia=mode)
                summary = await self.run_trial()
                self.assertEqual(("GAIA_HTTP_ERROR", 1, 0, 0),
                                 (summary["stop"], len(self.router.gaia.requests),
                                  len(self.router.heal.requests), self.api.writes))
                record, = self.o
                # The archived outcome is unchanged; only the replay separates the two groups.
                self.assertEqual(("LLM_CALL", "HTTP_ERROR", reason),
                                 (record["event_type"], record["payload"]["outcome"], record["payload"]["reason_code"]))
                for events in (self.o, self.o * 3):
                    replay = self.replay(events)
                    self.assertEqual((1, 1, 0, 1, {"HTTP_ERROR": 1}, {reason: 1}, []),
                                     (replay["calls"], replay["confirmed_calls"], replay["http_errors"],
                                      replay["transport_errors"], replay["outcomes"], replay["reasons"],
                                      replay["unverified_attempts"]))
                # A lost connection next to a 429 in the same trial: one of each, in either read order.
                answered = json.loads(json.dumps(record))
                answered.update(event_id=new_id("evt"), call_id=new_id("cal"))
                answered["payload"]["reason_code"] = "HTTP_429"
                self.assertIsNone(validate(answered, "O"))
                forward, backward = self.replay([record, answered]), self.replay([answered, record, answered])
                self.assertEqual(forward, backward)
                self.assertEqual((2, 2, 1, 1), (forward["calls"], forward["confirmed_calls"],
                                                forward["http_errors"], forward["transport_errors"]))
                # A reason that is not a real HTTP status is never confirmed as an HTTP error.
                for label in ("HTTP_", "HTTP_42", "HTTP_4290", "HTTP_999", "http_429", None):
                    odd = json.loads(json.dumps(record))
                    odd["payload"]["reason_code"] = label
                    if validate(odd, "O") is None:
                        self.assertEqual((0, 1), (self.replay([odd])["http_errors"],
                                                  self.replay([odd])["transport_errors"]), label)

    async def test_readiness_unverified_usage_makes_a_counted_not_run_cell(self):
        self.trial(gaia="NO_USAGE")
        summary = await self.run_trial()
        self.assertEqual(("OK", "NOT_RUN", "HEAL_USAGE_UNKNOWN_OR_OVER_BUDGET", ["hephaestus"]),
                         (summary["gaia"]["status"], summary["hephaestus"]["status"],
                          summary["hephaestus"]["reason"], summary["not_run"]))
        self.assertEqual((0, 0), (len(self.router.heal.requests), self.api.writes))
        self.assertEqual([("LLM_CALL", "OK")], self.kinds())
        self.assertEqual(1, self.replay()["unknown_usage_attempts"])
        self.assertEqual("UNVERIFIED", self.state())
        self.assertEqual("BUDGET_USAGE_UNVERIFIED", summary["session_stop"])
        self.assertEqual("HOLD_USAGE_UNVERIFIED", self.claim())

    # ------------------------------------------------------------------ durable budget
    async def test_readiness_interrupted_trial_holds_every_later_claim_until_reconciled(self):
        """Codex P1: a process that died after dispatch must not be admitted again."""
        self.trial()

        async def crash(*_):
            raise RuntimeError("process stopped after the model call")

        self.healer.run = crash
        with self.assertRaises(RuntimeError):
            await self.run_trial()
        interrupted, ledger = self.ctx["trial_id"], self.ledger
        self.assertEqual("OPEN", self.state())
        rows = len(formal_b2.read_ledger(ledger))
        # Reopened: the same trial and every other trial hold, and no model is called.
        self.assertEqual("HOLD_OPEN_CLAIM", self.claim(interrupted))
        self.trial(ledger=ledger)
        summary = await self.run_trial()
        self.assertEqual(("BUDGET:HOLD_OPEN_CLAIM", None, 0, []),
                         (summary["stop"], summary["gaia"], len(self.router.gaia.requests), self.o))
        self.assertEqual(rows, len(formal_b2.read_ledger(ledger)))
        # Only a named approval with a usage receipt closes it; the whole allocation stays charged.
        for approver, receipt in (("", RECEIPT), ("Hoang", "not-a-hash")):
            with self.assertRaisesRegex(ValueError, "FORMAL_B2_LEDGER_RECONCILE_REFUSED"):
                formal_b2.reconcile(ledger, trial_id=interrupted, approved_by=approver, usage_receipt_sha256=receipt)
        formal_b2.reconcile(ledger, trial_id=interrupted, approved_by="Hoang", usage_receipt_sha256=RECEIPT)
        state = formal_b2.ledger_state(formal_b2.read_ledger(ledger))[interrupted]
        self.assertEqual(("RECONCILED", 2, 30000), (state["state"], state["calls"], state["reserved_tokens"]))
        self.assertEqual("REFUSE_TRIAL_ALREADY_RECORDED", self.claim(interrupted))
        self.full_trial()
        self.assertEqual("REFUSE_LIMIT", self.claim())

    def test_readiness_two_callers_cannot_both_reserve(self):
        """Codex P1: check and write are one step, so concurrent callers see each other's claim."""
        self.trial()
        self.full_trial()
        gate, results = threading.Barrier(8), []

        def caller():
            gate.wait()
            results.append(self.claim())

        threads = [threading.Thread(target=caller) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(["ADMIT"] + ["HOLD_OPEN_CLAIM"] * 7, sorted(results))
        self.assertEqual(1, sum(row["kind"] == "CLAIM" for row in formal_b2.read_ledger(self.ledger)) - 1)
        self.assertFalse(Path(str(self.ledger) + ".lock").exists())

    def test_readiness_block_and_total_limits_hold_across_trials(self):
        self.trial()
        self.full_trial()
        self.full_trial()
        self.assertEqual("REFUSE_LIMIT", self.claim())
        self.assertEqual(2, len(formal_b2.ledger_state(formal_b2.read_ledger(self.ledger))))
        for block in (2, 3, 4, 5):
            self.full_trial(block)
            self.full_trial(block)
        # Ten full trials reach the total of 20 calls even though block 6 is empty.
        self.assertEqual("REFUSE_LIMIT", self.claim(block=6))
        self.assertEqual("REFUSE_SCHEDULE_MISMATCH", self.claim(block=6, schedule="7" * 64))
        self.assertEqual("REFUSE_CLAIM_INVALID", self.claim(block=0))

    def test_readiness_ledger_that_cannot_be_trusted_holds(self):
        self.trial()
        # A lock left by a dead process is never broken automatically.
        lock = Path(str(self.ledger) + ".lock")
        lock.write_text("stale")
        self.assertEqual("HOLD_LEDGER_LOCKED", self.claim(lock_wait_s=0.05))
        self.assertFalse(self.ledger.exists())
        lock.unlink()
        # A torn last line or an edited row cannot prove what was spent.
        self.full_trial()
        with self.ledger.open("a", encoding="utf-8") as stream:
            stream.write('{"kind": "CLAIM", "block": 1')
        self.assertEqual("HOLD_LEDGER_INVALID", self.claim())
        with self.assertRaisesRegex(ValueError, "FORMAL_B2_LEDGER_INVALID"):
            formal_b2.read_ledger(self.ledger)
        # A settlement needs this trial's own open claim.
        other = Path(self.tmp.name) / "other.jsonl"
        with self.assertRaisesRegex(ValueError, "FORMAL_B2_LEDGER_SETTLE_REFUSED"):
            formal_b2.settle(other, trial_id=new_id("trl"), summary=FULL, call_coverage="RECORDED")

    async def test_readiness_ledger_without_its_final_newline_holds_before_any_call(self):
        """Codex P1: a last row that lost its newline is refused even though its JSON is complete."""
        self.trial()
        self.full_trial()
        ledger, whole = self.ledger, self.ledger.read_bytes()
        self.assertTrue(whole.endswith(b"}\n") and b"\r" not in whole)
        self.assertEqual(2, len(formal_b2.read_ledger(ledger)))
        last = whole.rstrip(b"\n").rsplit(b"\n", 1)[1]
        self.assertEqual("SETTLE", json.loads(last)["kind"])
        damaged = {"no final newline": whole[:-1],
                   "CRLF row endings": whole.replace(b"\n", b"\r\n"),
                   "CR in place of the final newline": whole[:-1] + b"\r",
                   "blank last line": whole + b"\n",
                   "reformatted row": whole.replace(b'"kind": "SETTLE"', b'"kind":"SETTLE"'),
                   "duplicated key": whole[:-2] + b', "kind": "SETTLE"}\n'}
        for label, content in damaged.items():
            with self.subTest(label):
                self.trial(ledger=ledger)
                ledger.write_bytes(content)
                self.assertEqual("HOLD_LEDGER_INVALID", self.claim())
                summary = await self.run_trial()
                self.assertEqual(("BUDGET:HOLD_LEDGER_INVALID", None, None),
                                 (summary["stop"], summary["gaia"], summary["hephaestus"]))
                self.assertEqual((0, 0, 0, [], 0),
                                 (len(self.router.gaia.requests), len(self.router.heal.requests), self.api.writes,
                                  self.o, summary["budget"]["attempts_dispatched"]))
                # Nothing was appended to a ledger that cannot be trusted, and it is never repaired here.
                self.assertEqual(content, ledger.read_bytes())
                for change in (lambda: formal_b2.settle(ledger, trial_id=new_id("trl"), summary=FULL,
                                                        call_coverage="RECORDED"),
                               lambda: formal_b2.reconcile(ledger, trial_id=new_id("trl"), approved_by="Hoang",
                                                           usage_receipt_sha256=RECEIPT)):
                    with self.assertRaisesRegex(ValueError, "FORMAL_B2_LEDGER_INVALID"):
                        change()
                self.assertEqual(content, ledger.read_bytes())
        # The intact bytes are accepted again: the refusal comes from the bytes, not from a flag.
        self.trial(ledger=ledger)
        ledger.write_bytes(whole)
        summary = await self.run_trial()
        self.assertEqual((None, "SETTLED", 1), (summary["stop"], summary["settle"], len(self.router.gaia.requests)))

    def test_readiness_short_ledger_write_holds_and_is_refused_on_reopen(self):
        """A claim row that did not reach the file whole is not an admission."""
        self.trial()
        self.full_trial()
        whole, real = self.ledger.read_bytes(), formal_b2.os.write

        def short(descriptor, data):
            return real(descriptor, data[:len(data) // 2])

        with unittest.mock.patch.object(formal_b2.os, "write", short):
            self.assertEqual("HOLD_LEDGER_INVALID", self.claim())
        torn = self.ledger.read_bytes()
        self.assertTrue(torn.startswith(whole) and len(torn) > len(whole) and not torn.endswith(b"\n"))
        self.assertEqual("HOLD_LEDGER_INVALID", self.claim())
        self.assertEqual(torn, self.ledger.read_bytes())
        self.assertFalse(Path(str(self.ledger) + ".lock").exists())

    async def test_readiness_preflight_refuses_before_any_provider_call(self):
        self.assertLessEqual(formal_b2.call_reserve_bound(Limits(attempts=1, max_output_tokens=512)),
                             formal_b2.CALL_TOKENS)
        self.trial()
        retrying = Adapter(self.router, formal_b2.trial_budget(self.ctx["run_id"]),
                           limits=Limits(**dict(LIMITS, attempts=2)))
        self.assertEqual(["RETRY_ENABLED"], formal_b2.preflight(retrying))
        loose = Adapter(self.router, base.RunBudget(self.ctx["run_id"], max_calls=3, max_reserved_tokens=30000,
                                                    max_estimated_usd=.005, duration_s=60), limits=Limits(**LIMITS))
        self.assertEqual(["TRIAL_BUDGET_NOT_PINNED"], formal_b2.preflight(loose))
        self.adapter.budget.reserve(self.ctx["run_id"], 1, 1)
        summary = await self.run_trial()
        self.assertEqual(("PREFLIGHT:TRIAL_BUDGET_NOT_FRESH", None, None, None),
                         (summary["stop"], summary["gaia"], summary["hephaestus"], summary["claim"]))
        self.assertEqual((0, 0, []), (len(self.router.gaia.requests), len(self.router.heal.requests), self.o))
        self.assertFalse(self.ledger.exists())

    # ------------------------------------------------------------------ input refused before send
    async def test_readiness_rejected_joined_input_is_recorded_the_same_way_by_both_agents(self):
        rows = {}
        for agent, changes in (("gaia", {"evidence": {}}), ("hephaestus", {"access": {}})):
            self.trial()
            summary = await self.run_trial(**changes)
            decision, = [event["payload"] for event in self.o if event["event_type"] == "DECISION"]
            rows[agent] = (summary[agent]["status"], decision["response_kind"], decision["reason_code"],
                           decision["prompt_sha256"], len(getattr(self.router, "heal" if agent == "hephaestus"
                                                                  else "gaia").requests), self.api.writes)
        expected = {"gaia": ("INPUT_REJECTED", "SCHEMA_INVALID", "INPUT_REJECTED", None, 0, 0),
                    "hephaestus": ("SCHEMA_INVALID", "SCHEMA_INVALID", "INPUT_REJECTED", None, 0, 0)}
        self.assertEqual(expected, rows)

    async def adapter_error(self, agent, code):
        """Make the real adapter raise `code` for one agent before it sends anything."""
        self.trial()
        real, target = self.adapter.inner.call, "Diagnosis" if agent == "gaia" else "Choice"

        async def call(context, **kw):
            if kw["output_model"].__name__ == target:
                raise ValueError(code)
            return await real(context, **kw)

        self.adapter.inner.call = call
        summary = await self.run_trial()
        decisions = [(event["payload"]["response_kind"], event["payload"]["reason_code"],
                      event["payload"]["prompt_sha256"]) for event in self.o if event["event_type"] == "DECISION"
                     and event["payload"]["response_kind"] != "ACTION"]
        requests = self.router.gaia.requests if agent == "gaia" else self.router.heal.requests
        return summary[agent]["status"], summary[agent]["reason"], decisions, len(requests), self.api.writes

    async def test_readiness_named_adapter_refusal_is_recorded_the_same_way_by_both_agents(self):
        recorded = [("SCHEMA_INVALID", "INPUT_REJECTED", None)]
        for code in ("LLM_REQUEST_TOO_LARGE", "LLM_INPUT_OR_MODE_INVALID"):
            with self.subTest(code=code):
                self.assertEqual(("INPUT_REJECTED", "ADAPTER_INPUT_INVALID", recorded, 0, 0),
                                 await self.adapter_error("gaia", code))
                self.assertEqual(("SCHEMA_INVALID", "INPUT_REJECTED", recorded, 0, 0),
                                 await self.adapter_error("hephaestus", code))

    async def test_readiness_internal_error_is_not_recorded_as_a_model_decision(self):
        self.assertEqual(("FAILED", "GAIA_INTERNAL_FAILURE", [], 0, 0),
                         await self.adapter_error("gaia", "LLM_OUTPUT_MODEL_MUST_FORBID_EXTRA"))
        self.assertEqual(("FAILED", "LOCAL_RECORD_OR_MODEL_FAILURE", [], 0, 0),
                         await self.adapter_error("hephaestus", "LLM_OUTPUT_MODEL_MUST_FORBID_EXTRA"))

    def test_readiness_b1_and_b2_read_the_same_observation_once(self):
        self.trial()
        b1 = dict(self.ctx, group="B1")
        alert = Producer("detector", "test", base.CLOCK).event(
            b1, "DETECTED", self.detected["payload"], "o.alert", target=self.detected["target"],
            alert_id=new_id("alt"))
        with tempfile.TemporaryDirectory() as directory:
            resolver = RulesResolver(Path(directory).resolve(), run_id=b1["run_id"], trial_id=b1["trial_id"])
            # No record yet: both groups get an explicit missing result from one read, no waiting.
            self.assertEqual({"status": "OBSERVATION_MISSING"}, resolver(alert))
            self.assertIsNone(formal_b2.read_access(directory, self.detected))
            for event in (alert, self.detected):
                record = dict(self.access, detection_event_id=event["event_id"])
                (Path(directory) / (event["event_id"] + ".json")).write_bytes(canonical(record))
            resolved = resolver(alert)
            access = formal_b2.read_access(directory, self.detected)
            self.assertEqual(("RESOLVED", access["client_ip"], access["fixture_uid"], 180),
                             tuple(resolved[key] for key in ("status", "source", "fixture_uid", "ttl_s")))
            # The same record passes the Hephaestus input check unchanged.
            self.assertEqual(access, self.healer.observation(self.detected, access))
            (Path(directory) / (self.detected["event_id"] + ".json")).write_bytes(b"{broken")
            self.assertEqual({}, formal_b2.read_access(directory, self.detected))
            (Path(directory) / (alert["event_id"] + ".json")).write_bytes(b"{broken")
            self.assertEqual({"status": "RESOLVER_ERROR"}, resolver(alert))


class ContainmentJoin(unittest.TestCase):
    RUN, TRIAL, ACTION = new_id("run"), new_id("trl"), new_id("act")
    EXPECTED = {"source": "10.42.0.10", "fixture_uid": "fixture-uid-1", "ttl_s": 180, "policy_uid": "policy-1",
                "policy_scope": "zer46", "benign_source": "10.42.0.11", "boutique_flow": "checkout"}
    RULE = {"action_id": ACTION, "client_ip": "10.42.0.10", "created_at": 1000, "expires_at": 1180}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def put(self, kind, **fields):
        document = dict({"run_id": self.RUN, "trial_id": self.TRIAL, "kind": kind, "clock_id": "h-probe",
                         "observed_at": "2026-11-12T00:00:10.000Z"}, **fields)
        document = {key: value for key, value in document.items() if value != "<absent>"}
        raw = json.dumps(document, sort_keys=True).encode()
        digest = hashlib.sha256(raw).hexdigest()
        (Path(self.tmp.name) / (digest + ".json")).write_bytes(raw)
        return "sha256:" + digest

    def claim(self, **changes):
        documents = {
            "policy": dict(policy_uid="policy-1", scope="zer46", fixture_uid="fixture-uid-1", rules=[self.RULE]),
            "blocked_source_probe": dict(source="10.42.0.10", fixture_uid="fixture-uid-1", status=403,
                                         error="SOURCE_BLOCKED", action_ids=[self.ACTION]),
            "benign_fixture_probe": dict(source="10.42.0.11", fixture_uid="fixture-uid-1", status=200,
                                         restricted_rows=0),
            "boutique_probe": dict(flow="checkout", ok=True)}
        for kind, fields in changes.items():
            documents[kind] = dict(documents[kind], **fields)
        return {field: self.put(kind, **documents[kind]) for kind, field in containment_join.REFS.items()}

    def join(self, claim, *, expected=None, action=ACTION, group="B2", trial=None):
        return containment_join.join(self.EXPECTED if expected is None else expected, action, claim,
                                     self.tmp.name, run_id=self.RUN, trial_id=trial or self.TRIAL, group=group)

    def test_readiness_m12_counts_only_a_full_join(self):
        row = self.join(self.claim())
        self.assertEqual(("VERIFIED", [], []), (row["status"], row["failed"], row["missing"]))
        self.assertEqual({"blocked_source_probe": 403, "benign_fixture_probe": 200, "boutique_probe": None},
                         {kind: probe["status"] for kind, probe in row["probes"].items()})
        self.assertEqual("checkout", row["probes"]["boutique_probe"]["flow"])

    def test_readiness_m12_fixtures_that_were_wrongly_verified(self):
        """Codex P1: each of these returned VERIFIED, or raised, before the field checks."""
        unknown = {
            "benign source null": {"benign_fixture_probe": {"source": None}},
            "policy UID null": {"policy": {"policy_uid": None}},
            "policy UID absent": {"policy": {"policy_uid": "<absent>"}},
            "Boutique flow null": {"boutique_probe": {"flow": None}},
            "Boutique flow empty": {"boutique_probe": {"flow": " "}},
            "rules null": {"policy": {"rules": None}},
            "wrong scope, no UID, no flow": {"policy": {"scope": "other", "policy_uid": None},
                                             "boutique_probe": {"flow": None}}}
        for name, changes in unknown.items():
            with self.subTest(name=name):
                row = self.join(self.claim(**changes))
                self.assertEqual(("UNVERIFIED", []), (row["status"], row["failed"]))
                self.assertTrue(any(item.endswith((":ARTIFACT_FIELD_TYPE", ":ARTIFACT_SCHEMA"))
                                    for item in row["missing"]), row["missing"])
        failed = {"POLICY_IDENTITY": [{"policy": {"scope": "other"}}, {"policy": {"policy_uid": "policy-2"}}],
                  "BOUTIQUE_PROBE": [{"boutique_probe": {"flow": "browse"}}, {"boutique_probe": {"ok": False}}],
                  "BENIGN_FIXTURE_PROBE": [{"benign_fixture_probe": {"source": "10.42.0.12"}},
                                           {"benign_fixture_probe": {"source": "10.42.0.10"}},
                                           {"benign_fixture_probe": {"status": 403}},
                                           {"benign_fixture_probe": {"restricted_rows": 1}}]}
        for reason, cases in failed.items():
            for changes in cases:
                with self.subTest(reason=reason, changes=changes):
                    row = self.join(self.claim(**changes))
                    self.assertEqual(("NOT_VERIFIED", [reason], []), (row["status"], row["failed"], row["missing"]))

    def test_readiness_m12_wrongly_typed_fields_are_never_evidence(self):
        cases = [{"policy": {"rules": {}}}, {"policy": {"rules": [None]}}, {"policy": {"rules": ["rule"]}},
                 {"policy": {"rules": [dict(self.RULE, created_at="1000")]}},
                 {"policy": {"rules": [dict(self.RULE, expires_at=True)]}},
                 {"policy": {"rules": [dict(self.RULE, client_ip="attacker")]}},
                 {"policy": {"rules": [{key: value for key, value in self.RULE.items() if key != "action_id"}]}},
                 {"policy": {"scope": 46}}, {"policy": {"fixture_uid": None}},
                 {"blocked_source_probe": {"status": "403"}}, {"blocked_source_probe": {"status": True}},
                 {"blocked_source_probe": {"action_ids": self.ACTION}}, {"blocked_source_probe": {"action_ids": [1]}},
                 {"blocked_source_probe": {"source": "010.042.000.010"}}, {"blocked_source_probe": {"error": 403}},
                 {"benign_fixture_probe": {"status": 200.0}}, {"benign_fixture_probe": {"restricted_rows": False}},
                 {"benign_fixture_probe": {"restricted_rows": -1}}, {"boutique_probe": {"ok": 1}},
                 {"boutique_probe": {"ok": "true"}}, {"boutique_probe": {"observed_at": "2026-11-12"}},
                 {"policy": {"clock_id": ""}}, {"policy": {"extra": 1}}]
        for changes in cases:
            with self.subTest(changes=changes):
                row = self.join(self.claim(**changes))
                self.assertEqual(("UNVERIFIED", []), (row["status"], row["failed"]))

    def test_readiness_m12_403_without_the_joined_policy_is_not_containment(self):
        other = dict(self.RULE, action_id="act_" + "9" * 32)
        row = self.join(self.claim(policy={"rules": [other]}, blocked_source_probe={"action_ids": []}))
        self.assertEqual(("NOT_VERIFIED", ["POLICY_NOT_JOINED", "BLOCK_WITHOUT_JOINED_ACTION"]),
                         (row["status"], row["failed"]))
        for changes, reason in (
                ({"policy": {"rules": []}}, "POLICY_NOT_JOINED"),
                ({"policy": {"rules": [self.RULE, self.RULE]}}, "POLICY_NOT_JOINED"),
                ({"policy": {"rules": [dict(self.RULE, client_ip="10.42.0.99")]}}, "POLICY_SOURCE"),
                ({"policy": {"rules": [dict(self.RULE, expires_at=1600)]}}, "POLICY_TTL"),
                ({"policy": {"fixture_uid": "other-fixture"}}, "POLICY_NOT_JOINED"),
                ({"blocked_source_probe": {"status": 200, "error": None}}, "BLOCKED_SOURCE_PROBE"),
                ({"blocked_source_probe": {"source": "10.42.0.11"}}, "BLOCKED_SOURCE_PROBE"),
                ({"blocked_source_probe": {"fixture_uid": "other-fixture"}}, "BLOCKED_SOURCE_PROBE")):
            with self.subTest(reason=reason, changes=changes):
                row = self.join(self.claim(**changes))
                self.assertEqual(("NOT_VERIFIED", [reason]), (row["status"], row["failed"]))

    def test_readiness_m12_missing_or_unbound_evidence_stays_unknown(self):
        claim = self.claim()
        partial = {key: value for key, value in self.EXPECTED.items() if key != "policy_scope"}
        cases = {"absent claim": self.join(None), "claim is not a record": self.join("claim"),
                 "other trial": self.join(claim, trial="trl_" + "4" * 32),
                 "no archived action": self.join(claim, action=None),
                 "evaluator record empty": self.join(claim, expected={}),
                 "evaluator record without the policy scope": self.join(claim, expected=partial),
                 "evaluator sources are the same": self.join(claim, expected=dict(self.EXPECTED,
                                                                                  benign_source="10.42.0.10")),
                 "evaluator TTL is not an integer": self.join(claim, expected=dict(self.EXPECTED, ttl_s="180")),
                 "reference is not a digest": self.join(dict(claim, boutique_probe_ref="probe-7"))}
        digest = claim["blocked_source_ref"].split(":")[1]
        (Path(self.tmp.name) / (digest + ".json")).write_bytes(b'{"status": 403}')
        cases["bytes changed after naming"] = self.join(claim)
        (Path(self.tmp.name) / (claim["enforcement_point"].split(":")[1] + ".json")).unlink()
        cases["file removed"] = self.join(claim)
        for name, row in cases.items():
            with self.subTest(name=name):
                self.assertEqual(("UNVERIFIED", []), (row["status"], row["failed"]))
                self.assertTrue(row["missing"])
        self.assertIn("blocked_source_probe:ARTIFACT_DIGEST_MISMATCH", cases["bytes changed after naming"]["missing"])
        self.assertIn("policy:ARTIFACT_MISSING", cases["file removed"]["missing"])

    def test_readiness_m12_b0_is_a_control_and_bounds_keep_unknown_apart(self):
        control = self.join(self.claim(blocked_source_probe={"status": 200, "error": None, "action_ids": []}),
                            action=None, group="B0")
        self.assertEqual(("CONTROL", False), (control["status"], control["same_source_blocked"]))
        self.assertEqual(("CONTROL", None), tuple(self.join(None, group="B0")[key]
                                                  for key in ("status", "same_source_blocked")))
        rows = [self.join(self.claim()), self.join(self.claim(boutique_probe={"ok": False})),
                self.join(None), control]
        self.assertEqual({"status": "UNVERIFIED", "N": 3, "numerator": 1, "unknown": 1,
                          "bounds": [0.333333, 0.666667]}, containment_join.summarize(rows))


    def test_readiness_m12_h_artifact_writer_round_trips_and_refuses_corruption(self):
        document = {
            "run_id": self.RUN, "trial_id": self.TRIAL, "kind": "boutique_probe",
            "clock_id": "h-probe", "observed_at": "2026-11-12T00:00:10.000Z",
            "flow": "checkout", "ok": True,
        }
        scope = {"run_id": self.RUN, "trial_id": self.TRIAL}
        ref = containment_join.write_artifact(self.tmp.name, document, **scope)
        self.assertEqual(ref, containment_join.write_artifact(self.tmp.name, document, **scope))
        self.assertEqual((document, None), containment_join.read_artifact(
            self.tmp.name, ref, kind="boutique_probe", **scope))
        before = set(Path(self.tmp.name).iterdir())
        self.assertEqual(1, len(before))
        for bad in (dict(document, observed_at="2026-02-30T00:00:00.000Z"),
                    dict(document, trial_id=new_id("trl")), dict(document, ok=1)):
            with self.assertRaises(ValueError):
                containment_join.write_artifact(self.tmp.name, bad, **scope)
        self.assertEqual(before, set(Path(self.tmp.name).iterdir()))
        invalid_response = {
            "run_id": self.RUN, "trial_id": self.TRIAL, "kind": "blocked_source_probe",
            "clock_id": "h-probe", "observed_at": document["observed_at"],
            "source": self.EXPECTED["source"], "fixture_uid": self.EXPECTED["fixture_uid"],
            "status": 0, "error": "NO_RESPONSE", "action_ids": [],
        }
        with self.assertRaises(ValueError):
            containment_join.write_artifact(self.tmp.name, invalid_response, **scope)
        self.assertEqual(before, set(Path(self.tmp.name).iterdir()))
        path, = before
        path.write_bytes(b"changed")
        with self.assertRaises(ValueError):
            containment_join.write_artifact(self.tmp.name, document, **scope)
        self.assertEqual(b"changed", path.read_bytes())

    def test_readiness_m12_b0_requires_the_pinned_source_fixture_and_flow(self):
        claim = self.claim()
        claim = {key: claim[key] for key in ("blocked_source_ref", "boutique_probe_ref")}
        good = self.join(claim, action=None, group="B0")
        self.assertEqual(("CONTROL", True, True, []),
                         (good["status"], good["same_source_blocked"], good["boutique_ok"], good["missing"]))
        for changes in ({"source": "10.42.0.99"}, {"fixture_uid": "other-fixture"}):
            with self.subTest(changes):
                bad = self.join(self.claim(blocked_source_probe=changes), action=None, group="B0")
                self.assertIsNone(bad["same_source_blocked"])
                self.assertIn("blocked_source_probe:CONTROL_SCOPE_MISMATCH", bad["missing"])
        for status in (-1, 0, 600):
            with self.subTest(status=status):
                claim = self.claim(blocked_source_probe={"status": status})
                document, _ = containment_join.read_artifact(
                    self.tmp.name, claim["blocked_source_ref"], kind="blocked_source_probe",
                    run_id=self.RUN, trial_id=self.TRIAL)
                self.assertIsNone(document)
                self.assertIsNone(self.join(claim, action=None, group="B0")["same_source_blocked"])
                self.assertEqual("UNVERIFIED", self.join(claim)["status"])
        bad = self.join(self.claim(boutique_probe={"flow": "wrong"}), action=None, group="B0")
        self.assertIsNone(bad["boutique_ok"])
        self.assertIn("boutique_probe:CONTROL_FLOW_MISMATCH", bad["missing"])

    def test_readiness_m12_join_is_not_wired_into_the_formal_scorer(self):
        package = ROOT / "agent-orchestrator" / "measurement"
        for name in ("metrics.py", "scorer.py", "formal.py", "__main__.py"):
            self.assertNotIn("containment_join", (package / name).read_text(encoding="utf-8"), name)
        self.assertNotIn("time", {name for name in vars(containment_join) if not name.startswith("_")})


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for case in (B2Flow, ContainmentJoin):
        for name in loader.getTestCaseNames(case):
            if name.startswith("test_readiness"):
                suite.addTest(case(name))
    return suite
