"""ZER-11 AC-01/AC-02: the dashboard shows scorer results only, the same values as the export.

Raw traces (tests/fixtures/zer11/cases.py, locked ZER-10 builder) are sealed by the real ZER-9
Archive, scored by the ZER-10 CLI, registered, then read through measurement_view and the actual
Nemesis ASGI app. Expected values are hand-computed (fixtures/zer11/expected.json). No network,
Kafka, Prometheus, Kubernetes or model is contacted; upstream answers are fakes.
"""
import asyncio
import contextlib
import copy
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import httpx

REAL_CLIENT = httpx.AsyncClient  # the test's own client; the app's httpx.AsyncClient is replaced by FakeHttp
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent-orchestrator"))
sys.path.insert(0, str(ROOT / "tests/fixtures/zer11"))
EXPECTED = json.loads((ROOT / "tests/fixtures/zer11/expected.json").read_text())
GUARD = json.loads((ROOT / "tests/fixtures/zer12/command-guards.json").read_text())
STATIC = ROOT / "agent-orchestrator/nemesis/static"


def view_module():
    # Imported lazily so the legacy-behaviour tests below also run against the pre-ZER-11 snapshot.
    from nemesis import measurement_view
    return measurement_view


def score_case(name, root, options=None, output=None):
    """Seal the case and score it with the ZER-10 CLI into root/<output or name>."""
    from cases import CASES
    from measurement.__main__ import main as cli
    work = Path(tempfile.mkdtemp(dir=root.parent))
    h, o, _ = CASES[name]().seal(work)
    argv = ["score", "--h-export", str(h), "--o-export", str(o), "--output", str(root / (output or name)), "--required-flow", "checkout"]
    if options is not None:
        (work / "options.json").write_text(json.dumps(options))
        argv += ["--options", str(work / "options.json")]
    with contextlib.redirect_stdout(io.StringIO()):
        assert cli(argv) == 0, name
    return work


class Store:
    """A results root with every case scored and registered (built once per test class)."""
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "results"
        self.root.mkdir()
        mv = view_module()
        self.runs = {}
        for name in EXPECTED["cases"]:
            score_case(name, self.root)
            self.runs[name] = mv.register(self.root, name)["run_id"]

    def store(self):
        return view_module().ResultsStore(self.root)


def load_app(name):
    spec = importlib.util.spec_from_file_location("zer11_" + name, ROOT / "agent-orchestrator" / name / "main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(data):
    return hashlib.sha256(data).hexdigest()


class AdapterValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Store()

    @classmethod
    def tearDownClass(cls):
        cls.s.tmp.cleanup()

    def view(self, name):
        return self.s.store().view(self.s.runs[name])

    def row(self, view):
        self.assertEqual(1, len(view["incidents"]))
        return dict(zip(view["incident_columns"], view["incidents"][0]))

    def test_e01_matches_hand_values_and_the_export_file(self):
        e = EXPECTED["cases"]["b1_recovered"]
        v = self.view("b1_recovered")
        row = self.row(v)
        for column in ("label", "mttd_s", "mttr_s", "total_s", "reaction_s"):
            self.assertEqual(e[column if column != "label" else "label"], row[column], column)
        for metric, (verdict, rate, mean) in ((k, v) for k, v in e["kpi"].items() if k != "N"):
            self.assertEqual((verdict, rate, mean, e["kpi"]["N"]),
                             (v["kpi"][metric]["verdict"], v["kpi"][metric]["rate"], v["kpi"][metric]["mean_observed_s"], v["kpi"][metric]["N"]))
        self.assertEqual(e["recovered_rate"], [v["kpi"]["recovered_rate"]["numerator"], v["kpi"]["recovered_rate"]["N"]])
        self.assertEqual(e["failure_rate"], [v["kpi"]["failure_rate"]["numerator"], v["kpi"]["failure_rate"]["N"]])
        # The page's table is the export: the same rows as incidents.csv on disk.
        with open(self.s.root / "b1_recovered/incidents.csv", encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        self.assertEqual(rows[0], v["incident_columns"])
        self.assertEqual(rows[1:], v["incidents"])
        # KPI values are passed through from score.json unchanged (no second computation).
        document = json.loads((self.s.root / "b1_recovered/score.json").read_text(encoding="utf-8"))
        self.assertEqual(document["runs"][0]["metrics"]["kpi"], v["kpi"])
        self.assertEqual(document["runs"][0]["metrics"]["uptime"], v["uptime"])
        self.assertEqual(sha((self.s.root / "b1_recovered/score.json").read_bytes()), v["provenance"]["sha256"]["score.json"])

    def test_same_run_inputs_and_options_give_the_same_kpi(self):
        first = self.view("b1_recovered")
        again = self.s.store().view(self.s.runs["b1_recovered"])
        self.assertEqual(first, again)
        # Re-scoring the same raw (same trace, new seal) with the same options gives the same KPI.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "results"
            root.mkdir()
            mv = view_module()
            from cases import CASES
            from measurement.__main__ import main as cli
            trace = CASES["b1_recovered"]()
            exports = []
            for index in range(2):
                work = Path(tmp) / f"seal{index}"
                h, o, _ = trace.seal(work)
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(0, cli(["score", "--h-export", str(h), "--o-export", str(o), "--output", str(root / f"s{index}"),
                                             "--required-flow", "checkout"]))
                exports.append(json.loads((root / f"s{index}/score.json").read_text(encoding="utf-8")))
            self.assertEqual(exports[0]["runs"][0]["metrics"], exports[1]["runs"][0]["metrics"])
            self.assertEqual(exports[0]["options"], exports[1]["options"])
            mv.register(root, "s0")
            with self.assertRaises(mv.ResultError) as raised:
                mv.register(root, "s1")  # the same run_id cannot be registered twice
            self.assertEqual("ALREADY_REGISTERED", raised.exception.reason)

    def test_null_stays_empty_and_failure_is_counted(self):
        e = EXPECTED["cases"]["b1_failed_timeout"]
        v = self.view("b1_failed_timeout")
        row = self.row(v)
        self.assertEqual((e["label"], e["mttd_s"], e["mttr_s"], e["total_s"], e["reaction_s"]),
                         (row["label"], row["mttd_s"], row["mttr_s"], row["total_s"], row["reaction_s"]))
        self.assertEqual(e["failure_rate"], [v["kpi"]["failure_rate"]["numerator"], v["kpi"]["failure_rate"]["N"]])
        self.assertEqual(e["recovered_rate"], [v["kpi"]["recovered_rate"]["numerator"], v["kpi"]["recovered_rate"]["N"]])
        self.assertEqual("NOT_PASS", v["kpi"]["mttr_120"]["verdict"])
        self.assertIsNone(v["kpi"]["mttr_120"]["mean_observed_s"])

    def test_empty_run_is_empty_not_pass_or_rate(self):
        v = self.view("b1_empty")
        self.assertEqual([], v["incidents"])
        self.assertEqual("EMPTY", v["kpi"]["counts"]["status"])
        for metric in ("mttd", "mttr_120", "mttr_180", "reaction"):
            self.assertEqual("EMPTY", v["kpi"][metric]["verdict"])
            self.assertNotIn("rate", v["kpi"][metric])
        self.assertEqual({"status": "EMPTY", "N": 0}, v["kpi"]["recovered_rate"])
        self.assertEqual("UNKNOWN", v["data_time"]["status"])
        self.assertEqual("NO_EVENT_MILESTONE", v["data_time"]["reason"])

    def test_missing_and_unverified_clock_stay_unknown(self):
        v = self.view("b1_clock_unverified")
        row = self.row(v)
        self.assertEqual("MISSING", row["label"])
        self.assertIn("CLOCK_UNVERIFIED", row["flags"].split("|"))
        self.assertEqual("UNKNOWN", v["kpi"]["mttd"]["verdict"])
        self.assertEqual(1, v["kpi"]["unknown_rate"]["numerator"])

    def test_modes_labels_and_mode_violations(self):
        for name, e in EXPECTED["cases"].items():
            with self.subTest(case=name):
                v = self.view(name)
                self.assertEqual((e["group"], e["mode"]), (v["group"], v["mode"]))
                if "mode_violations" in e:
                    self.assertEqual(e["mode_violations"], v["mode_violations"]["count"])
                if "mode_violations_min" in e:
                    self.assertGreaterEqual(v["mode_violations"]["count"], e["mode_violations_min"])
                if "missing" in e:
                    self.assertIn(e["missing"], self.row(v)["missing_reasons"].split("|"))
        b0 = self.row(self.view("b0_controller"))
        e = EXPECTED["cases"]["b0_controller"]
        self.assertEqual((e["label"], e["mttd_s"], e["mttr_s"], e["total_s"], e["reaction_s"]),
                         (b0["label"], b0["mttd_s"], b0["mttr_s"], b0["total_s"], b0["reaction_s"]))
        self.assertEqual("N/A", self.view("b0_controller")["kpi"]["mttd"]["verdict"])
        self.assertEqual("N/A", self.view("b0_controller")["usage"]["status"])

    def test_data_time_is_latest_scored_milestone_not_generated_at(self):
        v = self.view("b1_recovered")
        e = EXPECTED["cases"]["b1_recovered"]
        self.assertEqual("OK", v["data_time"]["status"])
        self.assertEqual(EXPECTED["t0_ms"] + e["latest_milestone_s"] * 1000, v["data_time"]["latest_ms"])
        self.assertIn("not an event time", v["provenance"]["generated_at_meaning"])

    def test_view_leaks_no_path_and_columns_match_measurement_output(self):
        from measurement import output
        mv = view_module()
        self.assertEqual(output.INCIDENT_COLUMNS, mv.INCIDENT_COLUMNS)
        self.assertEqual(output.USAGE_COLUMNS, mv.USAGE_COLUMNS)
        for value in (None, True, False, 0, 0.0, 1.5, "x", ["b", "a"], ("t",), "N/A"):
            self.assertEqual(output.cell(value), mv.cell(value))
        for name in self.s.runs:
            text = json.dumps(self.view(name))
            self.assertNotIn(str(self.s.root), text)
            self.assertNotIn(self.s.root.as_posix(), text)
            self.assertNotIn("canary", text.lower())


class AdapterIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "results"
        self.root.mkdir()
        self.mv = view_module()
        score_case("b1_recovered", self.root)
        self.entry = self.mv.register(self.root, "b1_recovered")
        self.run = self.entry["run_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def refused(self, reason, run=None, store=None):
        with self.assertRaises(self.mv.ResultError) as raised:
            (store or self.mv.ResultsStore(self.root)).view(run or self.run)
        self.assertEqual(reason, raised.exception.reason)
        return raised.exception

    def rewrite(self, name, data, rehash=True):
        (self.root / "b1_recovered" / name).write_bytes(data)
        if rehash:
            registry = json.loads((self.root / "registry.json").read_text())
            registry["runs"][0]["sha256"][name] = sha(data)
            (self.root / "registry.json").write_text(json.dumps(registry))

    def registry(self, change):
        registry = json.loads((self.root / "registry.json").read_text())
        change(registry)
        (self.root / "registry.json").write_text(json.dumps(registry))

    def test_tampered_artifact_is_refused(self):
        data = (self.root / "b1_recovered/score.json").read_bytes()
        self.rewrite("score.json", data.replace(b'"mean_observed_s": 30.0', b'"mean_observed_s": 3.0'), rehash=False)
        self.assertEqual(422, self.refused("ARTIFACT_HASH_MISMATCH").status)

    def test_malformed_nonfinite_duplicate_and_schema(self):
        good = (self.root / "b1_recovered/score.json").read_bytes()
        for broken, reason in [(good.replace(b'"mean_observed_s": 30.0', b'"mean_observed_s": NaN'), "ARTIFACT_MALFORMED"),
                               (good.replace(b'"mean_observed_s": 30.0', b'"mean_observed_s": 1e999'), "ARTIFACT_MALFORMED"),
                               (good.replace(b'"mean_observed_s": 30.0', b'"mean_observed_s": 30.0, "mean_observed_s": 3.0'), "ARTIFACT_MALFORMED"),
                               (good[:-20], "ARTIFACT_MALFORMED"),
                               (good.replace(b'"schema": "zd-measurement-score/1"', b'"schema": "zd-measurement-score/2"'), "SCHEMA_UNSUPPORTED")]:
            with self.subTest(reason=reason):
                self.rewrite("score.json", broken)
                self.refused(reason)

    def test_run_group_and_export_mismatch(self):
        good = (self.root / "b1_recovered/score.json").read_bytes()
        document = json.loads(good)
        other = "run_" + "f" * 32
        swapped = copy.deepcopy(document)
        swapped["runs"][0]["run_id"] = other
        self.rewrite("score.json", json.dumps(swapped).encode())
        self.refused("RUN_MISMATCH")
        self.rewrite("score.json", good)
        self.registry(lambda r: r["runs"][0].update(group="B2"))
        self.refused("GROUP_MISMATCH")
        self.registry(lambda r: r["runs"][0].update(group="B1"))
        csv_data = (self.root / "b1_recovered/incidents.csv").read_bytes()
        self.rewrite("incidents.csv", csv_data.replace(b",30.0,", b",3.0,"))
        self.refused("EXPORT_INCONSISTENT")
        self.rewrite("incidents.csv", csv_data)
        self.assertEqual(self.run, self.mv.ResultsStore(self.root).view(self.run)["run_id"])

    def test_registry_paths_status_and_ids(self):
        for change, reason in [(lambda r: r["runs"][0].update(dir="../b1_recovered"), "REGISTRY_INVALID"),
                               (lambda r: r["runs"][0].update(dir="b1_recovered/../x"), "REGISTRY_INVALID"),
                               (lambda r: r["runs"][0].update(status="OPEN"), "REGISTRY_INVALID"),
                               (lambda r: r["runs"][0].update(extra=1), "REGISTRY_INVALID"),
                               (lambda r: r["runs"].append(dict(r["runs"][0])), "REGISTRY_INVALID")]:
            original = (self.root / "registry.json").read_bytes()
            with self.subTest(reason=reason):
                self.registry(change)
                self.assertEqual(503, self.refused(reason).status)
            (self.root / "registry.json").write_bytes(original)
        for bad, reason, status in [("../registry.json", "RUN_ID_INVALID", 400), ("run_" + "0" * 32, "RUN_NOT_REGISTERED", 404),
                                    (self.run.upper(), "RUN_ID_INVALID", 400)]:
            with self.subTest(run=bad):
                self.assertEqual(status, self.refused(reason, run=bad).status)
        with self.assertRaises(self.mv.ResultError) as raised:
            self.mv.ResultsStore(self.root).file(self.run, "../registry.json")
        self.assertEqual("FILE_NOT_EXPORTED", raised.exception.reason)

    def test_unregistered_output_is_never_listed_or_served(self):
        score_case("b1_failed_timeout", self.root)  # present on disk, not registered
        store = self.mv.ResultsStore(self.root)
        self.assertEqual([self.run], [r["run_id"] for r in store.runs()])
        document = json.loads((self.root / "b1_failed_timeout/score.json").read_text())
        self.refused("RUN_NOT_REGISTERED", run=document["runs"][0]["run_id"])

    def test_symlinked_artifact_outside_root_is_refused(self):
        outside = Path(self.tmp.name) / "outside"
        shutil.copytree(self.root / "b1_recovered", outside)
        shutil.rmtree(self.root / "b1_recovered")
        try:
            os.symlink(outside, self.root / "b1_recovered", target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlinks unavailable here: {type(error).__name__}")
        self.refused("ARTIFACT_SYMLINK")

    def test_root_configuration(self):
        with patch.dict(os.environ, {"ZD_RESULTS_ROOT": ""}):
            with self.assertRaises(self.mv.ResultError) as raised:
                self.mv.ResultsStore.from_env()
            self.assertEqual("RESULTS_NOT_CONFIGURED", raised.exception.reason)
        with self.assertRaises(self.mv.ResultError):
            self.mv.ResultsStore("relative/results")
        (self.root / "registry.json").unlink()
        with self.assertRaises(self.mv.ResultError) as raised:
            self.mv.ResultsStore(self.root).runs()
        self.assertEqual("REGISTRY_MISSING", raised.exception.reason)

    def test_register_refuses_an_export_that_differs_from_score_json(self):
        score_case("b1_failed_timeout", self.root)
        path = self.root / "b1_failed_timeout/usage.csv"
        path.write_bytes(path.read_bytes() + b"extra,row\n")
        with self.assertRaises(self.mv.ResultError) as raised:
            self.mv.register(self.root, "b1_failed_timeout")
        self.assertEqual("EXPORT_INCONSISTENT", raised.exception.reason)
        self.assertEqual(1, len(json.loads((self.root / "registry.json").read_text())["runs"]))

    def test_shape_of_consumed_fields_is_a_reason_code(self):
        # A score.json that parses but lacks what the view, the CSV rows or the page read is refused with
        # a 422 reason code when registered and when read, never an exception (HTTP 500).
        good = json.loads((self.root / "b1_recovered/score.json").read_bytes())
        run = lambda d: d["runs"][0]
        cases = [
            ("no H export digest", lambda d: d["inputs"].update(h_export_json_sha256=None), "INPUT_DIGEST_MISSING"),
            ("O export digest not hex", lambda d: d["inputs"].update(o_export_json_sha256="sha256:" + "0" * 64), "INPUT_DIGEST_MISSING"),
            ("kpi without entries", lambda d: run(d)["metrics"].update(kpi={}), "ARTIFACT_MALFORMED"),
            ("kpi entry not an object", lambda d: run(d)["metrics"]["kpi"].update(mttd=[]), "ARTIFACT_MALFORMED"),
            ("milestones list", lambda d: run(d)["incidents"][0].update(milestones=["t_det"]), "ARTIFACT_MALFORMED"),
            ("uncertainty null", lambda d: run(d)["incidents"][0].update(uncertainty_ms=None), "ARTIFACT_MALFORMED"),
            ("incident without label", lambda d: run(d)["incidents"][0].pop("label"), "ARTIFACT_MALFORMED"),
            ("mode violations count", lambda d: run(d)["findings"].update(mode_violations=1), "ARTIFACT_MALFORMED"),
            ("leak list", lambda d: run(d).update(leak=["trial"]), "ARTIFACT_MALFORMED"),
            ("leak unknown text", lambda d: run(d).update(leak={"trl_x": {"result": "PASS", "unknown": "x"}}), "ARTIFACT_MALFORMED"),
            ("uptime entry null", lambda d: run(d)["metrics"].update(uptime={"trl_x": None}), "ARTIFACT_MALFORMED"),
            ("run flags text", lambda d: run(d).update(run_flags="x"), "ARTIFACT_MALFORMED"),
        ]
        for i, (name, change, reason) in enumerate(cases):
            with self.subTest(case=name):
                doc = copy.deepcopy(good)
                change(doc)
                data = json.dumps(doc).encode()
                fresh = self.root / f"shape-{i}"
                shutil.copytree(self.root / "b1_recovered", fresh)
                (fresh / "score.json").write_bytes(data)
                with self.assertRaises(self.mv.ResultError) as raised:
                    self.mv.register(self.root, fresh.name)
                self.assertEqual((reason, 422), (raised.exception.reason, raised.exception.status))
                self.rewrite("score.json", data)  # registered entry now names these bytes
                self.assertEqual(422, self.refused(reason).status)
        # Control: a key nothing consumes is passed through as scored, not judged.
        doc = copy.deepcopy(good)
        run(doc)["metrics"]["kpi"]["N"] = "not read by the view"
        self.rewrite("score.json", json.dumps(doc).encode())
        self.assertEqual("not read by the view", self.mv.ResultsStore(self.root).view(self.run)["kpi"]["N"])
        self.assertEqual(1, len(json.loads((self.root / "registry.json").read_text())["runs"]))


class FakeResponse:
    def __init__(self, status, body):
        self.status_code, self.body = status, body

    def json(self):
        if isinstance(self.body, Exception):
            raise self.body
        return self.body


class FakeHttp:
    """httpx.AsyncClient stand-in: `answers` maps a URL fragment/query to a response or exception."""
    answers = {}
    calls = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get(self, url, params=None):
        key = (params or {}).get("query", url)
        FakeHttp.calls.append(key)
        for fragment, answer in FakeHttp.answers.items():
            if fragment in key:
                if isinstance(answer, Exception):
                    raise answer
                return answer
        raise ConnectionError("no fake answer")


class Http(unittest.IsolatedAsyncioTestCase):
    """The actual Nemesis ASGI app with fake Prometheus/Hephaestus answers."""
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.operator = {"id": "op", "purpose": "operator", "secret": "offline-operator-token-0000000000000000"}
        self.reader = {"id": "reader", "purpose": "results-reader", "secret": "offline-results-reader-token-000000000"}
        (d / "operator.json").write_text(json.dumps(self.operator))
        (d / "reader.json").write_text(json.dumps(self.reader))
        (d / "policy.json").write_text(json.dumps(GUARD["policy"]))
        self.env = {"ZD_COMMAND_POLICY_FILE": str(d / "policy.json"), "ZD_OPERATOR_TOKEN_FILE": str(d / "operator.json"),
                    "ZD_RESULTS_TOKEN_FILE": str(d / "reader.json"), "ZD_EVENT_URL": "", "OPENAI_API_KEY": "", "GEMINI_API_KEYS": ""}
        self.patch = patch.dict(os.environ, self.env)
        self.patch.start()
        self.nemesis = load_app("nemesis")
        self.http = patch.object(self.nemesis.httpx, "AsyncClient", FakeHttp)
        self.http.start()
        FakeHttp.answers, FakeHttp.calls = {}, []

    async def asyncTearDown(self):
        self.http.stop()
        self.patch.stop()
        self.tmp.cleanup()

    async def request(self, method, path, token=None):
        headers = {"Authorization": "Bearer " + token} if token else {}
        async with REAL_CLIENT(transport=httpx.ASGITransport(app=self.nemesis.app), base_url="http://offline") as client:
            return await client.request(method, path, headers=headers)

    def results_root(self):
        root = Path(self.tmp.name) / "results"
        root.mkdir()
        score_case("b1_recovered", root)
        run = view_module().register(root, "b1_recovered")["run_id"]
        os.environ["ZD_RESULTS_ROOT"] = str(root)
        return root, run

    async def test_status_reports_no_data_and_source_error_not_zero(self):
        FakeHttp.answers = {"kube_deployment": ConnectionError("down")}
        body = (await self.request("GET", "/api/status", self.operator["secret"])).json()
        self.assertEqual({"replicas": None, "cpu": None}, body["services"]["frontend"])
        self.assertEqual("ERROR", body["source"]["status"])
        FakeHttp.answers = {"kube_deployment": FakeResponse(200, {"data": {"result": [
            {"metric": {"deployment": "frontend"}, "value": [0, "0"]},
            {"metric": {"deployment": "cartservice"}, "value": [0, "NaN"]}]}}),
            "container_cpu": FakeResponse(500, {})}
        body = (await self.request("GET", "/api/status", self.operator["secret"])).json()
        self.assertEqual(0, body["services"]["frontend"]["replicas"])  # a real 0 stays 0
        self.assertIsNone(body["services"]["cartservice"]["replicas"])  # NaN is no data
        self.assertIsNone(body["services"]["frontend"]["cpu"])
        self.assertEqual(("PARTIAL", ["CPU_HTTP_500"]), (body["source"]["status"], body["source"]["errors"]))

    async def test_heal_history_and_logs_report_upstream_failure(self):
        FakeHttp.answers = {"/heal/history": ConnectionError("down")}
        response = await self.request("GET", "/api/heal-history", self.operator["secret"])
        self.assertEqual(503, response.status_code)
        self.assertNotIn("history", response.json())
        body = (await self.request("GET", "/api/logs", self.operator["secret"])).json()
        self.assertEqual("UNREACHABLE", body["sources"]["hephaestus"])

    async def test_chat_generates_no_reasoning(self):
        FakeHttp.answers = {"/heal/history": FakeResponse(200, {"history": [
            {"timestamp": "2026-10-21T00:00:00", "service": "frontend", "action": "SCALE_UP", "status": "SUCCESS"}]}),
            "container_cpu": FakeResponse(200, {"data": {"result": [{"metric": {"pod": "frontend-abc-def"}, "value": [0, "0.9"]}]}})}
        body = (await self.request("GET", "/api/chat", self.operator["secret"])).json()
        self.assertEqual([], body["chat"])
        self.assertEqual("UNAVAILABLE", body["status"])
        self.assertEqual([], FakeHttp.calls)  # nothing is read to compose a story

    async def test_results_need_the_reader_key_and_are_read_only(self):
        root, run = self.results_root()
        for token in (None, "wrong", self.operator["secret"]):
            response = await self.request("GET", "/api/results/runs", token)
            self.assertEqual(401, response.status_code)
            self.assertEqual({"detail": "UNAUTHORIZED"}, response.json())
        # The middleware itself refuses writes (READ_ONLY), also on paths no route serves, so a write
        # route added later under /api/results can never be reached.
        for method in ("POST", "PUT", "DELETE", "PATCH"):
            for path in (f"/api/results/runs/{run}", "/api/results/registry"):
                response = await self.request(method, path, self.reader["secret"])
                self.assertEqual((405, {"detail": "READ_ONLY"}), (response.status_code, response.json()))
        # The reader key opens nothing else.
        self.assertEqual(401, (await self.request("GET", "/api/status", self.reader["secret"])).status_code)
        # One shared secret for operator and reader is refused outright.
        (Path(self.tmp.name) / "reader.json").write_text(json.dumps(dict(self.reader, secret=self.operator["secret"])))
        response = await self.request("GET", "/api/results/runs", self.operator["secret"])
        self.assertEqual((503, {"detail": "KEY_SEPARATION"}), (response.status_code, response.json()))

    async def test_api_view_and_download_are_the_same_artifact(self):
        root, run = self.results_root()
        listed = (await self.request("GET", "/api/results/runs", self.reader["secret"])).json()
        self.assertEqual([run], [r["run_id"] for r in listed["runs"]])
        response = await self.request("GET", f"/api/results/runs/{run}?group=B2&run_id=run_{'f' * 32}", self.reader["secret"])
        self.assertEqual(200, response.status_code)
        self.assertEqual("no-store", response.headers["cache-control"])
        view = response.json()
        self.assertEqual((run, "B1", "RULES"), (view["run_id"], view["group"], view["mode"]))  # query cannot pick a group
        local = view_module().ResultsStore(root).view(run)
        view.pop("served_at")
        self.assertEqual(local, view)
        for name in ("score.json", "incidents.csv", "usage.csv"):
            response = await self.request("GET", f"/api/results/runs/{run}/files/{name}", self.reader["secret"])
            self.assertEqual(200, response.status_code)
            self.assertEqual((root / "b1_recovered" / name).read_bytes(), response.content)
            self.assertEqual(sha(response.content), response.headers["x-zd-sha256"])
        rows = list(csv.reader(io.StringIO((root / "b1_recovered/incidents.csv").read_text(encoding="utf-8"), newline="")))
        self.assertEqual(rows[1:], view["incidents"])

    async def test_bad_requests_return_codes_without_paths(self):
        root, run = self.results_root()
        cases = [(f"/api/results/runs/{run}/files/registry.json", 404), ("/api/results/runs/..%2F..%2Fregistry.json", 404),
                 (f"/api/results/runs/{run}/files/..%2Fregistry.json", 404), ("/api/results/runs/run_bad", 400),
                 ("/api/results/runs/run_" + "0" * 32, 404)]
        for path, status in cases:
            with self.subTest(path=path):
                response = await self.request("GET", path, self.reader["secret"])
                self.assertEqual(status, response.status_code, response.text)
                self.assertNotIn(str(root), response.text)
                self.assertNotIn(root.as_posix(), response.text)
        (root / "b1_recovered/score.json").write_bytes(b"{}")
        response = await self.request("GET", f"/api/results/runs/{run}", self.reader["secret"])
        self.assertEqual((422, {"detail": "ARTIFACT_HASH_MISMATCH"}), (response.status_code, response.json()))


class ResultsServer(unittest.IsolatedAsyncioTestCase):
    """serve-results: the real Nemesis app over an existing results root, read-only, results routes only."""
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.root = d / "s-root"
        self.root.mkdir()
        # Stands in for a closed run's root: two registered runs, not the fixture-server's SYNTHETIC set.
        self.runs = {}
        for name in ("b1_failed_timeout", "b0_controller"):
            score_case(name, self.root)
            self.runs[view_module().register(self.root, name)["run_id"]] = name
        self.reader = {"id": "reader", "purpose": "results-reader", "secret": "offline-results-reader-token-000000000"}
        (d / "reader.json").write_text(json.dumps(self.reader))
        self.env = patch.dict(os.environ, {})
        self.env.start()  # results_app sets the process env; restored after each test
        spec = importlib.util.spec_from_file_location("zer11_verify", ROOT / "infrastructure/scripts/verify-dashboard-baselines.py")
        self.verify = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.verify)
        self.before = self.verify.root_digest(self.root)
        self.siblings = sorted(p.name for p in d.iterdir())
        with patch.object(self.verify, "build_fixture_root", side_effect=AssertionError("fixture generated")):
            self.app, self.listed = self.verify.results_app(self.root, d / "reader.json")
        self.http = patch.object(httpx, "AsyncClient", FakeHttp)
        self.http.start()
        FakeHttp.answers, FakeHttp.calls = {}, []

    async def asyncTearDown(self):
        self.http.stop()
        self.env.stop()
        self.tmp.cleanup()

    async def request(self, method, path, token=None):
        headers = {"Authorization": "Bearer " + token} if token else {}
        async with REAL_CLIENT(transport=httpx.ASGITransport(app=self.app), base_url="http://offline") as client:
            return await client.request(method, path, headers=headers)

    async def test_serves_exactly_the_given_root_and_leaves_it_unchanged(self):
        registry = json.loads((self.root / "registry.json").read_bytes())
        self.assertEqual(set(self.runs), {r["run_id"] for r in self.listed})
        listed = (await self.request("GET", "/api/results/runs", self.reader["secret"])).json()["runs"]
        self.assertEqual({e["run_id"] for e in registry["runs"]}, {r["run_id"] for r in listed})
        for entry in registry["runs"]:
            view = (await self.request("GET", f"/api/results/runs/{entry['run_id']}", self.reader["secret"])).json()
            self.assertEqual(entry["sha256"], view["provenance"]["sha256"])
            for name in ("score.json", "incidents.csv"):
                body = await self.request("GET", f"/api/results/runs/{entry['run_id']}/files/{name}", self.reader["secret"])
                self.assertEqual((self.root / entry["dir"] / name).read_bytes(), body.content)
        page = await self.request("GET", "/dashboard/results.html")
        self.assertEqual(200, page.status_code)
        self.assertIn('src="results.js"', page.text)
        self.assertEqual(200, (await self.request("GET", "/dashboard/results.js")).status_code)
        self.assertEqual(401, (await self.request("GET", "/api/results/runs")).status_code)
        self.assertEqual((405, {"detail": "READ_ONLY"}), ((r := await self.request("POST", "/api/results/runs", self.reader["secret"])).status_code, r.json()))
        self.assertEqual(self.before, self.verify.root_digest(self.root))
        self.assertEqual(self.siblings, sorted(p.name for p in Path(self.tmp.name).iterdir()))

    async def test_other_routes_and_startup_never_reach_upstreams(self):
        self.assertEqual([], self.app.router.on_startup)  # no Kafka results consumer
        for method, path in [("GET", "/api/status"), ("GET", "/api/logs"), ("GET", "/api/heal-history"), ("POST", "/api/chat"),
                             ("POST", "/attack"), ("GET", "/healthz"), ("GET", "/dashboard/index.html"), ("POST", "/api/reset")]:
            with self.subTest(path=path):
                response = await self.request(method, path, self.reader["secret"])
                self.assertEqual((404, {"detail": "NOT_SERVED_IN_RESULTS_MODE"}), (response.status_code, response.json()))
        self.assertEqual([], FakeHttp.calls)

    def test_cli_receipt_records_the_root_at_start_and_exit(self):
        import uvicorn
        d = Path(self.tmp.name)
        args = lambda receipt: type("Args", (), {"root": str(self.root), "reader_key_file": str(d / "reader.json"),
                                                 "operator_key_file": None, "port": 8799, "receipt": str(receipt)})()
        started = []
        with patch.object(uvicorn, "run", side_effect=lambda app, **kw: started.append(json.loads((d / "a.json").read_text()))), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, self.verify.serve_results(args(d / "a.json")))
        self.assertEqual((False, self.before), (started[0]["stopped"], started[0]["root_files_sha256"]))  # on disk before serving
        receipt = json.loads((d / "a.json").read_text())
        self.assertEqual((True, True, [], sorted(self.runs)), (receipt["stopped"], receipt["root_unchanged"], receipt["changed"], sorted(receipt["runs"])))
        # A file changed while serving is reported and fails the command.
        touched = self.root / "b0_controller" / "usage.csv"
        with patch.object(uvicorn, "run", side_effect=lambda app, **kw: touched.write_bytes(touched.read_bytes() + b"x")), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(5, self.verify.serve_results(args(d / "b.json")))
        self.assertEqual(["b0_controller/usage.csv"], json.loads((d / "b.json").read_text())["changed"])
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(4, self.verify.serve_results(args(d / "b.json")))  # an existing receipt is never overwritten

    def test_ctrl_c_still_records_root_integrity_and_reports_changes(self):
        import uvicorn
        d = Path(self.tmp.name)
        for changed in (False, True):
            receipt = d / ("interrupt-changed.json" if changed else "interrupt-clean.json")
            args = type("Args", (), {"root": str(self.root), "reader_key_file": str(d / "reader.json"),
                                     "operator_key_file": None, "port": 8799, "receipt": str(receipt)})()
            def stop(app, **kw):
                if changed:
                    touched = self.root / "b0_controller" / "usage.csv"
                    touched.write_bytes(touched.read_bytes() + b"x")
                raise KeyboardInterrupt
            with patch.object(uvicorn, "run", side_effect=stop), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(5 if changed else 0, self.verify.serve_results(args))
            result = json.loads(receipt.read_text())
            self.assertTrue(result["stopped"])
            self.assertEqual(not changed, result["root_unchanged"])
            self.assertEqual(["b0_controller/usage.csv"] if changed else [], result["changed"])

    def test_refuses_a_root_without_a_registry_or_a_relative_root(self):
        empty = Path(self.tmp.name) / "empty"
        empty.mkdir()
        with self.assertRaises(view_module().ResultError) as raised:
            self.verify.results_app(empty, Path(self.tmp.name) / "reader.json")
        self.assertEqual("REGISTRY_MISSING", raised.exception.reason)
        with self.assertRaises(SystemExit):
            self.verify.results_app(Path("relative"), Path(self.tmp.name) / "reader.json")


class RuntimePlan(unittest.TestCase):
    """G-ZER11-RT1 budget (verify-dashboard-baselines.py plan-check) against the scorer's coverage rules."""
    def setUp(self):
        spec = importlib.util.spec_from_file_location("zer11_verify_plan", ROOT / "infrastructure/scripts/verify-dashboard-baselines.py")
        self.verify = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.verify)

    def plan(self, change):
        plan = copy.deepcopy(self.verify.RT1)
        change(plan)
        return self.verify.plan_matrix(plan)["problems"]

    def test_budget_covers_timeout_no_effect_and_verification(self):
        m = self.verify.plan_matrix()
        self.assertEqual([], m["problems"])
        f = m["f01_pilot"]
        # The PILOT inputs stay the ZER-32 3.6 illustrative set; the plan does not relax them.
        self.assertEqual({"delta_s": 1, "k": 3, "s_s": 30, "gap_s": 2, "cap_rec_s": 600}, {k: f[k] for k in ("delta_s", "k", "s_s", "gap_s", "cap_rec_s")})
        for name, t in m["trials"].items():
            with self.subTest(trial=name):
                after_effect = t["trial_max_s"] - self.verify.RT1["trials"][name]["baseline_s"] - m["w_eff_s"]
                self.assertGreaterEqual(after_effect, f["cap_rec_s"] + f["s_s"])  # TIMEOUT coverable, S kept at the cap
                self.assertGreaterEqual(t["trial_max_s"], m["w_eff_s"])           # NO_EFFECT coverable
                self.assertEqual(33, t["verify_min_samples"])
                self.assertGreaterEqual(t["probe_max_samples"], t["probe_max_duration_s"] // f["delta_s"])
        self.assertEqual((1, False), (m["totals"]["frontend_pod_deletes"], m["totals"]["p6"]))
        self.assertLessEqual(m["totals"]["worst_case_s"], m["totals"]["cap_s"])

    def test_the_reviewed_inconsistencies_are_rejected(self):
        # ZR11-02: the first plan's 35 min total, 30 transactions per trial and an enabled P6.
        self.assertTrue(self.plan(lambda p: p["caps"].update(total_s=35 * 60)))
        self.assertTrue(self.plan(lambda p: p["caps"].update(probe_samples_per_trial=30)))
        self.assertTrue(self.plan(lambda p: p.update(p6=True)))
        self.assertTrue(self.plan(lambda p: p["trials"]["B0-HPA"].update(fault="delete 1 frontend pod")))

    def test_runbook_quotes_the_computed_numbers(self):
        m = self.verify.plan_matrix()
        text = (ROOT / "docs/runbooks/dashboard-and-baselines.md").read_text(encoding="utf-8")
        section = text[text.index("### 5.3"):text.index("### 5.4")]
        t = m["trials"]["B0-CTRL"]
        for value in (t["trial_max_s"], t["probe_max_samples"], t["probe_max_requests"], t["verify_min_samples"],
                      m["totals"]["probe_samples"], m["totals"]["probe_requests"], m["totals"]["worst_case_s"],
                      m["totals"]["cap_s"], m["totals"]["load_requests"]):
            self.assertIn(str(value), section)
        self.assertIn("KHÔNG thuộc RT1", text)


class StaticPages(unittest.TestCase):
    def test_console_has_no_kpi_path_or_synthetic_numbers(self):
        app = (STATIC / "app.js").read_text(encoding="utf-8")
        index = (STATIC / "index.html").read_text(encoding="utf-8")
        for forbidden in ("Math.random", "updateSREStats", "12.3s", "25.6s", "100.0%", "100.00%", "/api/heal-history", "formatLogJson"):
            self.assertNotIn(forbidden, app)
        self.assertNotIn('id="sre-', index)
        # Untrusted text (logs, services, reasoning) never goes through innerHTML with interpolation.
        self.assertEqual([], re.findall(r"innerHTML\s*[+]?=\s*`[^`]*\$\{", app))

    def test_results_page_is_get_only_text_only_and_self_contained(self):
        js = (STATIC / "results.js").read_text(encoding="utf-8")
        html = (STATIC / "results.html").read_text(encoding="utf-8")
        self.assertNotRegex(js, r"innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval\(|new Function")
        self.assertNotRegex(js, r"\b(POST|PUT|DELETE|PATCH)\b")
        self.assertEqual(set(re.findall(r'method:\s*"([A-Z]+)"', js)), {"GET"})
        self.assertNotRegex(js, r"localStorage|sessionStorage|document\.cookie")
        for target in ("/attack", "/heal", "/api/reset", "/api/chat", "llm"):
            self.assertNotIn(target, js)
        self.assertNotRegex(html, r"<script[^>]+src=\"https?:|<link[^>]+href=\"https?:")

    def test_refresh_keeps_stale_only_for_transient_failures(self):
        # results.js itself in a Node VM (tests/results_page_vm.cjs): after a good view, an integrity,
        # access, unregistered or configuration answer clears the cached view; only a transient outage
        # keeps it as STALE; late answers of a previous run or key are dropped.
        node = shutil.which("node")
        self.assertIsNotNone(node, "node is required for the results page regression")
        done = subprocess.run([node, str(ROOT / "tests/results_page_vm.cjs"), str(STATIC / "results.js")],
                              capture_output=True, text=True, timeout=120)
        report = json.loads(done.stdout)
        self.assertGreaterEqual(len(report["cases"]), 18)
        for case in report["cases"]:
            with self.subTest(case=case["name"]):
                self.assertTrue(case["ok"], json.dumps(case["detail"]))
        self.assertEqual(0, done.returncode, done.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
