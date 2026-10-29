"""ZER-10/ZER-38 measurement CLI.

  score       recompute from sealed H/O exports into a NEW output directory (offline)
  plan-check  validate a probe plan and print its bounds (offline)
  probe       RUNTIME: send business transactions to the plan's target; requires --runtime-approval

`--help` and the offline commands open no network connection.
"""
import argparse
import json
import signal
import sys
import threading
from pathlib import Path

from . import VERSION
from .config import ConfigError, plan as check_plan


def flow_from(plan):
    from .flows import Flow, boutique_spec, fixture_spec
    spec = plan.get("flow_spec")
    if isinstance(spec, dict) and spec.get("builtin") == "boutique-checkout":
        args = spec.get("args", {})
        spec = boutique_spec(args["product_id"], args.get("product_marker"), args.get("checkout_form"), args.get("cart_markers"))
    elif isinstance(spec, dict) and spec.get("builtin") == "fixture-order-synthetic":
        spec = fixture_spec(spec.get("args", {}).get("item", "benign-catalog-item"))
    return Flow(spec, plan["target"]["origin"], plan["target"]["allowed_origins"])


def score(args):
    from .raw import RawError, load
    from .scorer import Scorer, SCORER_VERSION
    from .metrics import run_metrics
    from .output import OutputError, write
    options = json.loads(Path(args.options).read_text()) if args.options else {}
    if args.required_flow:
        options["required_flows"] = args.required_flow
    try:
        h, o = load(args.h_export, args.o_export)
        others = []
        for directory in args.other_export or []:
            meta = json.loads((Path(directory) / "export.json").read_text())
            from .raw import Export
            others.append(Export(directory, meta.get("plane")))
    except (RawError, OSError, ValueError) as error:
        print(f"REFUSED raw export: {error}", file=sys.stderr)
        return 3
    scorer = Scorer(h, o, options, others)
    scored = scorer.run()
    scored["metrics"] = run_metrics(scorer, scored, options)
    document = {"scorer_version": SCORER_VERSION, "options": options,
                "inputs": {"h_export_json_sha256": h.meta_sha256, "o_export_json_sha256": o.meta_sha256 if o else None,
                           "run_id": h.run_id, "other_exports": [{"run_id": x.run_id, "plane": x.plane,
                                                                  "export_json_sha256": x.meta_sha256} for x in others]},
                "runs": [scored]}
    try:
        # Every input export, the other runs' too, is outside the output boundary.
        out = write(args.output, document, [args.h_export, args.o_export] + list(args.other_export or []))
    except OutputError as error:
        print(f"REFUSED output: {error}", file=sys.stderr)
        return 4
    print(json.dumps({"output": str(out), "incidents": len(scored["incidents"]),
                      "labels": scored["metrics"]["kpi"]["labels"]}, sort_keys=True))
    return 0


def plan_check(args):
    try:
        plan = check_plan(json.loads(Path(args.plan).read_text()))
        flow = flow_from(plan)
    except (ConfigError, ValueError, KeyError) as error:
        print(f"INVALID plan: {error}", file=sys.stderr)
        return 2
    b = plan["budget"]
    print(json.dumps({"provenance": plan["provenance"], "flow": flow.spec["flow"], "spec_version": flow.spec["spec_version"],
                      "per_sample_max_requests": flow.per_sample_requests, "max_requests": b["max_requests"],
                      "max_samples": b["max_samples"], "max_duration_s": b["max_duration_s"],
                      "delta_s": plan["f01"]["delta_s"], "origin": plan["target"]["origin"],
                      "note": "values are inputs; only a LOCKED provenance comes from ZER-53"}, sort_keys=True))
    return 0


def probe(args):
    """Runtime path. Not exercised by the offline package; refuses without an explicit approval ref."""
    from .clock import HttpReference, ProbeClock
    from .probe import ProbeRunner
    from .sink import HttpHSink, Journal, Outbox, PersistenceFailure, Publisher, load_probe_key
    if not args.runtime_approval:
        print("REFUSED: runtime probing needs --runtime-approval <reference to the owner's approval>", file=sys.stderr)
        return 2
    try:
        plan = check_plan(json.loads(Path(args.plan).read_text()))
        flow = flow_from(plan)
        context = json.loads(Path(args.context).read_text())
    except (ConfigError, ValueError, KeyError) as error:
        print(f"INVALID input: {error}", file=sys.stderr)
        return 2
    outbox = Outbox(args.outbox)
    start = 0
    probe_cfg = plan["probe"]
    # A restarted probe continues its sequence: (trial, probe_id, probe_version, sequence) is the sample key.
    for line in Path(args.outbox).read_text().splitlines() if Path(args.outbox).exists() else []:
        record = json.loads(line)
        e = record.get("event") or {}
        p = e.get("payload") or {}
        if e.get("event_type") == "PROBE_SAMPLE" and e.get("trial_id") == context.get("trial_id") and \
                (p.get("probe_id"), p.get("probe_version")) == (probe_cfg["probe_id"], probe_cfg["probe_version"]):
            start = max(start, p["sequence"] + 1)
    clock = ProbeClock(probe_cfg["clock_id"], probe_cfg["clock_source"])
    reference = HttpReference(plan["clock_sync"]["reference_url"]) if probe_cfg["clock_source"] != "HOST_SHARED" else None
    publisher = Publisher(outbox, HttpHSink(args.h_url, load_probe_key(args.h_keys)))
    cancel = threading.Event()
    # The journal is on disk (fsync per note): a cancelled sample is never emitted, so its cleanup and
    # unresolved ownership must survive the process for the operator (residual of ZR10-10).
    journal_path = getattr(args, "journal", None) or str(args.outbox) + ".journal.jsonl"
    runner = ProbeRunner(plan, flow, context, clock, publisher, journal=Journal(journal_path), reference=reference,
                         cancel=cancel, target=plan.get("observed_target"), start_sequence=start)

    def stop(signum, frame):
        # SIGINT/SIGTERM take the cancel path: the transaction in flight ends at its next read slice, its
        # cleanup runs within grace_s of this moment and it is journaled, never emitted; the outbox is
        # flushed within the same grace window.
        runner.stop()
    previous = {sig: signal.signal(sig, stop) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        try:
            runner.note("PROBE_STARTED", runtime_approval=args.runtime_approval)
        except PersistenceFailure as error:
            print(f"REFUSED: {error}", file=sys.stderr)
            return 5
        summary = runner.run()
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    summary["runtime_approval"] = args.runtime_approval
    summary["journal"] = str(journal_path)
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["stop_reason"] not in {"PERSISTENCE_FAILED", "SINK_UNAUTHORIZED", "SINK_REFUSED"} else 5


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m measurement", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="recompute from sealed exports (offline)")
    s.add_argument("--h-export", required=True)
    s.add_argument("--o-export")
    s.add_argument("--output", required=True, help="new directory; never overwritten")
    s.add_argument("--required-flow", action="append", help="F-04 required flow for uptime (repeatable)")
    s.add_argument("--options", help="JSON options: criteria_version, benign, surfaces")
    s.add_argument("--other-export", action="append",
                   help="export of another run of the same archive, for cross-run LINK_CONFLICT (repeatable)")
    p = sub.add_parser("plan-check", help="validate a probe plan (offline)")
    p.add_argument("--plan", required=True)
    r = sub.add_parser("probe", help="RUNTIME probe; needs --runtime-approval")
    r.add_argument("--plan", required=True)
    r.add_argument("--context", required=True, help="JSON run/trial context from the harness")
    r.add_argument("--outbox", required=True)
    r.add_argument("--h-url", required=True)
    r.add_argument("--h-keys", required=True)
    r.add_argument("--journal", help="operator journal, appended and fsynced (default: <outbox>.journal.jsonl)")
    r.add_argument("--runtime-approval")
    args = parser.parse_args(argv)
    return {"score": score, "plan-check": plan_check, "probe": probe}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
