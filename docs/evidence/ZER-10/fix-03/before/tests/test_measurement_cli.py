"""CLI and entry points: offline by construction, outputs never overwrite, raw is refused when tampered."""
import contextlib
import csv
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "tests/fixtures/zer10"))
from builder import e01  # noqa: E402
from measurement.__main__ import main as cli  # noqa: E402
from measurement.output import INCIDENT_COLUMNS  # noqa: E402

PLANS = ROOT / "tests/fixtures/zer10"


@contextlib.contextmanager
def no_network():
    def refuse(*args, **kwargs):
        raise AssertionError("network access attempted")
    with patch.object(socket.socket, "connect", refuse), patch.object(socket, "create_connection", refuse), \
            patch.object(socket, "getaddrinfo", refuse):
        yield


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = cli(argv)
        except SystemExit as exit_:
            code = exit_.code
    return code, out.getvalue(), err.getvalue()


class Cli(unittest.TestCase):
    def test_help_and_plan_check_open_no_connection(self):
        with no_network():
            self.assertEqual(0, run(["--help"])[0])
            code, out, _ = run(["plan-check", "--plan", str(PLANS / "plan-synthetic-boutique.json")])
            self.assertEqual(0, code)
            self.assertEqual(9, json.loads(out)["per_sample_max_requests"])
            self.assertEqual(0, run(["plan-check", "--plan", str(PLANS / "plan-synthetic-fixture.json")])[0])
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "plan.json"
            plan = json.loads((PLANS / "plan-synthetic-boutique.json").read_text())
            del plan["budget"]
            bad.write_text(json.dumps(plan))
            self.assertEqual(2, run(["plan-check", "--plan", str(bad)])[0])

    def test_runtime_probe_is_refused_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp, no_network():
            code, _, err = run(["probe", "--plan", str(PLANS / "plan-synthetic-boutique.json"), "--context", "x",
                                "--outbox", str(Path(tmp) / "o.jsonl"), "--h-url", "http://127.0.0.1:9", "--h-keys", "k"])
            self.assertEqual(2, code)
            self.assertIn("--runtime-approval", err)
            self.assertFalse((Path(tmp) / "o.jsonl").exists())

    def test_score_writes_once_and_refuses_overwrite_or_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            h, o, _ = e01().seal(tmp)
            out = Path(tmp) / "score-1"
            with no_network():
                code, stdout, _ = run(["score", "--h-export", str(h), "--o-export", str(o), "--output", str(out),
                                       "--required-flow", "checkout"])
            self.assertEqual(0, code, stdout)
            document = json.loads((out / "score.json").read_text())
            self.assertEqual("zd-measurement-score/1", document["schema"])
            incident = document["runs"][0]["incidents"][0]
            self.assertEqual((30.0, 60.0, 90.0, 19.0), (incident["mttd"], incident["mttr"], incident["total"], incident["reaction"]))
            with open(out / "incidents.csv", encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))
            self.assertEqual(INCIDENT_COLUMNS, rows[0])
            self.assertEqual("RECOVERED", rows[1][INCIDENT_COLUMNS.index("label")])
            self.assertTrue((out / "usage.csv").read_text().startswith("level,key,calls"))
            before = (out / "score.json").read_bytes()
            self.assertEqual(4, run(["score", "--h-export", str(h), "--o-export", str(o), "--output", str(out)])[0])
            self.assertEqual(before, (out / "score.json").read_bytes())
            self.assertEqual(4, run(["score", "--h-export", str(h), "--o-export", str(o), "--output", str(h / "inside")])[0])
            self.assertFalse((h / "inside").exists())
            raw = h / "H.jsonl"
            raw.chmod(0o644)
            raw.write_bytes(raw.read_bytes().replace(b'"pass":false', b'"pass":true', 1))
            code, _, err = run(["score", "--h-export", str(h), "--o-export", str(o), "--output", str(Path(tmp) / "score-2")])
            self.assertEqual(3, code)
            self.assertIn("REFUSED raw export", err)
            self.assertFalse((Path(tmp) / "score-2").exists())
            self.assertFalse(any(p.name.startswith(".score-") for p in Path(tmp).iterdir()))

    def test_output_inside_any_input_export_is_refused(self):
        """ZR10-N1: other-run exports are inputs too; the output never lands inside one."""
        with tempfile.TemporaryDirectory() as tmp:
            h, o, _ = e01().seal(Path(tmp) / "primary")
            other_h, _, _ = e01().seal(Path(tmp) / "other")
            out = other_h / "score-inside-input"
            with no_network():
                code, _, err = run(["score", "--h-export", str(h), "--o-export", str(o), "--other-export", str(other_h),
                                    "--output", str(out)])
            self.assertEqual(4, code)
            self.assertIn("inside an input export", err)
            self.assertFalse(out.exists())

    def test_verify_entry_point_help_is_offline(self):
        sys.path.insert(0, str(ROOT / "infrastructure/scripts"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("verify_measurement", ROOT / "infrastructure/scripts/verify-measurement.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with no_network(), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as done:
                module.main(["--help"])
        self.assertEqual(0, done.exception.code)
        with module.OfflineGuard():
            with self.assertRaises(PermissionError):
                socket.create_connection(("192.0.2.10", 80), timeout=0.1)
            with self.assertRaises(PermissionError):
                socket.create_connection(("example.invalid", 80), timeout=0.1)

    def test_clean_checkout_needs_no_scratch(self):
        for path in list((ROOT / "tests").glob("test_measurement_*.py")) + list((ROOT / "tests/fixtures/zer10").glob("*")) + \
                list((ROOT / "agent-orchestrator/measurement").glob("*.py")) + [ROOT / "infrastructure/scripts/verify-measurement.py"]:
            if path.is_file():
                self.assertNotIn("scr" + "atch/", path.read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
