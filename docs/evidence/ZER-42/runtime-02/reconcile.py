"""Reconcile the retained four-case attempt offline, preserving all original bytes.
Creates explicit H-only ID mapping and new write-once bundles/exports. No network I/O.
"""
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import uuid
import yaml

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "chaos-worker/go.mod").is_file())
HERE = Path(__file__).resolve().parent
ATTEMPT = HERE / "zer42-74545a02be28"
OUT = HERE / "acceptance-final"
sys.path.insert(0, str(ROOT / "infrastructure/scripts"))
import sqli_executor_runtime as runtime


def load(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    with (OUT / name).open("x", encoding="utf8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def raw(name):
    p = next((ATTEMPT / "raw").glob(name + ".json"))
    document = load(p)
    assert document["returncode"] == 0, name
    return document


def records(name):
    return [json.loads(line) for line in raw(name)["stdout"].splitlines() if line.startswith("{")]


def main():
    assert OUT.is_dir() and load(OUT / "cleanup-receipt.json")["status"] == "CLEAN"
    original_hashes = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(ATTEMPT.rglob("*")) if p.is_file()}
    write("original-artifact-sha256.json", original_hashes)
    source_hashes = load(ATTEMPT / "source-manifest.json")
    assert all(sha(ROOT / p) == digest for p, digest in source_hashes.items()), "SOURCE_DRIFT"
    assert load(ATTEMPT / "baseline.json") == load(ATTEMPT / "after.json"), "HISTORICAL_RESTORE_MISMATCH"
    assert raw("143-verify-absent")["stdout"].strip() == ""
    owner = load(ATTEMPT / "namespace-owner.json")
    before_delete = json.loads(raw("140-namespace-before-cleanup")["stdout"])
    assert owner["uid"] == before_delete["metadata"]["uid"]
    assert before_delete["metadata"]["labels"]["zero-door.io/run"] == ATTEMPT.name

    envelopes = load(ATTEMPT / "commands.json")
    assert envelopes == json.loads(raw("103-remote-read")["stdout"])
    assert len(envelopes) == 4 and [r["offset"] for r in envelopes] == list(range(4))
    commands = [json.loads(base64.b64decode(r["value"]["payload"])) for r in envelopes]
    command_map = {c["commandId"]: c for c in commands}
    assert len(command_map) == 4
    safe = load(ATTEMPT / "results-safe.json")
    results = load(ATTEMPT / "results-vulnerable.json")
    assert results[:2] == safe and len(safe) == 2 and len(results) == 4
    assert [r["offset"] for r in results] == list(range(4))
    safe_ids = {r["value"]["commandId"] for r in safe}
    assert {r["value"]["commandId"] for r in results} == set(command_map)
    invalid = json.loads(raw("043-remote-trigger")["stdout"])
    assert invalid["status"] == 400 and invalid["body"]["detail"] == "SQLI_TEMPLATE"
    assert json.loads(raw("102-remote-trigger")["stdout"])["body"]["commandId"] == commands[0]["commandId"]

    fixture = {"safe": records("051-logs-safe-sqli-fixture"),
               "vulnerable": records("104-logs-failure-sqli-fixture")}
    proxy = records("105-logs-failure-zer41-private-ingress")
    assert len(proxy) == 16 and sum(len(v) for v in fixture.values()) == 16, "TRAFFIC_OR_REPLAY_MISMATCH"
    proxy_ids = {p["request_X-Correlation-Id"]: p for p in proxy}
    assert len(proxy_ids) == 16
    # Resolve identities only from captured Pod status, never from source-provided XFF.
    ips, image_ids = {}, {}
    for p in sorted((ATTEMPT / "raw").glob("*-*pods.json")):
        j = load(p)
        if j["returncode"]:
            continue
        for pod in json.loads(j["stdout"])["items"]:
            if pod["status"].get("podIP"):
                ips[pod["metadata"].get("labels", {}).get("app", pod["metadata"]["name"])] = pod["status"]["podIP"]
            for status in pod["status"].get("containerStatuses", []):
                image_ids.setdefault(pod["metadata"].get("labels", {}).get("app"), set()).add(status["imageID"])
    assert ips["zer42-source-a"] != ips["zer42-source-b"]
    rendered = list(yaml.safe_load_all((ATTEMPT / "rendered-disabled.yaml").read_text(encoding="utf8")))
    actor_images = {}
    for actor in ("worker", "nemesis"):
        expected_tag = "zer42-" + actor + ":" + hashlib.sha256(json.dumps(source_hashes, sort_keys=True).encode()).hexdigest()[:12]
        pod = next(d for d in rendered if d and d["kind"] == "Pod" and d["metadata"]["name"] == "zer42-" + actor)
        container = pod["spec"]["containers"][0]
        assert container["image"] == expected_tag and container["imagePullPolicy"] == "Never"
        assert raw("039-wait-zer42-worker" if actor == "worker" else "040-wait-zer42-nemesis")["returncode"] == 0
        inspected = raw("007-image-worker" if actor == "worker" else "009-image-nemesis")["stdout"].strip()
        actor_images[actor] = {"rendered_tag": expected_tag, "host_image_id": inspected,
            "ready_wait_passed": True, "runtime_container_image_id": "NOT_RETAINED"}
    command_ips = {e["client_ip"] for phase in fixture.values() for e in phase
                   if e["correlation_id"].split("/")[0] in command_map}
    assert len(command_ips) == 1 and not command_ips & {ips["zer42-source-a"], ips["zer42-source-b"]}
    ips["executor_observed_from_correlated_requests"] = next(iter(command_ips))
    joins, controls = [], []
    for phase in fixture:
        assert len(fixture[phase]) == 8
        for entry in fixture[phase]:
            corr = entry["correlation_id"]
            p = proxy_ids[corr]
            assert entry["request_id"] == p["origin_X-Request-Id"] == p["downstream_X-Request-Id"]
            assert entry["status"] == p["OriginStatus"] == p["DownstreamStatus"] == 200
            assert entry["tcp_peer"] == ips["zer41-private-ingress"]
            assert entry["client_ip"] == p["ClientHost"] != "203.0.113.77"
            assert entry["source_method"] == "XFF_AFTER_TRUSTED" and entry["source_confidence"] == "PROXY_CHAIN"
            assert p["RetryAttempts"] == 0
    for marker, phase, source in (("029", "safe", "a"), ("031", "safe", "b"),
                                  ("092", "vulnerable", "a"), ("094", "vulnerable", "b")):
        control = json.loads(raw(marker + "-remote-control")["stdout"])
        entry = next(e for e in fixture[phase] if e["correlation_id"] == control["correlation_id"])
        assert control["request_id"] == entry["request_id"]
        assert control["status"] == 200 and control["body"]["count"] == entry["rows"] == 2
        assert sorted(r["sku"] for r in control["body"]["results"]) == ["PUB-APP-001", "PUB-APP-002"]
        assert entry["restricted_rows"] == 0 and entry["client_ip"] == ips["zer42-source-" + source]
        controls.append({"profile": phase, "source": source, "client_ip": entry["client_ip"],
                         "request_id": entry["request_id"], "forged_xff_rejected": True})
    for marker in ("028", "030", "091", "093"):
        assert json.loads(raw(marker + "-remote-direct")["stdout"])["direct_fixture"] == "DENIED"
    # Each profile was released only after a successful iptables snapshot for that exact Pod.
    gates = []
    for marker, profile in (("026", "safe"), ("089", "vulnerable")):
        release = raw(marker + "-release-gate")
        name = release["args"][release["args"].index("exec") + 3]
        policy_files = sorted(p for p in (ATTEMPT / "raw").glob("*-policy.json") if int(p.name[:3]) < int(marker))
        assert any("POD name:" + name + " namespace: zd-sqli-lab" in load(p)["stdout"]
                   and load(p)["returncode"] == 0 for p in policy_files)
        gates.append({"profile": profile, "pod": name, "policy_observed": True})

    old_context = commands[0]["context"]
    assert all(c["context"] == old_context for c in commands)
    assert not runtime.contract.valid_id(old_context["run_id"], "run")
    # New IDs identify a post-collection H packaging operation; historical signed commands stay untouched.
    mapped = {kind + "_id": kind + "_" + uuid.UUID(bytes=hashlib.sha256(
        ("zer42-h-repack/1:" + old_context[kind + "_id"]).encode()).digest()[:16], version=4).hex
        for kind in ("run", "trial")}
    # Contract prefix for trial is trl, whereas its context key is trial_id.
    mapped["trial_id"] = "trl_" + mapped["trial_id"].split("_", 1)[1]
    mapping = {"format": "zer42-h-repack/1", "at": datetime.now(timezone.utc).isoformat(),
               "original_context": old_context, "mapped_context": mapped,
               "reason": "renderer padded a 12-hex label; zd-event/1 requires UUIDv4 version/variant bits",
               "raw_changed": False, "harness_attempt": ATTEMPT.name,
               "command_envelopes_sha256": sha(ATTEMPT / "commands.json"), "incidents": {}}
    summary = []
    for record in results:
        result = record["value"]
        cid = result["commandId"]
        command = command_map[cid]
        profile = "safe" if cid in safe_ids else "vulnerable"
        template = command["parameters"]["customParams"]["template"]
        disclosed = profile == "vulnerable" and template == "disclose-restricted"
        expected_skus = sorted(runtime.oracle_restricted()) if disclosed else []
        expected_rows = 2 if template == "benign-apparel" else len(expected_skus)
        assert result["status"] == "SUCCESS" and result["attackType"] == "SQLI"
        assert command["target"] == {"namespace": "zd-sqli-lab", "service": "sqli-fixture",
            "url": "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search"}
        assert command["parameters"]["duration"] == 5 and command["parameters"]["concurrency"] == 1
        sends = result["details"]["sqli"]["sends"]
        assert len(sends) == result["details"]["requestsSent"] == 3
        assert [s["seq"] for s in sends] == [1, 2, 3]
        assert result["duration"] <= 5000
        for send in sends:
            assert not send.get("error") and send["status"] == 200
            assert send["rows"] == expected_rows and send["restrictedRows"] == len(expected_skus)
            assert sorted(send.get("restrictedSkus", [])) == expected_skus
            corr = cid + "/" + str(send["seq"])
            assert send["requestId"] == corr
            matches = [e for e in fixture[profile] if e["correlation_id"] == corr]
            assert len(matches) == 1
            entry = matches[0]
            assert send["responseId"] == entry["request_id"]
            assert entry["rows"] == expected_rows and entry["restricted_rows"] == len(expected_skus)
            assert entry["client_ip"] == ips["executor_observed_from_correlated_requests"]
            joins.append({"command_id": cid, "profile": profile, "sequence": send["seq"],
                          "correlation_id": corr, "response_id": send["responseId"],
                          "fixture_client_ip": entry["client_ip"], "proxy_client_ip": proxy_ids[corr]["ClientHost"],
                          "rows": entry["rows"], "restricted_rows": entry["restricted_rows"]})
        incident = runtime.contract.new_id("inc")
        mapping["incidents"][cid] = incident
        context = {**mapped, "group": old_context["group"], "incident_id": incident,
                   "method_version": "zer42-h-repack/1", "config_ref": "sha256:" + runtime.digest(source_hashes)}
        bundle = runtime.prepare_bundle(result, context, OUT / (cid + "-bundle.json"))
        receipt = runtime.archive_bundle(bundle, OUT / (cid + "-archive"), OUT / (cid + "-export"))
        assert receipt == runtime.recheck_export(OUT / (cid + "-export"))
        assert receipt["checked"][0]["status"] == ("CONFIRMED" if disclosed else "UNKNOWN_EFFECT")
        assert bundle["events"][0]["payload"]["raw_result"] == result
        write(cid + "-receipt.json", receipt)
        summary.append({"command_id": cid, "profile": profile, "template": template,
            "sends": 3, "expected_rows_per_send": expected_rows, "expected_restricted_skus": expected_skus,
            "independent_joins": 3, "technical_case": "PASS", "formal_effect": receipt["checked"][0]["status"]})
    assert len(joins) == 12
    assert {(s["profile"], s["template"]) for s in summary} == {
        (p, t) for p in ("safe", "vulnerable") for t in ("disclose-restricted", "benign-apparel")}
    assert original_hashes == {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(ATTEMPT.rglob("*")) if p.is_file()}
    write("id-mapping.json", mapping)
    write("request-joins.json", {"joins": joins, "controls": controls, "policy_gates": gates,
          "observed_ips": ips, "actor_image_provenance": actor_images, "observed_image_ids": {k: sorted(v) for k, v in image_ids.items()},
          "replay_extra_commands": 0, "replay_extra_http_requests_in_retained_logs": 0})
    write("acceptance.json", {"verdict": "TECHNICAL_PASS_READY_FOR_PUBLICATION", "at": datetime.now(timezone.utc).isoformat(),
          "attempt": ATTEMPT.name, "head": "7db9d9f9bc265b07a4cb361923ee535f707adeda", "source_hashes_match": source_hashes,
          "original_artifact_count": len(original_hashes), "original_bytes_unchanged": True,
          "cases": summary, "guard_invalid_template_rejected": True, "requests": {"executor": 12, "benign_controls": 4},
          "cleanup": "CLEAN", "new_lab_test_requests": 0,
          "limitations": ["Post-collection H repack with explicit old-to-new ID mapping; original FAILED receipt preserved",
              "Safe/benign formal H statuses remain UNKNOWN_EFFECT as required; technical contrast uses independent logs",
              "Clock source remains UNKNOWN; no cross-host timing/KPI, containment, R3 or Boutique vulnerability claim",
              "Historical ephemeral signing keys are absent; signatures retained, no independent cryptographic revalidation",
              "Actor image tags/host digests/Ready waits retained; actor container imageID and PodIP snapshot not retained",
              "No Git publication, remote CI, merge, Linear change or owner Done acceptance performed"]})
    print("TECHNICAL_PASS_READY_FOR_PUBLICATION: 4 cases, 12 independent joins, 4 controls, 4 H exports, CLEAN")


if __name__ == "__main__":
    main()
