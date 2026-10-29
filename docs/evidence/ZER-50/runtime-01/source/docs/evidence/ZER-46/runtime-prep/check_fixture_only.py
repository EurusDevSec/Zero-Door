"""Offline checks that approval separation never converts Boutique failure to success."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("zer46_fixture_only_check", Path(__file__).with_name("run_fixture_only.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Boundary(unittest.TestCase):
    def test_failed_boutique_is_recorded_unchanged_and_not_a_fixture_gate(self):
        lab = module.Lab(); lab.save = Mock()
        row = {"healthy": False, "result": {"ok": False, "detail": "TIMEOUT"}}
        lab.probe = Mock(return_value=row)
        lab.check_business_baseline()
        actual = lab.save.call_args.args[1]
        self.assertIs(actual["result"], row)
        self.assertIs(actual["is_fixture_admission_gate"], False)
        self.assertIs(actual["formal_r1_health_claim"], False)

    def test_unresolved_cart_cleanup_still_blocks_the_attempt(self):
        lab = module.Lab(); lab.probe = Mock(side_effect=RuntimeError("BUSINESS_CLEANUP_UNRESOLVED"))
        with self.assertRaisesRegex(RuntimeError, "BUSINESS_CLEANUP_UNRESOLVED"):
            lab.check_business_baseline()

    def test_cached_only_mode_cannot_call_parent_puller(self):
        lab = module.Lab(); lab.command = Mock()
        with patch.object(module.full.Lab, "ensure_cache", side_effect=AssertionError("no pull path")):
            lab.ensure_cache()
        self.assertEqual(lab.command.call_count, 2)
        self.assertTrue(all("inspect" in c.args[0] and "pull" not in c.args[0] for c in lab.command.call_args_list))

    def test_resource_cleanup_does_not_mean_boutique_or_lab_pass(self):
        lab = module.Lab(); lab.save = Mock(); lab.validated = True
        report = {"errors": [], "namespace_absent": True, "specs_preserved": True, "restarts_preserved": True,
                  "policy_cleanup_observed": True, "business_2_of_2": False, "verdict": "INCOMPLETE"}
        with patch.object(module.full.Lab, "cleanup", return_value=report):
            result = lab.cleanup()
        self.assertEqual(result["component_resource_verdict"], "CLEAN")
        self.assertEqual(result["lab_readiness"], "NOT_MET_BOUTIQUE_NOT_HEALTHY")
        self.assertFalse(result["boutique_recovery_claim"])

    def test_missing_policy_readback_or_foreign_errors_never_pass_cleanup(self):
        for changes in ({"policy_cleanup_observed": False}, {"errors": ["CLEANUP_NAMESPACE_OWNER"]}):
            lab = module.Lab(); lab.save = Mock(); lab.validated = True
            report = {"errors": [], "namespace_absent": True, "specs_preserved": True, "restarts_preserved": True,
                      "policy_cleanup_observed": True, "business_2_of_2": False, **changes}
            with patch.object(module.full.Lab, "cleanup", return_value=report):
                self.assertEqual(lab.cleanup()["component_resource_verdict"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
