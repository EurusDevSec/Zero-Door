"""Independent business probe (ZER-38): fixed-cadence samples written to the H plane only.

Cadence runs on a monotonic counter; t_start is read from the probe clock and t_end = t_start +
elapsed, so t_end >= t_start always and latency is monotonic. Overrun skips slots instead of
bursting; a cancelled transaction is journaled but never emitted as pass or fail; a dead probe,
skipped slot or lost sample shows as a sequence/time gap the scorer counts as unobserved (U).
Budgets (duration, samples, requests) are hard stops. Healer state is never read.
"""
import hashlib
import threading
import time

from event_pipeline.contract import Producer, canonical

from . import VERSION
from .clock import cristian, stamp
from .flows import ERROR_CLASS, Memory
from .sink import PersistenceFailure, SinkRefused, SinkUnauthorized

DETAIL_SCHEMA = "zd-probe-detail/0"


class ProbeRunner:
    def __init__(self, plan, flow, context, clock, publisher, journal=None, reference=None, cancel=None,
                 http=None, target=None, start_sequence=0):
        self.plan, self.flow, self.clock, self.publisher = plan, flow, clock, publisher
        self.context = {k: context[k] for k in ("run_id", "trial_id", "group", "method_version", "config_ref")}
        self.journal = journal if journal is not None else []
        self.reference, self.http = reference, http
        self.cancel = cancel or threading.Event()
        probe = plan["probe"]
        self.probe_id, self.probe_version, self.flow_name = probe["probe_id"], probe["probe_version"], probe["flow"]
        if flow.spec["flow"] != self.flow_name:
            raise ValueError("plan flow and flow spec differ")
        spec_hash = hashlib.sha256(canonical(flow.spec)).hexdigest()[:16]
        self.producer = Producer("probe", f"{VERSION}+{flow.spec['spec_version']}+{spec_hash}", clock.envelope())
        self.target = target or {"namespace": None, "service": None, "flow": self.flow_name}
        self.sequence = start_sequence
        self.memory = Memory()
        self.interrupted = False
        self.counts = {"samples": 0, "pass": 0, "fail": 0, "skipped_slots": 0, "cancelled": 0, "requests": 0,
                       "clock_sync_failed": 0, "heartbeats": 0}

    def registration(self):
        """Entry for TRIAL_STARTED.payload.probes (contract 5.3)."""
        return {"probe_id": self.probe_id, "flow": self.flow_name, "probe_version": self.probe_version,
                "clock_id": self.clock.clock_id}

    def emit(self, typ, payload):
        # ts_event is read from the probe clock too, so every probe timestamp belongs to clock_id.
        event = self.producer.event(self.context, typ, payload, "h.probe", target=self.target,
                                    ts_event=stamp(self.clock.now_ms()))
        self.publisher.put(event)
        return event

    def note(self, kind, **fields):
        self.journal.append(dict(kind=kind, at=stamp(self.clock.now_ms()), **fields))

    def heartbeat(self):
        self.counts["heartbeats"] += 1
        self.emit("PROBE_HEARTBEAT", {"probe_id": self.probe_id, "flow": self.flow_name,
                                      "last_sequence": self.sequence - 1 if self.sequence else None,
                                      "probe_version": self.probe_version})

    def sync(self):
        if self.reference is None:
            return
        try:
            payload = cristian(self.clock, self.reference, self.plan["clock_sync"]["method"])
        except Exception as error:  # an unreachable reference leaves the clock unverified, never offset 0
            self.counts["clock_sync_failed"] += 1
            self.note("CLOCK_SYNC_FAILED", error=type(error).__name__)
            return
        self.emit("CLOCK_SYNC", payload)

    def sample(self, stop_ns=None):
        """One transaction. `stop_ns` is the run's workload cap: a transaction it cuts is cancelled."""
        timeouts = self.plan["timeouts"]
        started_ms, started_ns = self.clock.now_ms(), time.perf_counter_ns()
        deadline = started_ns + int(timeouts["transaction_s"] * 1e9)
        kwargs = {"http": self.http} if self.http else {}
        # Cleanup after the cap is bounded by the declared grace (budget.grace_s), not by the cap itself.
        cleanup_ns = None if stop_ns is None else stop_ns + int(self.plan["budget"]["grace_s"] * 1e9)
        result = self.flow.run(deadline, self.cancel, self.memory, step_s=timeouts["step_s"], stop_ns=stop_ns,
                               cleanup_ns=cleanup_ns, **kwargs)
        self.counts["requests"] += result["requests"]
        if result["detail"] == "CANCELLED":
            # Unknown outcome: journal it, consume no sequence, emit nothing.
            self.counts["cancelled"] += 1
            self.note("SAMPLE_CANCELLED", t_start=stamp(started_ms), requests=result["requests"], cleanup=result["cleanup"],
                      reason=result["reason"])
            if result["interrupted"]:
                self.cancel.set()  # an interrupt stops the run; the bounded cleanup above already ran
                self.interrupted = True
            return None
        latency = round(result["elapsed_ms"], 3)
        detail = result["detail"]
        if result["ok"] and latency > self.plan["f01"]["l_ms"]:
            detail = "SLOW"
        passed = result["ok"] and detail is None
        t_start = stamp(started_ms)
        t_end = stamp(started_ms + result["elapsed_ms"])  # result known before cleanup
        payload = {
            "probe_id": self.probe_id, "flow": self.flow_name, "sequence": self.sequence,
            "t_start": t_start, "t_end": t_end, "pass": passed,
            "error_class": None if passed else ERROR_CLASS[detail], "latency_ms": latency,
            "probe_version": self.probe_version,
            # Additive detail (MINOR proposal, docs/design/r1-measurement.md); 1.0.0 consumers ignore it.
            "detail": {"schema": DETAIL_SCHEMA, "detail_class": detail, "reason": result["reason"] if detail != "SLOW" else "LATENCY_ABOVE_L",
                       "steps": result["steps"], "requests": result["requests"], "cleanup": result["cleanup"],
                       "captures": result["captures"], "spec_version": self.flow.spec["spec_version"],
                       "provenance": self.flow.spec["provenance"]},
        }
        self.sequence += 1
        self.counts["samples"] += 1
        self.counts["pass" if passed else "fail"] += 1
        return self.emit("PROBE_SAMPLE", payload)

    def run(self):
        """Run until cancel, interrupt or a budget stop; returns a summary. Raises nothing for service errors.

        max_duration_s caps the workload: a transaction it cuts is cancelled (journaled, not emitted).
        After the cap only bounded work remains, within budget.grace_s: the cut sample's cleanup, a last
        heartbeat/sync and delivery of the outbox (what is left stays pending there, never dropped).
        """
        f01, budget = self.plan["f01"], self.plan["budget"]
        period = int(f01["delta_s"] * 1e9)
        start = time.perf_counter_ns()
        cap = start + int(budget["max_duration_s"] * 1e9)
        stop_reason = "CANCELLED"
        last_beat = last_sync = start
        slot = 0
        try:
            self.sync()
            self.heartbeat()
            while not self.cancel.is_set():
                now = time.perf_counter_ns()
                if now >= cap:
                    stop_reason = "MAX_DURATION"
                    break
                if self.counts["samples"] >= budget["max_samples"]:
                    stop_reason = "MAX_SAMPLES"
                    break
                if self.counts["requests"] + self.flow.per_sample_requests > budget["max_requests"]:
                    stop_reason = "MAX_REQUESTS"
                    break
                target = start + slot * period
                if now > target + period:
                    # Overrun: skip the missed slots; the gap stays visible to the scorer.
                    missed = (now - target) // period
                    slot += missed
                    self.counts["skipped_slots"] += missed
                    self.note("SLOTS_SKIPPED_OVERRUN", slots=int(missed))
                    continue
                if now < target:
                    if self.cancel.wait((target - now) / 1e9):
                        break
                    continue
                slot += 1
                self.sample(stop_ns=cap)
                if self.interrupted:
                    break
                now = time.perf_counter_ns()
                if now - last_beat >= self.plan["heartbeat_s"] * 1e9:
                    self.heartbeat()
                    last_beat = now
                if self.reference is not None and now - last_sync >= self.plan["clock_sync"]["interval_s"] * 1e9:
                    self.sync()
                    last_sync = now
                self.publisher.flush(max_attempts=1, deadline_ns=cap)
        except PersistenceFailure as error:
            self.note("PERSISTENCE_FAILED", error=str(error))
            return self.summary("PERSISTENCE_FAILED", start)
        except SinkRefused as error:
            return self.refused(error, start)
        except KeyboardInterrupt:
            self.interrupted = True  # outside a transaction (waiting, emitting): same bounded wind-down
        if self.interrupted:
            self.cancel.set()
            self.note("INTERRUPTED")
            stop_reason = "INTERRUPTED"
        # One grace window: from the cap when the cap stopped the run (the cut sample's cleanup used part of
        # it already), else from now. Wall time is bounded by max_duration_s + grace_s + one H request timeout.
        stopped_at = cap if time.perf_counter_ns() >= cap else time.perf_counter_ns()
        grace_end = stopped_at + int(budget["grace_s"] * 1e9)
        try:
            self.heartbeat()
            if not self.interrupted:
                self.sync()
            self.publisher.flush(max_attempts=3, deadline_ns=grace_end)
        except PersistenceFailure as error:
            self.note("PERSISTENCE_FAILED", error=str(error))
            return self.summary("PERSISTENCE_FAILED", start)
        except SinkRefused as error:
            return self.refused(error, start)
        return self.summary(stop_reason, start)

    def refused(self, error, start):
        """The H write was refused (identity, redirect, foreign ACK): stop; events stay in the outbox."""
        unauthorized = isinstance(error, SinkUnauthorized)
        self.note("SINK_UNAUTHORIZED" if unauthorized else "SINK_REFUSED", reason=str(error))
        return self.summary("SINK_UNAUTHORIZED" if unauthorized else "SINK_REFUSED", start)

    def summary(self, stop_reason, start=None):
        out = dict(self.counts, stop_reason=stop_reason, undelivered=len(self.publisher.outbox.pending),
                   delivery=dict(self.publisher.counts), registration=self.registration(),
                   max_duration_s=self.plan["budget"]["max_duration_s"], grace_s=self.plan["budget"]["grace_s"])
        if start is not None:
            out["wall_s"] = round((time.perf_counter_ns() - start) / 1e9, 3)
        return out
