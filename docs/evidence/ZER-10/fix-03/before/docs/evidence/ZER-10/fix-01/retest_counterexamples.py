"""fix-01 retest of every Codex counterexample (docs/evidence/ZER-10/codex-review/), offline.

  python -B docs/evidence/ZER-10/fix-01/retest_counterexamples.py [--output FILE]

The four Codex scripts are executed unchanged as subprocesses where they still run. Two diagnostic
lines of probe/counterexamples.py assume the old behaviour (a sample is always emitted; the H sink
returns a status instead of raising) and would stop the script under the fix; that script is
executed from its own source with exactly those two lines adapted (ADAPTATIONS below). The Codex
files are only read. Expected values are the ones the review states; each check prints actual/expected.
Fake servers are loopback ones the scripts create; nothing else is contacted.
"""
import argparse
import json
from pathlib import Path
# Fixed interpreter and fixed in-repo scripts, list arguments, no shell, no external input (B404/B603).
import subprocess  # nosec B404
import sys

ROOT = Path(__file__).resolve().parents[4]
REVIEW = ROOT / "docs/evidence/ZER-10/codex-review"
ADAPTATIONS = [
    ("'sample_latency_ms':samples(sink)[0]['payload']['latency_ms']",
     "'sample_latency_ms':(samples(sink)[0]['payload']['latency_ms'] if samples(sink) else None)",
     "a run-cap cut sample is no longer emitted"),
    ("status=HttpHSink(", "status=_refused(HttpHSink(", "the sink now raises SinkRefused on a redirect"),
    (".deliver({'event_id':'evt_synthetic'})", ".deliver)({'event_id':'evt_synthetic'})", "same line, closing the wrapper"),
]
PRELUDE = '''
def _refused(deliver):
    def call(event):
        try:
            return deliver(event)
        except Exception as error:  # SinkRefused and friends: report, as the fixed sink does
            return ["REFUSED", type(error).__name__, str(error)]
    return call
'''


def run_script(name):
    out = subprocess.run([sys.executable, "-B", str(REVIEW / name)], cwd=ROOT, capture_output=True, text=True, timeout=600)  # nosec B603
    if out.returncode:
        raise SystemExit(f"{name} failed:\n{out.stderr[-2000:]}")
    return json.loads(out.stdout)


def run_probe_script():
    source = (REVIEW / "probe/counterexamples.py").read_text(encoding="utf-8")
    for old, new, _ in ADAPTATIONS:
        if source.count(old) != 1:
            raise SystemExit(f"adaptation anchor not found exactly once: {old}")
        source = source.replace(old, new)
    first_newline = source.index("\n") + 1  # keep the original imports first
    source = source[:first_newline] + PRELUDE + source[first_newline:]
    out = subprocess.run([sys.executable, "-B", "-c", source.replace("Path(__file__)", f"Path({str(REVIEW / 'probe/counterexamples.py')!r})")],
                         cwd=ROOT, capture_output=True, text=True, timeout=600)  # nosec B603
    if out.returncode:
        raise SystemExit(f"probe/counterexamples.py (adapted) failed:\n{out.stderr[-2000:]}")
    return json.loads(out.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output")
    args = parser.parse_args()
    sp = run_script("scorer-probes.py")
    ce = run_script("metrics/counterexamples.py")
    ex = run_script("metrics/extra.py")
    pr = run_probe_script()
    kp = lambda case: sp[case]["kpi"]
    inc = lambda case, i=0: sp[case]["incidents"][i]
    checks = [
        ("ZR10-01", "mixed_invalid_request requested/N", (kp("mixed_invalid_request")["counts"]["requested"], kp("mixed_invalid_request")["counts"]["N"]), (2, 2)),
        ("ZR10-01", "mixed_invalid_request MTTD verdict", kp("mixed_invalid_request")["mttd"]["verdict"], "UNKNOWN"),
        ("ZR10-01", "invalid_request requested/status (not EMPTY)", (kp("invalid_request")["counts"]["requested"], kp("invalid_request")["counts"]["status"]), (1, "OK")),
        ("ZR10-01", "invalid_request label", inc("invalid_request")["label"], "MISSING"),
        ("ZR10-02", "detector_unsynced label/mttd/total", (inc("detector_unsynced")["label"], inc("detector_unsynced")["mttd"], inc("detector_unsynced")["total"]), ("MISSING", "MISSING", 90.0)),
        ("ZR10-02", "detector_unsynced CLOCK_UNVERIFIED flag", "CLOCK_UNVERIFIED" in inc("detector_unsynced")["flags"], True),
        ("ZR10-02", "detector_unsynced MTTD verdict", kp("detector_unsynced")["mttd"]["verdict"], "UNKNOWN"),
        ("control", "clean E01 MTTD/MTTR verdicts", (kp("clean")["mttd"]["verdict"], kp("clean")["mttr_120"]["verdict"]), ("PASS", "PASS")),
        ("common cause", "negative_latency label", inc("negative_latency")["label"], "MISSING"),
        ("ZR10-03", "different_episode_keys episodes, per hour",
         (ce["different_episode_keys"]["actual"]["episodes_observed"], ce["different_episode_keys"]["actual"]["episodes_per_hour"]), (2, 25.899281)),
        ("ZR10-03", "all_slots_hit_without_coverage episodes/h, verdict",
         (ce["all_slots_hit_without_coverage"]["actual"]["episodes_per_hour"], ce["all_slots_hit_without_coverage"]["actual"]["verdict"]), (None, "UNKNOWN")),
        ("ZR10-03", "all_slots_hit_without_coverage slot bounds", ce["all_slots_hit_without_coverage"]["actual"]["bounds"], [1.0, 1.0]),
        ("ZR10-04", "started_action_no_terminal executed / terminal MISSING",
         (ce["started_action_no_terminal"]["actual"]["M6_actions_observed"], ce["started_action_no_terminal"]["actual"]["M6_terminal"]["MISSING"]), (1, 1)),
        ("B0 note", "b0_detector_off M5/M6", (ce["b0_detector_off"]["actual"]["M5"]["status"], ce["b0_detector_off"]["actual"]["M6"]["status"]), ("N/A", "N/A")),
        ("ZR10-05", "llm_decision_with_no_call_records status", ce["llm_decision_with_no_call_records"]["actual"]["status"], "MISSING"),
        ("ZR10-05", "invalid_second_llm_call raw records/coverage/usage/cost",
         tuple(ce["invalid_second_llm_call"]["actual"][k] for k in ("raw_call_records", "call_coverage_status", "usage_status", "cost_status")),
         (2, "MISSING", "MISSING", "MISSING")),
        ("ZR10-05", "invalid_second_llm_call cost lower bound",
         next(iter(ce["invalid_second_llm_call"]["actual"]["by"]["run"].values()))["usd"], 0.01),
        ("ZR10-06", "malformed_gt_constraint: no exception, outcome",
         ("actual_exception" in ex["malformed_gt_constraint"], ex["malformed_gt_constraint"].get("actual", {}).get("rows", [{}])[0].get("outcome")), (False, "UNKNOWN_GT")),
        ("ZR10-07", "conflicting_guard_verdicts accept_correct/conflicts",
         (ex["conflicting_guard_verdicts"]["actual_M3"]["accept_correct"], ex["conflicting_guard_verdicts"]["actual_M3"]["conflicting_verdicts"]), (0, 1)),
        ("ZR10-07", "same result in reversed ingest order", ex["conflicting_guard_reversed"]["actual_M3"], ex["conflicting_guard_verdicts"]["actual_M3"]),
        ("ZR10-08", "duplicate_cart pass", pr["duplicate_cart"]["pass"], False),
        ("ZR10-09", "step_timeout pass/home ms < 200", (pr["step_timeout"]["pass"], pr["step_timeout"]["home_ms"] < 200), (False, True)),
        ("ZR10-09", "max_duration samples/cancelled/stop", (pr["max_duration"]["summary"]["samples"], pr["max_duration"]["summary"]["cancelled"],
                                                           pr["max_duration"]["summary"]["stop_reason"]), (0, 1, "MAX_DURATION")),
        ("ZR10-09", "max_duration wall within cap + grace + 1 s", pr["max_duration"]["actual_s"] <= 0.2 + pr["max_duration"]["summary"]["grace_s"] + 1, True),
        ("ZR10-10", "fixture_stale_cleanup pre-existing kept / no DELETE",
         (pr["fixture_stale_cleanup"]["pre_existing_still_exists"], "DELETE" in [m for m, _ in pr["fixture_stale_cleanup"]["requests"]]), (True, False)),
        ("ZR10-10", "fixture_stale_cleanup cleanup", pr["fixture_stale_cleanup"]["cleanup"], {"order": "UNRESOLVED_OWNERSHIP"}),
        ("ZR10-10", "keyboard_interrupt_cleanup carts emptied / cleanup sent",
         (pr["keyboard_interrupt_cleanup"]["cart_sizes"], len(pr["keyboard_interrupt_cleanup"]["cleanup_requests"])), ([0], 1)),
        ("ZR10-11", "h_sink_redirect refused, nothing at the other origin",
         (pr["h_sink_redirect"]["status"][0], pr["h_sink_redirect"]["received_at_other_origin"]), ("REFUSED", [])),
        ("ZR10-N1", "other_input_output exit/created", (pr["other_input_output"]["exit"], pr["other_input_output"]["created_inside_other_export"]), (4, False)),
    ]
    rows = [{"finding": f, "check": c, "actual": a, "expected": e, "ok": a == e} for f, c, a, e in json.loads(json.dumps(checks))]
    report = {"script": "fix-01 retest of Codex counterexamples", "adaptations": [{"old": o, "new": n, "why": w} for o, n, w in ADAPTATIONS],
              "checks": rows, "passed": sum(r["ok"] for r in rows), "total": len(rows),
              "verdict": "ALL_EXPECTED" if all(r["ok"] for r in rows) else "MISMATCH"}
    text = json.dumps(report, indent=1, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    for r in rows:
        print(("ok  " if r["ok"] else "FAIL"), r["finding"], "-", r["check"], "| actual", json.dumps(r["actual"]), "| expected", json.dumps(r["expected"]))
    print(report["verdict"], f'{report["passed"]}/{report["total"]}')
    return 0 if report["verdict"] == "ALL_EXPECTED" else 1


if __name__ == "__main__":
    sys.exit(main())
