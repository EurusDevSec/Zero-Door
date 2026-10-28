"""Approved fixture-only component protocol. Boutique stays an observed outcome, never fabricated PASS.
No effects on import. The separate approval file/hash and explicit --execute are mandatory.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-04"
AUTHORIZATION_FILE = ROOT / "docs/evidence/ZER-46/runtime-prep/fixture-only-authorization.json"
spec = importlib.util.spec_from_file_location("zer46_fixture_parent", Path(__file__).with_name("run_component.py"))
full = importlib.util.module_from_spec(spec)
spec.loader.exec_module(full)
full.OUT = OUT
full.base.OUT = OUT


class Lab(full.Lab):
    def ensure_cache(self):
        # The new approval permits no additional pulls; inspect the two exact cached refs only.
        full.base.Lab.ensure_cache(self)

    def check_business_baseline(self):
        print("BOUTIQUE_OBSERVER_BEFORE_NOT_FIXTURE_GATE", flush=True)
        observed = self.probe()  # cleanup failure still raises: no abandoned observer-owned cart.
        self.save("boutique-before-observed.json", {"at": time.time(), "result": observed,
            "is_fixture_admission_gate": False, "formal_r1_health_claim": False})

    def cleanup(self):
        report = super().cleanup()
        self.save("cleanup-original-aggregate.json", report)
        resource_ok = not report["errors"] and all(report.get(k) for k in
            ("namespace_absent", "specs_preserved", "restarts_preserved"))
        if self.validated:
            resource_ok = resource_ok and report.get("policy_cleanup_observed") is True
        report["component_resource_verdict"] = "CLEAN" if resource_ok else "INCOMPLETE"
        report["lab_readiness"] = "NOT_VERIFIED" if report.get("business_2_of_2") else "NOT_MET_BOUTIQUE_NOT_HEALTHY"
        report["verdict"] = "CLEAN_OWNED_RESOURCES_ONLY" if resource_ok else "INCOMPLETE"
        report["boutique_recovery_claim"] = False
        self.save("cleanup.json", report)
        return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute: parser.error("explicit --execute required")
    if (OUT / "started.json").exists() or (OUT / "acceptance.json").exists():
        parser.error("one attempt only; no automatic retry")
    authorization = json.loads(AUTHORIZATION_FILE.read_text())
    if authorization["status"] != "APPROVED" or hashlib.sha256((ROOT / authorization["proposal"]).read_bytes()).hexdigest() != authorization["proposalSha256"]:
        parser.error("missing or drifted approval")
    lab = Lab()
    lab.save("authorization.json", authorization)
    error = None
    try:
        lab.execute()
        lab.component()  # actual fixture baseline, two sources, spoof, isolation, block/TTL/restart.
    except Exception as failure:
        error = str(failure)
        lab.save("failure.json", {"at": time.time(), "reason": error})
        print("STOP", error, flush=True)
    finally:
        cleanup = lab.cleanup()
    if lab.failure:
        error = error or "GUARD_FAILURE:" + repr(lab.failure)
        lab.save("failure.json", {"at": time.time(), "reason": error, "guard_failures": list(lab.failure)})
    observed = lab.validated and error is None and cleanup["component_resource_verdict"] == "CLEAN"
    lab.save("acceptance.json", {"component_observed": observed, "error": error,
        "component_resource_cleanup": cleanup["component_resource_verdict"], "lab_readiness": cleanup["lab_readiness"],
        "status": "COMPONENT_RECONCILE_REQUIRED" if observed else "NOT_MET",
        "boutique_pass": False, "formal_kpi_pass": False, "issue_done": False,
        "elapsed_seconds": time.time() - lab.started})
    return 0 if observed else 1


if __name__ == "__main__":
    sys.exit(main())
