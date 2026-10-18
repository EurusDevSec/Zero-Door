#!/usr/bin/env python3
"""Bound JMX heap in Kafka 29.3.2; reject an unexpected chart layout."""
import sys
import yaml


def render(documents):
    matches = []
    for doc in documents:
        if not doc or doc.get("kind") != "StatefulSet":
            continue
        if doc.get("metadata", {}).get("name") != "kafka-controller":
            continue
        if doc["metadata"].get("namespace") != "zero-door":
            continue
        for container in doc["spec"]["template"]["spec"]["containers"]:
            if container["name"] == "jmx-exporter":
                matches.append(container)
    if len(matches) != 1:
        raise ValueError("expected exactly one zero-door/kafka-controller jmx-exporter")
    container = matches[0]
    args = container.get("args", [])
    if container.get("command") != ["java"] or args.count("-XX:MaxRAMPercentage=100") != 1:
        raise ValueError("unexpected JMX command/args; re-review the pinned chart")
    if container.get("resources", {}).get("limits", {}).get("memory") != "256Mi":
        raise ValueError("JMX memory limit changed; re-evaluate the 128Mi heap budget")
    if any(a.startswith(("-Xmx", "-Xms")) for a in args):
        raise ValueError("unexpected existing JMX heap options")
    i = args.index("-XX:MaxRAMPercentage=100")
    args[i:i + 1] = ["-Xms32m", "-Xmx128m"]
    return documents


if __name__ == "__main__":
    try:
        documents = list(yaml.safe_load_all(sys.stdin))
        yaml.safe_dump_all(render(documents), sys.stdout, sort_keys=False)
    except (ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        sys.exit(f"Kafka JMX render refused: {exc}")
