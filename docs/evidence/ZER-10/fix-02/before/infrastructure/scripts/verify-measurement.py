"""ZER-10/ZER-38 measurement verification and recompute entry point.

  --offline    (default) run the measurement test suites and a sealed-fixture recompute (E01) with a
               socket guard: only loopback connections owned by the tests are allowed. No lab access.
  --recompute  score sealed H/O exports into a NEW output directory (measurement CLI `score`).
  --runtime    RUNTIME probe from an explicit bounded plan; refused without --runtime-approval.
               Not executed in the ZER-10 offline package.
"""
import argparse
import ipaddress
import json
import socket
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests/fixtures/zer10"))


class OfflineGuard:
    """Refuse any connection that is not to a loopback address while offline checks run."""
    def __enter__(self):
        self.original = socket.socket.connect, socket.create_connection
        guard = self

        def check(address):
            host = address[0] if isinstance(address, tuple) else address
            try:  # IP literals only; a name would need DNS, which is itself network access
                loopback = host == "localhost" or ipaddress.ip_address(host).is_loopback
            except (TypeError, ValueError):
                loopback = False
            if not loopback:
                raise PermissionError(f"offline verification refused a connection to {host}")

        def connect(sock, address):
            check(address)
            return guard.original[0](sock, address)

        def create_connection(address, *args, **kwargs):
            check(address)
            return guard.original[1](address, *args, **kwargs)
        socket.socket.connect, socket.create_connection = connect, create_connection
        return self

    def __exit__(self, *exc):
        socket.socket.connect, socket.create_connection = self.original
        return False


def offline(output=None):
    from builder import e01
    from measurement.raw import load
    from measurement.scorer import Scorer
    with OfflineGuard():
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_measurement_*.py", top_level_dir=str(ROOT / "tests"))
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        expected = json.loads((ROOT / "tests/fixtures/zer10/expected.json").read_text())["E01"]
        with tempfile.TemporaryDirectory() as tmp:
            h, o, _ = e01().seal(tmp)
            got = Scorer(*load(h, o)).run()["incidents"][0]
        recompute = {k: got[k] for k in ("label", "mttd", "mttr", "total", "reaction")}
        recompute_ok = all(expected[k] == v for k, v in recompute.items())
    summary = {"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
               "skipped": len(result.skipped), "e01_recompute": recompute, "e01_matches_hand_values": recompute_ok,
               "verdict": "OFFLINE_PASS" if result.wasSuccessful() and recompute_ok else "OFFLINE_FAIL",
               "scope": "SYNTHETIC/OFFLINE only; not runtime evidence"}
    print(json.dumps(summary, sort_keys=True))
    if output:
        out = Path(output)
        out.mkdir(parents=True, exist_ok=False)
        (out / "offline-summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    return 0 if summary["verdict"] == "OFFLINE_PASS" else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="default")
    mode.add_argument("--recompute", action="store_true")
    mode.add_argument("--runtime", action="store_true")
    parser.add_argument("--h-export")
    parser.add_argument("--o-export")
    parser.add_argument("--output", help="new directory; never overwritten")
    parser.add_argument("--required-flow", action="append")
    parser.add_argument("--options")
    parser.add_argument("--other-export", action="append", help="export of another run (cross-run LINK_CONFLICT)")
    parser.add_argument("--plan")
    parser.add_argument("--context")
    parser.add_argument("--outbox")
    parser.add_argument("--h-url")
    parser.add_argument("--h-keys")
    parser.add_argument("--runtime-approval")
    args = parser.parse_args(argv)
    from measurement.__main__ import main as cli
    if args.recompute:
        if not (args.h_export and args.output):
            parser.error("--recompute needs --h-export and --output (and --o-export unless B0)")
        call = ["score", "--h-export", args.h_export, "--output", args.output]
        call += ["--o-export", args.o_export] if args.o_export else []
        call += [x for flow in args.required_flow or [] for x in ("--required-flow", flow)]
        call += ["--options", args.options] if args.options else []
        call += [x for other in args.other_export or [] for x in ("--other-export", other)]
        return cli(call)
    if args.runtime:
        missing = [k for k in ("plan", "context", "outbox", "h_url", "h_keys") if not getattr(args, k)]
        if missing:
            parser.error("--runtime needs --" + ", --".join(m.replace("_", "-") for m in missing))
        if args.outbox and Path(args.outbox).exists():
            parser.error("--outbox must be a new file for a new runtime run")
        call = ["probe", "--plan", args.plan, "--context", args.context, "--outbox", args.outbox,
                "--h-url", args.h_url, "--h-keys", args.h_keys]
        call += ["--runtime-approval", args.runtime_approval] if args.runtime_approval else []
        return cli(call)
    return offline(args.output)


if __name__ == "__main__":
    sys.exit(main())
