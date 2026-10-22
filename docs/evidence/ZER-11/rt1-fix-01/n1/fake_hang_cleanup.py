"""N1, deterministic: one ZER-10 boutique transaction through the suite's FakeCluster.http, with the fault
(target hangs) landing right after add_to_cart, i.e. while the probe owns the cart. The transaction then
times out and Flow.cleanup sends POST /cart/empty with a live (callable) deadline. Run on a tree whose suite
has the old fake: TypeError escapes (the probe dies); on the fixed fake: a TIMEOUT failure and a cleanup
result. Offline: loopback fake Boutique only.
    python -B fake_hang_cleanup.py <tree> <out.json>"""
import json
import sys
import tempfile
import time
import traceback
from pathlib import Path

tree, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
sys.path[:0] = [str(tree / "agent-orchestrator"), str(tree / "infrastructure/scripts"), str(tree / "tests")]
import r1_baseline_runtime as rt  # noqa: E402
import test_dashboard_baseline_runtime as suite  # noqa: E402
from measurement.flows import Flow, Memory, boutique_spec  # noqa: E402

server, cls, origin = suite.serve(suite.Boutique)
result = {"tree": str(tree)}
try:
    with tempfile.TemporaryDirectory() as tmp:
        cluster = suite.FakeCluster(tmp, origin, after_fault="hang")
        time.sleep(0.2)  # the fake's initial frontend pod is Ready 50 ms after it is made
        seen = []

        def http(url, method="GET", headers=(), body=b"", deadline_ns=0, cancel=None, **kw):
            seen.append({"method": method, "path": url[len(origin):], "deadline": "callable" if callable(deadline_ns) else "number"})
            answer = cluster.http(url, method, headers, body, deadline_ns, cancel, **kw)
            if method == "POST" and url.endswith("/cart") and cluster.fault_at is None:
                cluster.fault_at = time.monotonic()  # the fault lands right after the cart is filled
            return answer

        flow = Flow(boutique_spec(rt.EXEC["product"], rt.EXEC["product_marker"], rt.FORM), origin, [origin])
        now = time.perf_counter_ns()
        live = lambda: now + int(5e9)  # the runner's live stop bound (ProbeRunner.stop_deadline), here fixed
        try:
            r = flow.run(now + int(2e9), None, Memory(), http=http, step_s=1, cleanup_ns=now + int(4e9), grace_s=2, stop_deadline=live)
            result.update(outcome="sample", ok=r["ok"], detail=r["detail"], reason=r["reason"], cleanup=r["cleanup"])
        except Exception as error:
            result.update(outcome="exception", error=type(error).__name__, where=traceback.format_exc().strip().splitlines()[-3:])
        result["requests"] = seen
finally:
    suite.stop(server)
out.write_text(json.dumps(result, indent=1) + "\n")
print(json.dumps({k: result.get(k) for k in ("outcome", "error", "detail", "reason", "cleanup")}))
