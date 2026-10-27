"""Independent read-only comparison of saved ZER-42 broker, fixture, proxy and export evidence.

Does not trust the runner's case PASS assertions and does not issue requests.
"""
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "chaos-worker/go.mod").is_file())


def load(path):
    return json.loads(path.read_bytes())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def main(out):
    expected = load(ROOT / "tests/fixtures/zer41/expected.json")
    raw_results = load(out / "results-vulnerable.json")
    raw_commands = load(out / "commands.json")
    assert len(raw_commands) == 4 and len(raw_results) == 4
    commands = {}
    for record in raw_commands:
        envelope = record["value"]
        assert envelope["purpose"] == "fault" and envelope["version"] == "zd-command/1"
        command = json.loads(base64.b64decode(envelope["payload"]))
        assert command["attackType"] == "SQLI"
        assert command["target"] == {"namespace": "zd-sqli-lab", "service": "sqli-fixture",
            "url": "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search"}
        assert command["parameters"]["concurrency"] == 1 and command["parameters"]["duration"] <= 5
        assert command["commandId"] not in commands
        commands[command["commandId"]] = command
    observations = []
    proxy_records = {}
    fixture_records = {}
    for path in sorted((out / "raw").glob("*.json")):
        record = load(path)
        args = record.get("args", [])
        stdout = record.get("stdout", "")
        if "logs" in args:
            for line in stdout.splitlines():
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("request_id"):
                    previous = fixture_records.setdefault(row["request_id"], row)
                    assert previous == row, "conflicting repeated log row"
                elif "ClientHost" in row:
                    proxy_records[(row.get("StartUTC"), row.get("RequestCount"))] = row
        if "control" in args and record["returncode"] == 0:
            value = json.loads(stdout)
            pod = args[args.index("-i") + 1]
            observations.append((pod, value))
    pods = load(out / "pods-final.json")["items"]
    ips = {p["metadata"]["labels"].get("app"): p["status"].get("podIP") for p in pods}
    assert len({ips[name] for name in ("zer42-source-a", "zer42-source-b", "zer42-worker")}) == 3
    matches = []
    for pod, observation in observations:
        log = fixture_records[observation["request_id"]]
        assert log["correlation_id"] == observation["correlation_id"]
        assert log["client_ip"] == ips[pod] and log["client_ip"] != "203.0.113.77"
        assert log["source_confidence"] != "UNKNOWN" and log["status"] == 200
        assert sorted(row["sku"] for row in observation["body"]["results"]) == expected["benign"]["apparel"]
        matches.append({"source": pod, "request_id": log["request_id"], "client_ip": log["client_ip"]})
    assert len(observations) == 4
    classifications = Counter()
    send_ids = set()
    for record in raw_results:
        result = record["value"]
        command = commands[result["commandId"]]
        template = command["parameters"]["customParams"]["template"]
        sends = result["details"]["sqli"]["sends"]
        assert result["status"] == "SUCCESS" and len(sends) == 3
        assert result["details"]["requestsSent"] == 3
        returned = []
        for send in sends:
            assert send["status"] == 200 and not send.get("error")
            assert send["requestId"] == result["commandId"] + "/" + str(send["seq"])
            log = fixture_records[send["responseId"]]
            assert log["correlation_id"] == send["requestId"] and log["status"] == send["status"]
            assert log["client_ip"] == ips["zer42-worker"] and log["source_confidence"] != "UNKNOWN"
            assert log["restricted_rows"] == send["restrictedRows"]
            assert send["responseId"] not in send_ids
            send_ids.add(send["responseId"])
            returned.append(set(send.get("restrictedSkus", [])))
        if template == "benign-apparel":
            assert all(s["rows"] == 2 and s["restrictedRows"] == 0 for s in sends)
            classifications["benign"] += 1
        elif any(returned):
            assert all(s == set(expected["injection"]["vulnerable_returns_restricted"]) for s in returned)
            classifications["vulnerable_disclosure"] += 1
        else:
            assert all(s["rows"] == 0 for s in sends)
            classifications["safe_disclosure"] += 1
        bundle = load(out / (result["commandId"] + "-bundle.json"))
        fault, effect = bundle["events"]
        assert fault["payload"]["raw_result"] == result
        assert fault["payload"]["raw_result_sha256"] == hashlib.sha256(canonical(result)).hexdigest()
        assert effect["causation_id"] == fault["event_id"]
        want = "CONFIRMED" if any(returned) else "UNKNOWN_EFFECT"
        assert effect["payload"]["status"] == want
        sys.path.insert(0, str(ROOT / "agent-orchestrator"))
        from measurement.raw import Export
        exported = Export(out / (result["commandId"] + "-export"), "H")
        envelopes = {r["envelope"]["event_id"]: r["envelope"] for r in exported.records}
        assert envelopes[fault["event_id"]] == fault and envelopes[effect["event_id"]] == effect
    assert classifications == {"benign": 2, "vulnerable_disclosure": 1, "safe_disclosure": 1}
    assert len(send_ids) == 12
    # Proxy records independently confirm the same three source identities and total requests.
    proxy_counts = Counter(row["ClientHost"] for row in proxy_records.values() if row.get("RequestPath", "").startswith("/fixture/"))
    assert proxy_counts[ips["zer42-worker"]] == 12, proxy_counts
    assert proxy_counts[ips["zer42-source-a"]] == 2 and proxy_counts[ips["zer42-source-b"]] == 2
    process = load(out / "process-receipt.json")
    assert process["status"] == "COLLECTED_PENDING_RECONCILIATION" and not process["cleanup_problems"]
    assert process["elapsed_seconds"] <= 2700
    assert process.get("authorization_elapsed_seconds", process["elapsed_seconds"]) <= 2700
    assert load(out / "baseline.json") == load(out / "after.json")
    receipt = {"verdict": "PASS_PRIVATE_RUNTIME", "broker_commands": 4, "broker_results": 4,
        "executor_sends": len(send_ids), "source_controls": len(observations), "cases": dict(classifications),
        "proxy_source_counts": dict(proxy_counts), "source_ip_joins": matches,
        "checked_exports": 4, "cleanup": "VERIFIED", "elapsed_seconds": process["elapsed_seconds"],
        "limitations": ["proxy source/count corroboration; proxy does not retain per-request IDs",
                        "executor-only no-effect events stay UNKNOWN; not a research KPI result"]}
    target = out / "independent-verification.json"
    with target.open("x", encoding="utf8", newline="\n") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
