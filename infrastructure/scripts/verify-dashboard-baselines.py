"""ZER-11 / ZER-39 dashboard and baseline verification.

  --help             this text; opens no connection
  offline            run the dashboard/mode/profile suites and a sealed fixture end to end
                     (stdlib + the agents' test deps; loopback fakes only; no cluster, Docker or model)
  fixture-server     serve the real Nemesis app on 127.0.0.1 with SYNTHETIC registered results, for a
                     local browser check (no Kafka consumer, no Prometheus, no model)
  register           add a closed run's output/1 directory to <root>/registry.json after checking that
                     its CSVs equal measurement.output of its score.json
  serve-results      serve an existing results root (a real run's registered artifacts) read-only on
                     127.0.0.1: only the results page and GET /api/results/*; no fixture is generated,
                     no Kafka consumer starts and no Prometheus/Hephaestus/model route is reachable;
                     the root's file hashes are compared at exit
  plan-check         print the G-ZER11-RT1 phase/budget matrix and check its arithmetic against the
                     scorer's coverage rules (offline; the runbook quotes these numbers)
  runtime-preflight  RUNTIME, read-only kubectl inventory for the approved plan; refuses without
                     --runtime-approval and never applies, scales, deletes or injects anything
  rt1                H-RT1 harness (r1_baseline_runtime.py). Without --execute: print the exact
                     phase/write/rollback matrix, probe budgets and image (offline). With --execute,
                     --runtime-approval <ref> and --context k3d-zero-door: RUNTIME, runs P0-P7 then P8.
                     The flag records an approval given elsewhere; it grants nothing by itself
  rt1-score          P8 again, offline: score pulled H/O exports with the ZER-10 CLI and register them

The runtime plan itself is docs/runbooks/dashboard-and-baselines.md.
"""
import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
# subprocess runs fixed argv lists only, never through a shell.
import subprocess  # nosec B404
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEMESIS = ROOT / "agent-orchestrator/nemesis"
RESULTS_PAGES = {"/dashboard/results.html", "/dashboard/results.js"}
SUITES = ["tests/test_dashboard_measurement.py", "tests/test_dashboard_modes.py", "tests/check_r1_baselines.py",
          "tests/test_command_modes.py", "tests/test_command_guard_integration.py", "tests/test_event_agents.py",
          "tests/test_dashboard_baseline_runtime.py"]


def offline(args):
    results = {}
    for suite in SUITES:
        started = time.monotonic()
        done = subprocess.run([sys.executable, "-B", suite], cwd=ROOT, capture_output=True, text=True, timeout=600)  # nosec B603
        tail = (done.stdout + done.stderr).strip().splitlines()[-1:] or [""]
        results[suite] = {"exit": done.returncode, "last_line": tail[0], "seconds": round(time.monotonic() - started, 1)}
    print(json.dumps({"python": sys.version.split()[0], "results": results}, indent=1, sort_keys=True))
    return 0 if all(r["exit"] == 0 for r in results.values()) else 1


def build_fixture_root(root, cases=None):
    """Score the SYNTHETIC ZER-11 cases with the ZER-10 CLI and register them under `root`."""
    sys.path.insert(0, str(ROOT / "agent-orchestrator"))
    sys.path.insert(0, str(ROOT / "tests"))
    from test_dashboard_measurement import EXPECTED, score_case
    from nemesis.measurement_view import register
    runs = {}
    for name in cases or EXPECTED["cases"]:
        score_case(name, root)
        runs[name] = register(root, name)["run_id"]
    return runs


def fixture_server(args):
    import uvicorn
    work = Path(tempfile.mkdtemp(prefix="zd-zer11-fixture-"))
    root = work / "results"
    root.mkdir()
    runs = build_fixture_root(root)
    keys = work / "keys"
    keys.mkdir()
    reader = {"id": "fixture-reader", "purpose": "results-reader", "secret": "synthetic-results-reader-" + os.urandom(12).hex()}
    operator = {"id": "fixture-operator", "purpose": "operator", "secret": "synthetic-operator-" + os.urandom(12).hex()}
    (keys / "reader.json").write_text(json.dumps(reader))
    (keys / "operator.json").write_text(json.dumps(operator))
    os.environ.update({"ZD_RESULTS_ROOT": str(root), "ZD_RESULTS_TOKEN_FILE": str(keys / "reader.json"),
                       "ZD_OPERATOR_TOKEN_FILE": str(keys / "operator.json"), "ZD_EVENT_URL": "",
                       "OPENAI_API_KEY": "", "GEMINI_API_KEYS": "", "KAFKA_BOOTSTRAP_SERVERS": "127.0.0.1:9"})
    os.chdir(ROOT / "agent-orchestrator/nemesis")  # StaticFiles(directory="static")
    sys.path.insert(0, str(ROOT / "agent-orchestrator/nemesis"))
    import main as nemesis
    nemesis.app.router.on_startup.clear()  # no Kafka results consumer in the fixture server
    control = work / "control.json"
    control.write_text("{}")

    @nemesis.app.middleware("http")
    async def fixture_faults(request, call_next):
        # Browser-check knobs (SYNTHETIC): {"fail": true} answers 503 for run views;
        # {"delay": {"<run_id>": seconds}} delays that run's view to test a late answer after a switch.
        knobs = json.loads(control.read_text() or "{}")
        path = request.url.path
        if path.startswith("/api/results/runs/") and "/files/" not in path:
            delay = (knobs.get("delay") or {}).get(path.rsplit("/", 1)[-1])
            if delay:
                await asyncio.sleep(float(delay))
            if knobs.get("fail"):
                from fastapi.responses import JSONResponse
                return JSONResponse({"detail": "FIXTURE_UPSTREAM_DOWN"}, status_code=503)
        return await call_next(request)

    info = {"url": f"http://127.0.0.1:{args.port}/dashboard/results.html", "reader_key_file": str(keys / "reader.json"),
            "control_file": str(control), "runs": runs, "note": "SYNTHETIC fixture; loopback only"}
    (work / "fixture.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(dict(info, fixture=str(work / "fixture.json")), indent=1), flush=True)
    uvicorn.run(nemesis.app, host="127.0.0.1", port=args.port, log_level="warning")
    return 0


def register_cmd(args):
    sys.path.insert(0, str(ROOT / "agent-orchestrator"))
    from nemesis.measurement_view import ResultError, register
    try:
        entry = register(Path(args.root).resolve(), args.dir)
    except ResultError as error:
        print("REFUSED", error.reason, file=sys.stderr)
        return 3
    print(json.dumps(entry, sort_keys=True))
    return 0


def root_digest(root):
    """{relative path: sha256} of every regular file under the root (symlinks are listed, not followed)."""
    out = {}
    for base, dirs, files in os.walk(root):
        for name in sorted(dirs + files):
            path = Path(base) / name
            if path.is_symlink():
                out[path.relative_to(root).as_posix()] = "SYMLINK"
            elif path.is_file():
                out[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def results_app(root, reader_key_file, operator_key_file=None):
    """The real Nemesis app, restricted to the S results page and GET /api/results/*, over `root`.

    The root is used as given: nothing is scored, generated or registered here. Startup handlers
    (the Kafka results consumer) are removed and every other route answers 404 before reaching
    Nemesis code, so no Prometheus, Hephaestus, Kafka or model call can be made. Returns (app, runs)."""
    root = Path(root)
    if not root.is_absolute():
        raise SystemExit("REFUSED: --root must be an absolute path")
    sys.path.insert(0, str(ROOT / "agent-orchestrator"))
    from nemesis.measurement_view import ResultsStore
    runs = ResultsStore(root).runs()  # the registry must parse under the reader's own rules
    os.environ.update({"ZD_RESULTS_ROOT": str(root), "ZD_RESULTS_TOKEN_FILE": str(Path(reader_key_file).resolve()),
                       "ZD_EVENT_URL": "", "OPENAI_API_KEY": "", "GEMINI_API_KEYS": "",
                       "KAFKA_BOOTSTRAP_SERVERS": "127.0.0.1:9", "PROMETHEUS_URL": "http://127.0.0.1:9",
                       "HEPHAESTUS_URL": "http://127.0.0.1:9"})
    if operator_key_file:  # lets authorize_reader enforce KEY_SEPARATION against the run's operator key
        os.environ["ZD_OPERATOR_TOKEN_FILE"] = str(Path(operator_key_file).resolve())
    else:
        os.environ.pop("ZD_OPERATOR_TOKEN_FILE", None)
    spec = importlib.util.spec_from_file_location("zd_nemesis_results_only", NEMESIS / "main.py")
    nemesis = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nemesis)
    nemesis.app.router.on_startup.clear()
    from fastapi.responses import JSONResponse
    from fastapi.staticfiles import StaticFiles
    if not any(getattr(route, "path", None) == "/dashboard" for route in nemesis.app.routes):
        nemesis.app.mount("/dashboard", StaticFiles(directory=str(NEMESIS / "static")), name="dashboard")

    @nemesis.app.middleware("http")
    async def results_only(request, call_next):
        # Outermost: /api/results* goes on to Nemesis' own READ_ONLY and results-reader checks.
        path = request.url.path
        if path.startswith("/api/results") or (request.method == "GET" and path in RESULTS_PAGES):
            return await call_next(request)
        return JSONResponse({"detail": "NOT_SERVED_IN_RESULTS_MODE"}, status_code=404)

    return nemesis.app, runs


def serve_results(args):
    import uvicorn
    root = Path(args.root)
    if not root.is_absolute() or not root.is_dir():
        print("REFUSED: --root must be an existing absolute directory", file=sys.stderr)
        return 2
    if args.receipt and Path(args.receipt).exists():
        print("REFUSED: receipt exists; choose a new file", file=sys.stderr)
        return 4
    before = root_digest(root)
    sys.path.insert(0, str(ROOT / "agent-orchestrator"))
    from nemesis.measurement_view import ResultError
    try:
        app, runs = results_app(root, args.reader_key_file, args.operator_key_file)
    except ResultError as error:
        print("REFUSED", error.reason, file=sys.stderr)
        return 3
    digest = lambda d: hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()
    info = {"url": f"http://127.0.0.1:{args.port}/dashboard/results.html", "root": str(root),
            "runs": [r["run_id"] for r in runs], "registry_sha256": before.get("registry.json"),
            "root_files": len(before), "root_digest": digest(before), "note": "read-only; results page and GET /api/results only"}
    print(json.dumps(info, indent=1), flush=True)
    if args.receipt:  # written at start too, so a hard stop still leaves the starting hashes to compare
        with open(args.receipt, "x", encoding="utf-8") as handle:
            json.dump(dict(info, root_files_sha256=before, stopped=False), handle, indent=1, sort_keys=True)
    try:
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
    except KeyboardInterrupt:
        pass  # Uvicorn can re-raise Ctrl+C after shutdown; still record the root integrity below.
    after = root_digest(root)
    receipt = dict(info, root_files_sha256=before, stopped=True, root_digest_after=digest(after), root_unchanged=after == before,
                   changed=sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k)))
    print(json.dumps({k: receipt[k] for k in ("root_unchanged", "changed")}), flush=True)
    if args.receipt:
        Path(args.receipt).write_text(json.dumps(receipt, indent=1, sort_keys=True), encoding="utf-8")
    return 0 if receipt["root_unchanged"] else 5


# G-ZER11-RT1 (docs/runbooks/dashboard-and-baselines.md section 5). F-01 values are the ZER-32 3.6
# illustrative set used as PILOT inputs, unchanged; nothing here relaxes them to fit a time cap.
RT1 = {
    "id": "G-ZER11-RT1", "context": "k3d-zero-door", "p6": False,
    "f01": {"delta_s": 1, "k": 3, "s_s": 30, "l_ms": 2000, "gap_s": 2, "eps_s": 1, "cap_det_s": 300, "cap_rec_s": 600},
    "w_eff_s": 300, "requests_per_sample": 9, "stop_margin_s": 5,
    # Wall-clock allowance of the non-trial phases, seconds.
    "phases_s": {"P0": 180, "P1": 300, "P2": 180, "P4_hpa_ready": 120, "P5_seal_export": 180, "P7": 300},
    "trials": {"B0-CTRL": {"warmup_s": 30, "baseline_s": 30, "fault": "delete 1 frontend pod", "load_s": 0},
               "B0-HPA": {"warmup_s": 30, "baseline_s": 30, "fault": "HTTP GET load on frontend", "load_s": 180}},
    "load": {"rps": 20, "connections": 10},
    "caps": {"total_s": 3600, "probe_samples_per_trial": 1000, "frontend_pod_deletes": 1, "load_requests": 3600},
}


def plan_matrix(plan=RT1):
    """Derived worst cases and the checks the plan must pass (raises nothing; `problems` lists failures)."""
    f, caps = plan["f01"], plan["caps"]
    trials, problems = {}, []
    for name, t in plan["trials"].items():
        # Worst case: the effect is confirmed only at T_req + W_eff, then nothing recovers, so the
        # probe must cover T_eff + cap_rec (TIMEOUT) and a candidate at the cap still gets its S.
        recovery_s = f["cap_rec_s"] + f["s_s"] + plan["stop_margin_s"]
        window_s = t["baseline_s"] + plan["w_eff_s"] + recovery_s
        samples = (t["warmup_s"] + window_s) // f["delta_s"]
        trials[name] = {"fault": t["fault"], "warmup_s": t["warmup_s"], "trial_max_s": window_s,
                        "probe_max_duration_s": t["warmup_s"] + window_s, "probe_max_samples": samples,
                        "probe_max_requests": samples * plan["requests_per_sample"],
                        "verify_min_samples": f["k"] + f["s_s"] // f["delta_s"],
                        "no_effect_needs_s": plan["w_eff_s"], "timeout_needs_after_t_eff_s": f["cap_rec_s"]}
        if samples > caps["probe_samples_per_trial"]:
            problems.append(f"{name}: {samples} samples exceed the per-trial cap")
        if recovery_s < f["cap_rec_s"] + f["gap_s"]:
            problems.append(f"{name}: the window cannot cover cap_rec, so TIMEOUT could never be scored")
        if t["load_s"] > plan["w_eff_s"]:
            problems.append(f"{name}: load runs past the effect window")
    trial_s = sum(t["probe_max_duration_s"] for t in trials.values())
    total_s = sum(plan["phases_s"].values()) + trial_s
    load_requests = plan["load"]["rps"] * plan["trials"]["B0-HPA"]["load_s"]
    if total_s > caps["total_s"]:
        problems.append(f"worst case {total_s} s exceeds the total cap {caps['total_s']} s")
    if load_requests > caps["load_requests"]:
        problems.append("load requests exceed the cap")
    if plan["p6"]:
        problems.append("P6 (BM on a new image) is not part of RT1; it needs its own package")
    deletes = sum(1 for t in plan["trials"].values() if t["fault"].startswith("delete"))
    if deletes != caps["frontend_pod_deletes"]:
        problems.append("pod deletions differ from the cap")
    totals = {"worst_case_s": total_s, "cap_s": caps["total_s"], "probe_samples": sum(t["probe_max_samples"] for t in trials.values()),
              "probe_requests": sum(t["probe_max_requests"] for t in trials.values()), "load_requests": load_requests,
              "frontend_pod_deletes": deletes, "p6": plan["p6"]}
    return {"id": plan["id"], "context": plan["context"], "f01_pilot": f, "w_eff_s": plan["w_eff_s"], "phases_s": plan["phases_s"],
            "trials": trials, "totals": totals, "problems": problems}


def plan_check(args):
    matrix = plan_matrix()
    print(json.dumps(matrix, indent=1, sort_keys=True))
    return 1 if matrix["problems"] else 0


def runtime_preflight(args):
    if not args.runtime_approval:
        print("REFUSED: runtime-preflight needs --runtime-approval <reference to Hoang's approval of the reviewed plan>", file=sys.stderr)
        return 2
    if not args.context:
        print("REFUSED: --context <exact kube context named in the approved plan> is required", file=sys.stderr)
        return 2
    out = Path(args.output)
    if out.exists():
        print("REFUSED: output exists; choose a new file", file=sys.stderr)
        return 4
    reads = {
        "deployments": ["get", "deploy", "-n", "target-app", "-o", "json"],
        "hpa_all_namespaces": ["get", "hpa", "-A", "-o", "json"],
        "zero_door_workloads": ["get", "deploy,sa,rolebinding", "-n", "zero-door", "-o", "json"],
        "target_rolebindings": ["get", "rolebinding,role", "-n", "target-app", "-o", "json"],
        "metrics_api": ["get", "apiservice", "v1beta1.metrics.k8s.io", "-o", "json"],
    }
    snapshot = {"runtime_approval": args.runtime_approval, "context": args.context, "reads": {}}
    for name, argv in reads.items():
        # kubectl from the approved operator PATH; read-only verbs from `reads`, context passed as one argv item
        done = subprocess.run(["kubectl", "--context", args.context, "--request-timeout=10s", *argv],  # nosec B603 B607
                              capture_output=True, text=True, timeout=30)
        snapshot["reads"][name] = {"exit": done.returncode, "stdout": done.stdout if done.returncode == 0 else None,
                                   "stderr": done.stderr[-2000:]}
    with open(out, "x", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=1, sort_keys=True)
    print(json.dumps({"output": str(out), "reads": {k: v["exit"] for k, v in snapshot["reads"].items()}}))
    return 0 if all(v["exit"] == 0 for v in snapshot["reads"].values()) else 1


def harness():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import r1_baseline_runtime
    return r1_baseline_runtime


def rt1(args):
    rt = harness()
    if not args.execute:
        print(json.dumps(rt.matrix(RT1), indent=1, sort_keys=True))
        return 0
    if not args.runtime_approval:
        print("REFUSED: --execute needs --runtime-approval <reference to Hoang's approval of the reviewed RT1 plan>", file=sys.stderr)
        return 2
    if args.context != RT1["context"]:
        print(f"REFUSED: --context must be exactly {RT1['context']}", file=sys.stderr)
        return 2
    problems = plan_matrix()["problems"]
    if problems or not args.out or Path(args.out).exists():
        print("REFUSED: plan-check problems or --out missing/existing", problems, file=sys.stderr)
        return 2
    kube = rt.Kube(args.context)
    result = rt.Orchestrator(RT1, kube, Path(args.out), args.runtime_approval).run()
    # errors carries RECEIPT_NOT_WRITTEN and salvage/P7 failures: when the host disk fails, this output is the record.
    print(json.dumps({k: result.get(k) for k in ("verdict", "abort", "cleanup", "final_diff", "p8", "errors")}, indent=1, default=str))
    return 0 if result["verdict"] == "COMPLETED" and result["cleanup"] == "CLEAN" and not result.get("errors") else 1


def rt1_score(args):
    rt = harness()
    out = rt.score_and_register(Path(args.raw), Path(args.root))
    print(json.dumps(out, indent=1, sort_keys=True, default=str))
    return 0 if "registered" in out else 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="verify-dashboard-baselines", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("offline", help="run the offline suites")
    f = sub.add_parser("fixture-server", help="serve SYNTHETIC results on 127.0.0.1 for a browser check")
    f.add_argument("--port", type=int, default=8711)
    r = sub.add_parser("register", help="register a closed run's scorer output directory")
    r.add_argument("--root", required=True)
    r.add_argument("--dir", required=True, help="directory name under the root (no path)")
    s = sub.add_parser("serve-results", help="serve an existing results root read-only on 127.0.0.1")
    s.add_argument("--root", required=True, help="absolute path of the results root (registry.json + run dirs)")
    s.add_argument("--reader-key-file", required=True, help='{"id","purpose":"results-reader","secret"} file')
    s.add_argument("--operator-key-file", help="the run's operator key file, to enforce KEY_SEPARATION")
    s.add_argument("--port", type=int, default=8712)
    s.add_argument("--receipt", help="new file for the start/exit root hashes")
    sub.add_parser("plan-check", help="print and check the G-ZER11-RT1 budget matrix (offline)")
    p = sub.add_parser("runtime-preflight", help="RUNTIME read-only inventory; needs --runtime-approval")
    p.add_argument("--runtime-approval")
    p.add_argument("--context")
    p.add_argument("--output", default="zer11-preflight.json")
    h = sub.add_parser("rt1", help="H-RT1: print the matrix (default) or RUN it with --execute")
    h.add_argument("--execute", action="store_true")
    h.add_argument("--runtime-approval")
    h.add_argument("--context")
    h.add_argument("--out", help="new directory for receipts, raw exports and results")
    q = sub.add_parser("rt1-score", help="P8 offline on pulled exports")
    q.add_argument("--raw", required=True)
    q.add_argument("--root", required=True)
    args = parser.parse_args(argv)
    return {"rt1": rt1, "rt1-score": rt1_score, "offline": offline, "fixture-server": fixture_server, "register": register_cmd,
            "serve-results": serve_results, "plan-check": plan_check, "runtime-preflight": runtime_preflight}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
