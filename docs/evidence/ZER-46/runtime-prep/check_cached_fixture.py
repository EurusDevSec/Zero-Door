"""Offline admission checks; cache mismatch never falls through to build/import/pull."""
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("zer46_cached_check", Path(__file__).with_name("run_cached_fixture.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Cached(unittest.TestCase):
    def fixture(self, wrong=False, proxy=True):
        lab = module.Lab(); lab.save = Mock()
        images = [{"repoTags": ["docker.io/library/" + module.TAG], "id": "wrong" if wrong else module.NODE_ID}]
        if proxy: images.append({"repoDigests": [module.PROXY_DIGEST], "id": "proxy-config"})
        lab.command = Mock(side_effect=[subprocess.CompletedProcess([], 0, (module.HOST_ID + "\n").encode(), b""),
            subprocess.CompletedProcess([], 0, json.dumps({"images": images}).encode(), b"")])
        return lab

    def test_matching_artifact_uses_only_inspection(self):
        lab = self.fixture()
        with patch.object(module.parent.full.Lab, "prepare_fixture_image", side_effect=AssertionError("no builder")):
            lab.prepare_fixture_image(module.TAG)
        self.assertEqual(lab.command.call_count, 2)
        self.assertTrue(all(not any(x in {"build", "pull", "import", "run", "create"} for x in c.args[0]) for c in lab.command.call_args_list))
        self.assertEqual(lab.save.call_args.args[0], "cache-admission.json")

    def test_wrong_config_or_missing_proxy_is_a_stop_not_fallback(self):
        for lab in (self.fixture(wrong=True), self.fixture(proxy=False)):
            with self.assertRaisesRegex(RuntimeError, "CACHED_NODE_DIGEST"):
                lab.prepare_fixture_image(module.TAG)
            lab.save.assert_not_called()

    def test_changed_tag_rejected_before_any_command(self):
        lab = self.fixture()
        with self.assertRaisesRegex(RuntimeError, "CACHED_TAG_PIN"):
            lab.prepare_fixture_image("zer46-fixture:other")
        lab.command.assert_not_called()

    def test_cache_preflight_has_no_unnecessary_host_base_requirement(self):
        lab = self.fixture()
        lab.ensure_cache()
        calls = [c.args[0] for c in lab.command.call_args_list]
        self.assertEqual(len(calls), 2)
        self.assertTrue(all("gcr.io/distroless" not in " ".join(args) for args in calls))

    def test_all_workloads_in_renderer_forbid_implicit_pulls(self):
        docs = module.parent.full.renderer.render("zer46-0123456789ab", "run_" + "1" * 32,
                                                  "trl_" + "2" * 32, "10.42.1.12")
        for doc in docs:
            if doc["kind"] == "Deployment": pod = doc["spec"]["template"]["spec"]
            elif doc["kind"] == "Pod": pod = doc["spec"]
            else: continue
            self.assertTrue(all(c["imagePullPolicy"] == "Never" for c in pod["containers"]))


if __name__ == "__main__":
    unittest.main()
