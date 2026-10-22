"""N1 instrumentation: run the H-RT1 suite in this tree with timing wrappers around the production gateway's
submit, the archive's append+fsync and the client's HttpHSink.deliver. Source files are not changed; the
wrappers only time and record. Usage: python -B n1_run.py <tree> <timings.jsonl> [test names...]"""
import json
import sys
import threading
import time
import unittest

tree, out = sys.argv[1], sys.argv[2]
sys.path[:0] = [tree + "/agent-orchestrator", tree + "/infrastructure/scripts", tree + "/tests"]
from event_pipeline import gateway as gw, store  # noqa: E402
from measurement import sink  # noqa: E402

log, lock, current = open(out, "a"), threading.Lock(), {"test": None}


def rec(**k):
    k.update(test=current["test"], wall=time.time())
    with lock:
        log.write(json.dumps(k) + "\n")
        log.flush()


submit = gw.Gateway.submit
def timed_submit(self, event, source, request_id, raw=None, error=None):
    t = time.perf_counter()
    outcome = "ok"
    try:
        return submit(self, event, source, request_id, raw=raw, error=error)
    except Exception as e:
        outcome = type(e).__name__
        raise
    finally:
        rec(kind="submit", plane=self.archive.plane, type=event.get("event_type") if isinstance(event, dict) else None,
            source=source, outcome=outcome, ms=round((time.perf_counter() - t) * 1000, 2))
gw.Gateway.submit = timed_submit

append = store.Archive.append
def timed_append(path, record):
    t = time.perf_counter()
    try:
        return append(path, record)
    finally:
        rec(kind="append", file=str(path)[-24:], ms=round((time.perf_counter() - t) * 1000, 2))
store.Archive.append = staticmethod(timed_append)

deliver = sink.HttpHSink.deliver
def timed_deliver(self, event, deadline_ns=None):
    t = time.perf_counter_ns()
    from measurement.flows import deadline_value
    left = None if deadline_ns is None else round((deadline_value(deadline_ns) - t) / 1e6, 1)
    outcome = None
    try:
        state = deliver(self, event, deadline_ns)
        outcome = state[0]
        return state
    except Exception as e:
        outcome = type(e).__name__ + ":" + str(e)[:60]
        raise
    finally:
        rec(kind="deliver", type=event.get("event_type"), source=event.get("source_component"), outcome=outcome,
            ms=round((time.perf_counter_ns() - t) / 1e6, 2), budget_ms=left)
sink.HttpHSink.deliver = timed_deliver

import test_dashboard_baseline_runtime as suite  # noqa: E402


class Result(unittest.TextTestResult):
    def startTest(self, test):
        current["test"] = test.id().split(".", 1)[1]
        rec(kind="start")
        super().startTest(test)

    def stopTest(self, test):
        rec(kind="stop")
        super().stopTest(test)


names = sys.argv[3:]
loader = unittest.TestLoader()
tests = loader.loadTestsFromNames(names, suite) if names else loader.loadTestsFromModule(suite)
result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(tests)
rec(kind="summary", run=result.testsRun, failures=[t.id() for t, _ in result.failures], errors=[t.id() for t, _ in result.errors])
sys.exit(0 if result.wasSuccessful() else 1)
