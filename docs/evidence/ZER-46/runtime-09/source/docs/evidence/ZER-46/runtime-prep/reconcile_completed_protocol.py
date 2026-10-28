"""Separate offline reconciliation of a completed candidate run, not independent human review.
No Docker/Kubernetes/HTTP calls. A missing or contradictory required artifact fails this verifier.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs/evidence/ZER-46/runtime-08"
spec = importlib.util.spec_from_file_location("zer46_r07_identity", Path(__file__).with_name("reconcile_runtime03.py"))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)


def read(name): return json.loads((OUT / name).read_text(encoding="utf8"))


def log_contains(raw, pod_name, record):
    for receipt in raw:
        args = receipt['args']
        if 'logs' not in args or 'pod/' + pod_name not in args or receipt.get('returncode') != 0:
            continue
        for line in receipt.get('stdout', '').splitlines():
            try: observed = json.loads(line)
            except ValueError: continue
            if observed == record: return True
    return False


def terminal_checks(path, raw):
    """Veto failure history and missing actual RPC-process exit, regardless of happy-path evidence."""
    def get(name): return json.loads((path / name).read_text(encoding="utf8"))
    assert not (path / "failure.json").exists(), "FAILURE_HISTORY"
    acceptance, cleanup = get("acceptance.json"), get("cleanup.json")
    assert acceptance["component_observed"] is True and acceptance.get("error") is None, "ACCEPTANCE_ERROR"
    assert acceptance["status"] == "COMPONENT_RECONCILE_REQUIRED", "ACCEPTANCE_STATUS"
    assert not cleanup["errors"] and not cleanup["guard_failures"], "CLEANUP_OR_GUARD_HISTORY"
    assert all(not row.get("error") and not row.get("cancelled") and row.get("returncode") == 0 for row in raw), "COMMAND_FAILURE_OR_UNKNOWN"
    dispatches = [row for row in raw if "exec" in row["args"] and any("X-Correlation-Id" in arg and "sys.argv[1]" in arg for arg in row["args"])]
    assert len(dispatches) == 29, "DISPATCH_COUNT"
    for n, dispatch in enumerate(dispatches, 1):
        sent = json.loads(dispatch["args"][-1])
        observed = get("http-%03d.json" % n)
        assert sent == observed["request"], "DISPATCH_ASSOCIATION"
        assert json.loads(dispatch["stdout"]) == observed["response"], "DISPATCH_RESPONSE"
    exits = []
    for no in (1, 2):
        identity, hello, exit_row = get("writer-%d-identity.json" % no), get("writer-%d-hello.json" % no), get("writer-%d-exit.json" % no)
        assert type(identity["pid"]) is int and identity["pid"] > 0
        assert type(identity["creation_ticks"]) is int and identity["creation_ticks"] > 0
        assert identity["method"] == "WINDOWS_RETAINED_PROCESS_HANDLE"
        assert identity["instance"] and identity["executable"]
        assert identity['rpc_executable'] == hello['executable']
        assert identity['executable'] == hello['kernel_executable']
        for op in (["hello", "block"] if no == 1 else ["hello", "block", "cleanup"]):
            reply = get("writer-%d-%s.json" % (no, op))
            assert reply["ok"] is True and reply["pid"] == identity["pid"] and reply["instance"] == identity["instance"]
            assert reply["executable"] == hello["executable"] and reply["op"] == op, "RPC_IDENTITY"
            assert reply['kernel_executable'] == identity['executable'], 'RPC_NATIVE_IMAGE'
        assert exit_row["writer"] == identity and exit_row["launcher_pid"] == get("writer-%d.json" % no)["pid"]
        assert exit_row["rpc_exit"] == "EXITED" and type(exit_row["launcher_exit"]) is int and not exit_row.get("error"), "WRITER_EXIT_UNKNOWN"
        assert exit_row["ended_at"] >= exit_row["at"] >= get("writer-%d.json" % no)["at"]
        exits.append(exit_row)
    assert exits[0]["writer"]["instance"] != exits[1]["writer"]["instance"]
    assert (exits[0]['writer']['pid'], exits[0]['writer']['creation_ticks']) != (exits[1]['writer']['pid'], exits[1]['writer']['creation_ticks'])
    assert cleanup["writer_exit_proofs"] == exits, "WRITER_CLEANUP_PROOF"
    phases, completed, rule = get("ttl-phases.json"), get("ttl-phases-completed.json"), get("original-rule.json")
    schedule = (("projection",40),("blocked_before",35),("writer_stop",10),("replacement",30),("blocked_after",35),("writer_replay",10))
    assert [r["phase"] for r in phases] == [name for name, _ in schedule], "TTL_PHASES"
    for i, row in enumerate(phases):
        assert row["expiry"] == rule["expires_at"]
        assert 0 < row["deadline_monotonic"] - row["monotonic"] <= schedule[i][1] + .001
        assert row["future_reserved_seconds"] == sum(seconds for _, seconds in schedule[i + 1:])
        assert row["at"] + row["deadline_monotonic"] - row["monotonic"] + row["future_reserved_seconds"] <= rule["expires_at"] - 15 + .1
        if i: assert row["monotonic"] <= phases[i-1]["deadline_monotonic"], "TTL_PHASE_OVERRUN"
    assert completed["expires_at"] == rule["expires_at"] and completed["remaining_seconds"] >= 15
    assert completed["monotonic"] <= phases[-1]["deadline_monotonic"] and completed["at"] < rule["expires_at"]
    return exits


def main():
    raw = [json.loads(p.read_text(encoding="utf8")) for p in sorted((OUT / "raw").glob("*.json"))]
    exits = terminal_checks(OUT, raw)
    assert not any(r["args"][:4] in (["docker", "--context", "desktop-linux", op] for op in ("build", "pull")) or
                   r["args"][:3] == ["k3d", "image", "import"] for r in raw)
    for path, expected in read("source-manifest.json")["scripts"].items():
        assert hashlib.sha256((OUT / "scripts" / Path(path).name).read_bytes()).hexdigest() == expected
    auth = read("authorization.json")
    assert auth["status"] == "APPROVED"
    assert hashlib.sha256((ROOT / auth["proposal"]).read_bytes()).hexdigest() == auth["proposalSha256"]
    assert hashlib.sha256((OUT / "prepared-source-manifest.json").read_bytes()).hexdigest() == auth["sourceManifestSha256"]
    address = read("source-addresses.json")
    assert len(set(address.values())) == 3
    fixture, replacement = read("fixture-initial.json"), read("fixture-after-replacement.json")
    assert fixture["metadata"]["uid"] != replacement["metadata"]["uid"]
    assert read("pod-delete-options.json")["preconditions"]["uid"] == fixture["metadata"]["uid"]
    old_absent = read('old-pod-absent.json')
    assert old_absent['name'] == fixture['metadata']['name'] and old_absent['uid'] == fixture['metadata']['uid'] and old_absent['absent'] is True
    assert any('get' in r['args'] and 'pod' in r['args'] and old_absent['name'] in r['args'] and
               '--ignore-not-found' in r['args'] and r.get('returncode') == 0 and not r['stdout'].strip() for r in raw), 'OLD_POD_ABSENCE_NOT_OBSERVED'
    for pod in (fixture, replacement):
        assert pod["spec"]["nodeName"] == "k3d-zero-door-agent-0"
        assert any(c["type"] == "Ready" and c["status"] == "True" for c in pod["status"]["conditions"])
        assert all(c.get("restartCount", 0) == 0 for c in pod["status"]["containerStatuses"])
    profile_spec = importlib.util.spec_from_file_location("zer46_r07_hook", Path(__file__).with_name("run_agent_fixture.py"))
    profile = importlib.util.module_from_spec(profile_spec); profile_spec.loader.exec_module(profile)
    tables = [r for r in raw if "iptables-save" in r["args"] and r["returncode"] == 0]
    assert all(any(profile.hooked_policy(row["stdout"], pod) for row in tables) for pod in (fixture, replacement))
    rules = read("original-rule.json")
    assert rules["client_ip"] == address["a"] and rules["expires_at"] - rules["created_at"] == 180
    applied = read("policy-applied.json")
    assert json.loads(applied["data"]["policy.json"])["rules"] == [rules]
    replay = read("replay-readback.json")
    assert replay["before"] == replay["after"] and json.loads(replay["after"]["data"]["policy.json"])["rules"] == [rules]
    writer1, writer2 = read("writer-1.json"), read("writer-2.json")
    for no, writer in ((1, writer1), (2, writer2)):
        reply = read("writer-%d-block.json" % no)
        assert reply["ok"] and type(reply["pid"]) is int and reply["pid"] > 0 and reply["result"]["rule"] == rules
        assert reply["result"]["containment_verified"] is False and reply["result"]["replay"] == (no == 2)
    rpc_pids = [read("writer-%d-block.json" % n)["pid"] for n in (1, 2)]
    assert read("writer-2-cleanup.json")["pid"] == rpc_pids[1]
    responses = [read("http-%03d.json" % n) for n in range(1, 30)]
    joins = [read("join-%03d.json" % n) for n in range(1, 30)]
    statuses = [200,200,201,200,200,404,200,200,403,200,201,200,200,404,403,
                403,200,201,200,200,404,200,200,201,200,200,404,200,200]
    assert len(list(OUT.glob("http-*.json"))) == len(responses) == 29
    for i, (row, joined, expected) in enumerate(zip(responses, joins, statuses), 1):
        result = row["response"]
        assert result["status"] == joined["status"] == expected
        assert result["request_id"] == joined["request_id"] and row["request"]["correlation"] == joined["correlation_id"]
        assert joined["client_ip"] == address[row["who"]] and joined["tcp_peer"] == address["proxy"]
        assert joined["source_method"] == "XFF_AFTER_TRUSTED" and joined["source_confidence"] == "PROXY_CHAIN"
        if expected == 403:
            assert row["who"] == "a" and result["body"]["error"] == "SOURCE_BLOCKED"
            assert joined["blocked"] is True and joined["action_ids"] == [rules["action_id"]]
            assert rules["created_at"] <= result["begin"] <= result["end"] < rules["expires_at"]
        if i >= 22:
            assert result["begin"] >= rules["expires_at"]
    for i in range(1, 30):
        target = read("log-pod-target-%03d.json" % i)
        expected = fixture if i <= 15 else replacement
        assert target["uid"] == expected["metadata"]["uid"] and target["name"] == expected["metadata"]["name"]
        assert log_contains(raw, target['name'], joins[i - 1]), 'JOIN_NOT_IN_PINNED_POD_RAW_LOG'
    assert responses[6]["request"]["headers"]["X-Forwarded-For"] == "203.0.113.77"
    assert joins[6]["client_ip"] == address["a"]
    for start in (2, 10, 17, 23):
        made, got, deleted, missing = responses[start:start + 4]
        ref = made["response"]["body"]["order_ref"]
        assert got["request"]["path"] == deleted["request"]["path"] == missing["request"]["path"] == "/fixture/orders/" + ref
        assert got["response"]["body"]["note"] == made["request"]["body"]["note"]
    tcp = [r for r in raw if "socket.socket()" in " ".join(r["args"])]
    assert len(tcp) == 4 and all(r["returncode"] == 0 and json.loads(r["stdout"]) == {"denied": True} for r in tcp)
    clean_api = read("policy-cleanup-api.json")
    assert clean_api["metadata"]["uid"] == applied["metadata"]["uid"]
    assert json.loads(clean_api["data"]["policy.json"])["rules"] == []
    digest = hashlib.sha256(clean_api["data"]["policy.json"].encode()).hexdigest()
    mounted = []
    for r in raw:
        if "open('/containment/policy.json'" in " ".join(r["args"]) and r.get("returncode") == 0:
            mounted.append(json.loads(r["stdout"]))
    assert any(x["sha256"] == digest and x["policy"]["rules"] == [] for x in mounted)
    created, deleted = read("namespace-created.json"), read("namespace-delete-options.json")
    assert deleted["preconditions"]["uid"] == created["metadata"]["uid"]
    absent = [r for r in raw if r["args"][0] == "kubectl" and "namespace" in r["args"] and "--ignore-not-found" in r["args"]]
    assert absent and all(r["returncode"] == 0 and not r["stdout"].strip() for r in absent)
    assert h.identity(read("before.json")) == h.identity(read("after.json"))
    assert h.restarts(read("before.json")) == h.restarts(read("after.json"))
    samples = read("resource-samples.json")
    assert len(samples) >= 25 and samples[24]["at"] - samples[0]["at"] >= 119
    assert all(x["hostAvailable"] >= 1073741824 and x["wslAvailableKiB"] >= 1048576 and x["memoryPsiAvg10"] <= 5 for x in samples)
    cleanup = read("cleanup.json")
    assert cleanup["component_resource_verdict"] == "CLEAN" and cleanup["policy_cleanup_observed"]
    assert cleanup["writer_processes"] == 2 and cleanup["fixture_http"] == 29 and cleanup["tcp_checks"] == 4
    result = {"status": "COMPONENT_AC_OBSERVED_RAW_RECONCILED", "fixture_http": 29, "joined": 29,
        "tcp_denied_controls": 4, "builds": 0, "imports": 0, "pulls": 0, "writer_processes": 2,
        "actual_rpc_exit_proofs": exits, "failure_history_veto_checked": True,
        "launcher_pids": [writer1["pid"], writer2["pid"]], "writer_rpc_pids": rpc_pids,
        "fixture_uid_before": fixture["metadata"]["uid"], "fixture_uid_after": replacement["metadata"]["uid"],
        "ttl_seconds": 180, "replay_changed_state": False, "original_expiry": rules["expires_at"],
        "owned_policy_api_and_mount_empty": True, "namespace_uid_delete_verified_absent": True,
        "shared_spec_uid_restart_preserved": True, "guard_samples": len(samples),
        "max_memory_psi_avg10": max(x["memoryPsiAvg10"] for x in samples),
        "boutique_healthy": cleanup["business_2_of_2"], "formal_kpi_pass": False, "end_to_end_pass": False,
        "independent_human_or_agent_review": "PENDING", "merge": "NOT_DONE", "issue_done": False}
    (OUT / "independent-verification.json").write_text(json.dumps(result, indent=2), encoding="utf8")
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    args = parser.parse_args()
    candidate = args.runtime.resolve()
    if candidate.parent != (ROOT / "docs/evidence/ZER-46").resolve() or not candidate.name.startswith("runtime-"):
        parser.error("explicit ZER-46 runtime evidence directory required")
    OUT = candidate
    main()
