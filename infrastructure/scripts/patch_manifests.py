#!/usr/bin/env python3
"""
Zero-Door Manifest Patcher for Cloud Deployment

Chuyển đổi K8s manifests từ local (image: agent:latest)
sang cloud (image: ghcr.io/org/repo/agent:latest) và inject imagePullSecrets.

Bài học từ deploy lần 1:
- gaia dùng "zero-door/gaia:latest" KHÁC với các agent khác ("gaia:latest")
- gaia dùng imagePullPolicy: Never KHÁC với các agent khác (IfNotPresent)
- Dùng Python re.sub để inject imagePullSecrets — tránh bash sed phức tạp

Cách dùng:
  python3 patch_manifests.py \\
    --src /path/to/manifests \\
    --dst /tmp/manifests-cloud \\
    --registry ghcr.io/eurusdevsec/zero-door
"""

import os
import re
import shutil
import argparse


def patch_agent(content: str, local_image: str, agent_name: str, registry: str) -> str:
    """Patch một agent manifest: thay image, pull policy, inject imagePullSecrets."""

    # 1. Thay image local → GHCR image
    content = content.replace(
        f"image: {local_image}",
        f"image: {registry}/{agent_name}:latest"
    )

    # 2. Thay imagePullPolicy (cả Never và IfNotPresent → Always)
    content = content.replace("imagePullPolicy: IfNotPresent", "imagePullPolicy: Always")
    content = content.replace("imagePullPolicy: Never", "imagePullPolicy: Always")
    # Xóa comment sau imagePullPolicy nếu có
    content = re.sub(r"(imagePullPolicy: Always)\s*#.*", r"\1", content)

    # 3. Inject imagePullSecrets vào pod template spec
    # Tìm "    spec:" theo sau bởi "      securityContext:" hoặc "      serviceAccountName:"
    # hoặc "      containers:" — đây là pod template spec (indentation 4 spaces)
    content = re.sub(
        r"(    spec:\n)(      (?:securityContext|serviceAccountName|containers):)",
        r"\1      imagePullSecrets:\n        - name: ghcr-secret\n\2",
        content
    )

    return content


def main():
    parser = argparse.ArgumentParser(description="Patch Zero-Door manifests for cloud deployment")
    parser.add_argument("--src", required=True, help="Source manifests directory")
    parser.add_argument("--dst", required=True, help="Destination directory for patched manifests")
    parser.add_argument("--registry", required=True, help="Container registry base URL (e.g. ghcr.io/org/repo)")
    args = parser.parse_args()

    os.makedirs(args.dst, exist_ok=True)

    # Map: filename → (local_image_name, agent_name)
    # Bài học: gaia dùng "zero-door/gaia:latest" KHÁC với các agent còn lại
    AGENT_MAP = {
        "nemesis-deployment.yaml":    ("nemesis:latest",          "nemesis"),
        "gaia-deployment.yaml":       ("zero-door/gaia:latest",   "gaia"),     # ← đặc biệt!
        "hephaestus-deployment.yaml": ("hephaestus:latest",       "hephaestus"),
        "chaos-worker.yaml":          ("chaos-worker:latest",     "chaos-worker"),
    }

    patched_count = 0
    for fname, (local_image, agent_name) in AGENT_MAP.items():
        src_path = os.path.join(args.src, fname)
        dst_path = os.path.join(args.dst, fname)

        if not os.path.exists(src_path):
            print(f"[WARN] Not found: {src_path} — skipping")
            continue

        with open(src_path, encoding="utf-8") as f:
            content = f.read()

        content = patch_agent(content, local_image, agent_name, args.registry)

        with open(dst_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Verify patch
        if f"{args.registry}/{agent_name}:latest" in content:
            print(f"[OK] {fname} → image: {args.registry}/{agent_name}:latest")
        else:
            print(f"[WARN] {fname} — image patch may have failed, check manually")

        if "imagePullSecrets" in content:
            print(f"     imagePullSecrets: ghcr-secret ✓")
        else:
            print(f"[WARN] {fname} — imagePullSecrets NOT injected!")

        patched_count += 1

    print(f"\nDone: {patched_count}/{len(AGENT_MAP)} manifests patched → {args.dst}")


if __name__ == "__main__":
    main()
