"""Offline validation against the pinned Kubernetes client's OpenAPI models.

Reject unknown fields/type mismatches recursively without constructing a client
or contacting a cluster. Admission policies, rollout and storage are not tested.
"""
from pathlib import Path
import re
import yaml
from kubernetes.client import models

ROOT = Path(__file__).resolve().parents[1]


def validate(value, schema, location="$"):
    if value is None:
        return  # OpenAPI model fields may be optional/nullable.
    if schema.startswith("list["):
        if type(value) is not list:
            raise ValueError((location, "expected list"))
        for i, item in enumerate(value):
            validate(item, schema[5:-1], location + f"[{i}]")
    elif schema.startswith("dict("):
        if type(value) is not dict:
            raise ValueError((location, "expected object"))
        child = schema.split(", ", 1)[1][:-1]
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError((location, "expected string key"))
            validate(item, child, location + "." + key)
    elif schema in {"str", "int", "bool", "float"}:
        expected = {"str": str, "int": int, "bool": bool, "float": float}[schema]
        if type(value) is not expected:
            raise ValueError((location, "expected " + schema))
    elif schema in {"object", "datetime", "date"}:
        return
    else:
        model = getattr(models, schema)
        if type(value) is not dict:
            raise ValueError((location, "expected " + schema))
        fields = {wire: model.openapi_types[attr] for attr, wire in model.attribute_map.items()}
        for key, item in value.items():
            if key not in fields:
                raise ValueError((location + "." + key, "unknown field in " + schema))
            validate(item, fields[key], location + "." + key)


def check(documents):
    for document in documents:
        version = document["apiVersion"].rsplit("/", 1)[-1]
        if not re.fullmatch(r"v[0-9]+(?:alpha[0-9]+|beta[0-9]+)?", version):
            raise ValueError("unsupported apiVersion")
        validate(document, version[0].upper() + version[1:] + document["kind"])


if __name__ == "__main__":
    for name in ("chaos-worker.yaml", "nemesis-deployment.yaml", "hephaestus-deployment.yaml", "command-guard-config.yaml"):
        documents = list(yaml.safe_load_all((ROOT / "infrastructure/manifests" / name).read_text()))
        check(documents)
        print(name, "OpenAPI field/type PASS", len(documents), "resources")
