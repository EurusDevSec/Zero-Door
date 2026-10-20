"""ZER-10/ZER-38 package checker: file hashes, protected sources, append-only notes and Git scope.

  python -B docs/evidence/ZER-10/check_package.py --check          verify against fix-01/manifest.json
  python -B docs/evidence/ZER-10/check_package.py --write          create fix-01/manifest.json once (refuses to overwrite)

fix-01 (Codex review CHANGES_REQUIRED): the first handoff manifest (manifest.json, SHA-256 b3a33293...)
stays as it was and is the base; fix-01/manifest.json records every package file now plus the delta
(changed/added) against that base. The Codex review report and its evidence are read-only here.

Offline; reads files and `git status`. It does not run tests (see verification.md for those commands).
"""
import argparse
import hashlib
import json
from pathlib import Path
# Fixed `git status`/`git diff` with list arguments, no shell, no external input (B404/B603/B607).
import subprocess  # nosec B404
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = HERE / "manifest.json"
BASE_SHA256 = "b3a33293105ee44f0e772405ca40ddea1b4820ca95cea035da93fdbc6b169292"
MANIFEST = HERE / "fix-01" / "manifest.json"

PACKAGE = [
    *(f"agent-orchestrator/measurement/{n}" for n in ("__init__.py", "__main__.py", "config.py", "clock.py", "flows.py", "sink.py",
                                                      "probe.py", "recovery.py", "raw.py", "scorer.py", "metrics.py", "output.py")),
    "infrastructure/scripts/verify-measurement.py", "infrastructure/scripts/verify-measurement.sh",
    *(f"tests/test_measurement_{n}.py" for n in ("probe", "recovery", "scorer", "metrics", "cli")),
    "tests/fixtures/zer10/builder.py", "tests/fixtures/zer10/expected.json",
    "tests/fixtures/zer10/plan-synthetic-boutique.json", "tests/fixtures/zer10/plan-synthetic-fixture.json",
    ".github/workflows/ci.yml", "docs/design/r1-measurement.md", "docs/runbooks/independent-measurement.md",
    "docs/evidence/ZER-10/verification.md", "docs/evidence/ZER-10/check_mutants.py", "docs/evidence/ZER-10/crosscheck_zer37.py",
    "docs/evidence/ZER-10/check_package.py", "docs/evidence/ZER-10/fix-01/retest_counterexamples.py",
]
RESULTS = ("docs/evidence/ZER-10/results", "docs/evidence/ZER-10/fix-01/results")
# Read-only sources at intake (scratch/zer10/intake-baseline.json, 20/10/2026); must keep these hashes.
PROTECTED = {
    "AGENTS.md": "fe18d0003c865a021eb7eb8a2432ea290b034deec5cad3cb5c1cd338be88d50e",
    "docs/delivery/README.md": "c7b9f0f8673359cce4be9d3bb0a4517925060b4b98345de1d8f5edc3f0a220b4",
    "docs/delivery/WORKFLOW.md": "ded0fdee2473ce8cac32f994f4139ee59e241e13fc48528b0fe42c026ef15ffb",
    "docs/delivery/WORKING-AGREEMENT.md": "fc34c9ae5fc3f6edfd1197c79b5bee380c0b9ec1b3a365df363405084264bc87",
    "docs/delivery/milestones/R1-measurement/README.md": "b86437ac75848ad6b2e11bb83c8e07db121dcb686cff929cca37851aaf359324",
    "docs/delivery/milestones/R1-measurement/event-contract.md": "9b3fd2be6f3c91eead340898c66df54aef9d2589fa220b06d28fa8f51c23ff99",
    "docs/delivery/milestones/R1-measurement/guards-and-ci.md": "033baea65de6c7ab2f2fd807b67780a387afd285f15945bcc67412930298ee31",
    "docs/evidence/ZER-32/requirements-and-kpi.md": "a5579b900d7f46f34dd95060f28ba179c4d8d94bbbacccdc481f640e4ba3a24c",
    "docs/evidence/ZER-8/research-design.md": "cfaec5227972e85a62df205782e71ba915931aadb437073a4c09b40386305db8",
    "docs/design/r1-event-contract.md": "fe09beb590ecc7fd82452e8108215565558e74886765da215954450415fe91fc",
    "docs/delivery/milestones/R2-chaos-scenarios/sqli-fixture.md": "02dd1d0a3a56e209c88ebd619eb438aad2d8998e4072153af2aecae0f8c16c78",
    "agent-orchestrator/event_pipeline/adapters.py": "10ca7c699091c390c6ac1fec524bc5fbdfb64031fe8ac021a13d631259fa4ef9",
    "agent-orchestrator/event_pipeline/audit.py": "b7ebc3195cd72c424e95f35f326fbab117dabc11ba319064305869720c5eb369",
    "agent-orchestrator/event_pipeline/client.py": "b2c3057dfe74efa60b53eaaf80147f5685d2b177c0a02d7a65a43b451ec59b28",
    "agent-orchestrator/event_pipeline/contract.py": "5c4a890e1cb4b72431a63641061f66b3887111afa2d54ea0e83332160cab7136",
    "agent-orchestrator/event_pipeline/gateway.py": "74fef63be94c571b9f033bf9717931b1b2fe429b1c1e4bd8552c4e3eac93b4d9",
    "agent-orchestrator/event_pipeline/requirements.lock": "92896b1f11b6b7787bfdf01fcecd6771007b38f6a4031c2158a5b5a1e40a1069",
    "agent-orchestrator/event_pipeline/requirements.txt": "f8bf3f588cde491ec1e92b5e6d045ad2a0b40fa045a89db9be3493f9afb88b2d",
    "agent-orchestrator/event_pipeline/store.py": "de30c0acd10679da38b3864c562e184fa4cddb16ee3c3a3d2befd31d68f157c6",
    "agent-orchestrator/event_pipeline/telemetry.py": "d0cfcb9cf6d85c6109dabd86f396e76784443b1232db4510ac3bd7e247735fb3",
    "agent-orchestrator/event_pipeline/__init__.py": "d9f668a9ea4218cfe61e859c7e6e64772604f1c81cc853047c2268de5b9f5482",
    "docs/evidence/ZER-37/check_contract.py": "d645b36cbed8409cfad4c6fcb57e183b61ad17b98a9d16707c185747c9dadbe1",
    "docs/evidence/ZER-37/fixtures.json": "c9144d7500f11a468f8d9b2f30bb3ee6ab9e1b47364890932ef5a8c78e2382a2",
    "docs/evidence/ZER-37/independent_checks.py": "e1ab3d4835082277fa124bda12c74c2e1c44ccd67075f3853f16ce75619c7196",
    "docs/evidence/ZER-37/verification.md": "3bad07e23fcae71dea9a27dd608c480d5059569523861e945a029ec01c9e319f",
    "docs/evidence/ZER-37/verify_release.py": "24e61c8bffdcfa87c0ce90279651530e142a33c99eac45222d83bea1acd2cdb3",
    "docs/runbooks/r1-event-pipeline.md": "ed6617d41224ea55bc33eae7c50bb6b9e06f4e1dcb03ca582b4e93fa5acee0fa",
    # Out of package scope, present before fix-01 (Codex review §1): kept as it was.
    "docs/detail_zero-door.md": None,
}
# Codex review report and evidence (fix-01 intake, scratch/zer10/claude/fix-01/intake.json): read-only.
REVIEW = {
    "docs/evidence/ZER-10/codex-review.md": "9f0e9b495a1af50c0ea47f96f7546cf06bbd22adbe54ac9172c106c3dafc4237",
}
REVIEW_DIR = "docs/evidence/ZER-10/codex-review"
# Notes keep their fix-01 intake bytes as a prefix (note, appended) or suffix (NOW, pointer on top).
APPEND_ONLY = {"docs/delivery/milestones/R1-measurement/probes-and-metrics.md": (25690, "prefix"),
               "docs/delivery/NOW.md": (67106, "suffix")}
DIRTY_BEFORE = {"AGENTS.md", "docs/delivery/NOW.md", "docs/delivery/README.md", "docs/delivery/WORKFLOW.md",
                "docs/delivery/milestones/R1-measurement/README.md", "docs/delivery/milestones/R1-measurement/event-contract.md",
                "docs/delivery/milestones/R1-measurement/guards-and-ci.md", "docs/delivery/milestones/R1-measurement/probes-and-metrics.md",
                "docs/delivery/WORKING-AGREEMENT.md", "docs/detail_zero-door.md"}
INTAKE = ROOT / "scratch/zer10/claude/fix-01/intake.json"


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def package_files():
    files = list(PACKAGE)
    for folder in RESULTS:
        files += sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / folder).rglob("*") if p.is_file())
    return files


def review_files():
    return sorted([*REVIEW] + [p.relative_to(ROOT).as_posix() for p in (ROOT / REVIEW_DIR).rglob("*") if p.is_file()])


def intake():
    """fix-01 intake: hashes of the Codex review files and the note/NOW sizes and digests at intake."""
    if not INTAKE.is_file():
        return None
    return json.loads(INTAKE.read_text(encoding="utf-8"))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout  # nosec B603 B607


def check():
    problems = []
    if sha(BASE.relative_to(ROOT)) != BASE_SHA256:
        problems.append("base manifest.json (first handoff) changed")
    manifest = json.loads(MANIFEST.read_text())
    for path, digest in manifest["files"].items():
        if not (ROOT / path).is_file():
            problems.append(f"missing {path}")
        elif sha(path) != digest:
            problems.append(f"hash changed {path}")
    problems += [f"not in manifest {p}" for p in sorted(set(package_files()) - set(manifest["files"]))]
    for path, digest in PROTECTED.items():
        if digest is None:
            digest = manifest["outside_scope"].get(path)
        if sha(path) != digest:
            problems.append(f"protected source changed {path}")
    review = manifest["review_read_only"]
    for path in sorted(set(review_files()) | set(review)):
        if path not in review:
            problems.append(f"new file in Codex review evidence {path}")
        elif not (ROOT / path).is_file() or sha(path) != review[path]:
            problems.append(f"Codex review evidence changed {path}")
    for path, (size, where) in APPEND_ONLY.items():
        data = (ROOT / path).read_bytes()
        part = data[:size] if where == "prefix" else data[-size:]
        if hashlib.sha256(part).hexdigest() != manifest["append_only"][path]:
            problems.append(f"{path}: intake content is not preserved as the {where}")
    try:
        status = git("status", "--porcelain", "--untracked-files=all")
        changed = {line[3:].strip().strip('"') for line in status.splitlines() if line.strip()}
        allowed = DIRTY_BEFORE | set(manifest["files"]) | set(review) | {
            BASE.relative_to(ROOT).as_posix(), MANIFEST.relative_to(ROOT).as_posix()}
        problems += [f"outside package scope: {p}" for p in sorted(changed - allowed)]
        if git("diff", "--cached", "--name-only").strip():
            problems.append("staged changes present")
    except (OSError, subprocess.CalledProcessError):
        problems.append("git status unavailable (scope not checked)")
    print(json.dumps({"files": len(manifest["files"]), "changed_vs_base": len(manifest["delta"]["changed"]),
                      "added_vs_base": len(manifest["delta"]["added"]), "protected": len(PROTECTED),
                      "review_read_only": len(review), "problems": problems}, indent=1))
    return 1 if problems else 0


def write():
    taken = intake()
    if taken is None:
        raise SystemExit("fix-01 intake (scratch/zer10/claude/fix-01/intake.json) is needed to record the review baseline")
    review = {p: sha(p) for p in review_files()}
    if review != taken["review_read_only"]:
        raise SystemExit("Codex review files differ from the fix-01 intake; refusing to record them")
    base = json.loads(BASE.read_text())["files"]
    files = {p: sha(p) for p in package_files()}
    append_only = {}
    for path, (size, where) in APPEND_ONLY.items():
        data = (ROOT / path).read_bytes()
        append_only[path] = hashlib.sha256(data[:size] if where == "prefix" else data[-size:]).hexdigest()
        at_intake = taken["note_sha256"] if where == "prefix" else taken["now_sha256"]
        if append_only[path] != at_intake:
            raise SystemExit(f"{path}: the fix-01 intake content is not preserved as the {where}")
    delta = {"changed": sorted(p for p in files if p in base and base[p] != files[p]),
             "added": sorted(p for p in files if p not in base),
             "removed": sorted(p for p in base if p not in files),
             "unchanged": len([p for p in files if base.get(p) == files[p]])}
    with open(MANIFEST, "x") as handle:
        json.dump({"package": "ZER-10 + ZER-38 fix-01 offline (Claude, 20/10/2026)", "base": "55200c9 (tree = 0babf90)",
                   "base_manifest": {"path": BASE.relative_to(ROOT).as_posix(), "sha256": BASE_SHA256},
                   "review": "docs/evidence/ZER-10/codex-review.md (CHANGES_REQUIRED)", "files": files, "delta": delta,
                   "review_read_only": review, "append_only": append_only,
                   "outside_scope": {p: sha(p) for p, d in PROTECTED.items() if d is None}}, handle, indent=1, sort_keys=True)
        handle.write("\n")
    print(f"wrote {MANIFEST.relative_to(ROOT)} with {len(files)} files; delta {len(delta['changed'])} changed, {len(delta['added'])} added")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    sys.exit(write() if parser.parse_args().write else check())
