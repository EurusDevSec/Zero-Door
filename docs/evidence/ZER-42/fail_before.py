"""ZER-42 fail-before: targeted mutation checks for the easy-to-slip admission/validation boundaries.

For NEW capability there is no pre-change behaviour to regress against, so instead of a before-snapshot replay
this proves the new tests are not vacuous: each mutation flips exactly one load-bearing boundary in the source
and the one test that guards it must turn RED. Every file is read up front and restored in a finally block, so
an interruption cannot leave a mutated file behind. It runs no lab, no broker and no network. Offline.

    NEMESIS=<python> python -B docs/evidence/ZER-42/fail_before.py [results-dir]
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKER = ROOT / "chaos-worker"
PIN = os.environ.get("NEMESIS")
if not PIN:
    sys.exit("set NEMESIS to a production-pinned python.exe")

POLICY = ROOT / "chaos-worker/internal/guard/policy.go"
TARGET = ROOT / "chaos-worker/internal/validation/target.go"
GUARD = ROOT / "agent-orchestrator/nemesis/command_guard.py"
SQLI = ROOT / "chaos-worker/internal/attack/sqli.go"
RUNTIME = ROOT / "infrastructure/scripts/sqli_executor_runtime.py"


def go_test(pkg, run):
    return subprocess.run(["go", "test", "-count=1", pkg, "-run", run], cwd=WORKER,
                          capture_output=True, text=True).returncode


def py_test(selector=None):
    cmd = [PIN, "-B", str(ROOT / "tests/test_sqli_executor.py")]
    if selector:
        cmd.append(selector)
    return subprocess.run(cmd, capture_output=True, text=True).returncode


# (file, old, new, label, test) — old must occur exactly once; test() returns a nonzero code when RED.
MUTATIONS = [
    (POLICY, "if err != nil || endpoint != allowed {", "if err != nil || false {",
     "guard: drop SQLi endpoint exact-match", lambda: go_test("./internal/guard/", "TestAdmitSQLiRejections")),
    (POLICY, "if p.SQLi == nil || !p.SQLi.Enabled {", "if p.SQLi == nil || false {",
     "guard: SQLi capability no longer must be enabled", lambda: go_test("./internal/guard/", "TestAdmitSQLiRejections")),
    (TARGET, "u.Path != sqliSearchPath {", "false {",
     "validation: accept any path, not only the search path", lambda: go_test("./internal/validation/", "TestValidateSQLiEndpoint")),
    (GUARD, "type(template) is not str or template not in SQLI_TEMPLATE_IDS:", "type(template) is not str or False:",
     "nemesis: accept an unknown template id", lambda: py_test("SqliCommand.test_rejections")),
    (GUARD, "not isinstance(raw, str) or raw != raw.lower() or any(", "not isinstance(raw, str) or any(",
     "nemesis: drop the lowercase-endpoint parity guard", lambda: py_test("EndpointValidation.test_exact_endpoint_only")),
    # Codex review boundaries (ZR42-01..05).
    (SQLI, "if parsed.Results == nil || parsed.Count == nil || *parsed.Count < 0 || *parsed.Count != len(*parsed.Results) {",
     "if false {", "executor: drop the 200-response schema check (ZR42-02)",
     lambda: go_test("./internal/attack/", "TestSQLiExecutorRejectsMalformed200")),
    (SQLI, "nextAt = sendStart.Add(interval) // schedule the next send from this dispatch, not from a fixed ticker",
     "nextAt = sendStart // schedule the next send from this dispatch, not from a fixed ticker",
     "executor: drop send pacing so sends can burst (ZR42-03)",
     lambda: go_test("./internal/attack/", "TestSQLiExecutorPacingNeverBurstsAfterSlowResponse")),
    (SQLI, "if !isPrivateClusterIP(ip) {", "if false {",
     "executor: drop the private-peer preflight (ZR42-04)",
     lambda: go_test("./internal/attack/", "TestSQLiExecutorPeerCheck")),
    (TARGET, "!sqliIngressHost.MatchString(u.Hostname()) || u.Hostname() == sqliFixtureHost ||",
     "!sqliIngressHost.MatchString(u.Hostname()) || false ||",
     "validation: accept the fixture Service directly (ZR42-04)",
     lambda: go_test("./internal/validation/", "TestValidateSQLiEndpoint")),
    (RUNTIME, "and times[0] - t_req <= gap and end - times[-1] <= gap \\",
     "and times[0] - t_req <= gap and True \\",
     "evaluator: drop the window end-coverage check (ZR42-01)",
     lambda: py_test("EffectEvaluator.test_single_clean_sample_does_not_cover_a_long_window")),
    (RUNTIME, "effect = build_event(context, payload, clock, causation_id=fault[\"event_id\"])",
     "effect = build_event(context, payload, clock)",
     "evaluator: drop the fault->effect causation link (ZR42-05)",
     lambda: py_test("EmitEvidence.test_entrypoint_emits_two_linked_events")),
]


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "scratch/zer42/claude/fail-before"
    out.mkdir(parents=True, exist_ok=True)
    # Read and restore BYTES, so newline translation can never rewrite the files.
    originals = {p: p.read_bytes() for p in {POLICY, TARGET, GUARD, SQLI, RUNTIME}}
    lines, ok = [], True
    try:
        for path, old, new, label, test in MUTATIONS:
            raw = originals[path]
            old_b, new_b = old.encode("utf-8"), new.encode("utf-8")
            if raw.count(old_b) != 1:
                lines.append(f"SETUP-ERROR | {label} | anchor not unique ({raw.count(old_b)})")
                ok = False
                continue
            try:
                path.write_bytes(raw.replace(old_b, new_b))
                code = test()
            finally:
                path.write_bytes(raw)  # restore immediately
            red = code != 0
            ok = ok and red
            lines.append(f"{'RED (caught)' if red else 'GREEN (MISS!)'} | {label} | test rc={code}")
    finally:
        for p, raw in originals.items():
            p.write_bytes(raw)  # belt-and-braces restore

    # After restore, the real suites must be green again.
    green_go = go_test("./internal/...", ".")
    green_py = py_test()
    lines.append(f"restored-green | go ./internal/... rc={green_go} | python test_sqli_executor rc={green_py}")
    ok = ok and green_go == 0 and green_py == 0

    report = "\n".join(lines) + "\n"
    (out / "fail-before.txt").write_text(report, encoding="utf-8")
    print(report, end="")
    print("OVERALL", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
