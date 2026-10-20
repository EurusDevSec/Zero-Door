"""Verify the sealed fix-03 package offline. Reads hashes/Git only; never regenerates evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess  # nosec B404 - fixed read-only Git commands, no shell

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(local=False):
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    problems = []
    labels = ["files", "protected", "historical_read_only"] + (["local_only_protected"] if local else [])
    for label in labels:
        for path, expected in manifest[label].items():
            target = ROOT / path
            target.resolve().relative_to(ROOT.resolve())
            if not target.is_file() or sha(target) != expected:
                problems.append(f"{label}: {path}")
    before = json.loads((HERE / "before.json").read_text(encoding="utf-8"))
    old = json.loads((HERE.parent / "fix-02" / "manifest.json").read_text(encoding="utf-8"))["files"]
    for path, digest in before.items():
        if old.get(path) != digest or sha(HERE / "before" / path) != digest:
            problems.append(f"snapshot: {path}")
    for path, info in manifest["append_only"].items():
        data = (ROOT / path).read_bytes()
        if info["where"] == "contains":
            part = info["text"].encode()
            if part not in data:
                problems.append(f"checkpoint missing: {path}")
        else:
            part = data[:info["bytes"]] if info["where"] == "prefix" else data[-info["bytes"]:]
        if hashlib.sha256(part).hexdigest() != info["sha256"]:
            problems.append(f"append-only: {path}")
    known = set(manifest["files"]) | set(manifest["protected"]) | set(manifest["historical_read_only"]) | set(manifest["append_only"]) | set(manifest["local_only_protected"])
    known |= {"docs/evidence/ZER-10/fix-03/manifest.json", *manifest["existing_dirty"]}
    status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT,
                            check=True, capture_output=True, text=True).stdout  # nosec B603 B607
    for row in status.splitlines():
        path = row[3:].strip('"')
        if path not in known:
            problems.append(f"outside scope: {path}")
    diff = subprocess.run(["git", "diff", "--check"], cwd=ROOT,
                          capture_output=True, text=True)  # nosec B603 B607
    if diff.returncode:
        problems.append("git diff --check")
    print(json.dumps({"files": len(manifest["files"]), "protected": len(manifest["protected"]),
                      "historical": len(manifest["historical_read_only"]), "snapshot": len(before),
                      "problems": problems}, indent=2))
    return bool(problems)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--local", action="store_true", help="also verify owner's unpublished pre-existing files")
    args = parser.parse_args()
    raise SystemExit(check(args.local))
