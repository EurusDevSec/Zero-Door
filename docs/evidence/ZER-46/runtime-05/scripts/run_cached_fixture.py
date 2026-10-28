"""Prepared cached-only protocol. A new approval is required; no build/import/pull path is used.
Default import is inert. The existing immutable fixture and proxy must both be present on server-0.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-05"
spec = importlib.util.spec_from_file_location("zer46_cached_parent", Path(__file__).with_name("run_fixture_only.py"))
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)
parent.OUT = OUT
parent.full.OUT = OUT
parent.full.base.OUT = OUT
parent.AUTHORIZATION_FILE = ROOT / "docs/evidence/ZER-46/runtime-prep/cached-fixture-authorization.json"

TAG = "zer46-fixture:24662046a33f"
HOST_ID = "sha256:d85043c06db6a60c98cddb53a1545f6e053b6def409d43b156179a625df55274"
NODE_ID = "sha256:d85cb46078ed6e928af880acb2e1927056783ad03a1d18b30a69b8de2a922a16"
PROXY_DIGEST = "docker.io/library/traefik@sha256:575fa15b135078fe5e50aa847987d96dbddd7b093c172429618404df73f3fa7c"


class Lab(parent.Lab):
    def ensure_cache(self):
        # Host base-image names are irrelevant when no build is permitted. Verify the actual artifact
        # and both node-resident runtime images instead, before even the Boutique observer is sent.
        self.prepare_fixture_image(TAG)

    def prepare_fixture_image(self, tag):
        if tag != TAG: raise RuntimeError("CACHED_TAG_PIN")
        original = json.loads((ROOT / "docs/evidence/ZER-46/runtime-04/source-manifest.json").read_text())
        for path in ("services/sqli-fixture/app.py", "services/sqli-fixture/containment.py",
                     "services/sqli-fixture/Dockerfile", "services/sqli-fixture/seed.json"):
            if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != original["componentSource"]["source"][path]:
                raise RuntimeError("BUILT_SOURCE_DRIFT")
        host = self.command(["docker", "--context", "desktop-linux", "image", "inspect", TAG, "--format", "{{.Id}}"])
        if host.stdout.decode().strip() != HOST_ID: raise RuntimeError("CACHED_HOST_DIGEST")
        raw = self.command(["docker", "--context", "desktop-linux", "exec", "k3d-zero-door-server-0", "crictl", "images", "-o", "json"])
        images = json.loads(raw.stdout)["images"]
        fixture = [x for x in images if "docker.io/library/" + TAG in x.get("repoTags", [])]
        proxy = [x for x in images if PROXY_DIGEST in x.get("repoDigests", [])]
        if len(fixture) != 1 or fixture[0]["id"] != NODE_ID or len(proxy) != 1:
            raise RuntimeError("CACHED_NODE_DIGEST")
        self.save("cache-admission.json", {"at": time.time(), "host_image_id": HOST_ID,
            "fixture_node_image": fixture[0], "proxy_node_image": proxy[0], "builds": 0, "imports": 0, "pulls": 0})
        print("CACHED_IMAGE_DIGESTS_CONFIRMED_NO_BUILD_IMPORT_PULL", flush=True)

    def capture_guard_stop(self):
        # Only known attempt-owned Pod UUIDs; no process memory, env, credentials or other Pod content.
        try:
            latest_path = OUT / "watch-latest.json"
            latest = json.loads(latest_path.read_text()) if latest_path.exists() else {"items": []}
            ids = [p["metadata"]["uid"] for p in latest["items"] if p["kind"] == "Pod" and
                p["metadata"]["namespace"] == "zd-sqli-lab" and p["metadata"]["labels"].get("zero-door.io/run") == self.owner]
            if not ids:
                args = ["kubectl", "--context", "k3d-zero-door", "--request-timeout=2s", "-n", "zd-sqli-lab",
                        "get", "pods", "-l", "zero-door.io/run=" + self.owner, "-o", "json"]
                query = subprocess.run(args, capture_output=True, timeout=3, env=self.env,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                if query.returncode == 0:
                    ids = [p["metadata"]["uid"] for p in json.loads(query.stdout)["items"] if
                           p["metadata"]["labels"].get("zero-door.io/run") == self.owner]
            if not ids:
                self.save("guard-owned-cgroups.json", {"at": time.time(), "status": "NO_OWNED_POD_UID_AVAILABLE"})
                return
            if len(ids) > 4 or any(not re.fullmatch(r"[a-f0-9-]{36}", x) for x in ids):
                raise ValueError("DIAGNOSTIC_OWNER_PIN")
            script = 'set -u\nfor u in ' + ' '.join(ids) + '; do\n'
            script += ' v=$(echo "$u" | tr - _)\nfor p in $(find /sys/fs/cgroup/kubepods -name memory.events 2>/dev/null); do\n'
            script += ' case "$p" in *"$u"*|*"$v"*) d=${p%/memory.events}; for f in memory.current memory.max memory.high memory.events memory.events.local memory.pressure cpu.stat; do\n'
            script += ' printf "@@ %s/%s\\n" "$d" "$f"; cat "$d/$f" 2>/dev/null || true; done;; esac\ndone\ndone\n'
            args = ["docker", "--context", "desktop-linux", "exec", "-i", "k3d-zero-door-server-0", "sh", "-s"]
            result = subprocess.run(args, input=script.encode(), capture_output=True, timeout=4, env=self.env,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            self.save("guard-owned-cgroups.json", {"at": time.time(), "pod_uids": ids, "args": args,
                "returncode": result.returncode, "stdout": result.stdout.decode(errors="replace"), "stderr": result.stderr.decode(errors="replace")})
        except Exception as error:
            self.save("guard-diagnostic-error.json", {"at": time.time(), "error_type": type(error).__name__})


parent.Lab = Lab

if __name__ == "__main__":
    sys.exit(parent.main())
