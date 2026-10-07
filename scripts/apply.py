#!/usr/bin/env python3
"""Preflight every repository before applying the locked bring-up patch series."""
import argparse
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
PATHS = {
    "build": "build/make",
    "aidl": "system/tools/aidl",
    "device": "device/glodroid",
    "kernel": "kernel/glodroid-stable",
    "uboot": "external/u-boot",
    "drm_hwcomposer": "external/drm_hwcomposer",
}


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], check=check,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--check", action="store_true", help="preflight only")
    parser.add_argument("--bsp-only", action="store_true", help="skip Android build/make and AIDL host patches")
    args = parser.parse_args()
    root = args.source.resolve()
    lock = json.loads((PROJECT / "sources.lock.json").read_text())
    expected = {x["component"]: x["commit"] for x in lock["sources"]}
    pending = []
    for component, rel in PATHS.items():
        if args.bsp_only and component in ("build", "aidl"):
            continue
        repo = root / rel
        head = git(repo, "rev-parse", "HEAD").stdout.strip()
        if head != expected[component]:
            raise SystemExit(f"{rel}: expected {expected[component]}, got {head}; no patches applied")
        patches = sorted((PROJECT / "patches" / component).glob("*.patch"))
        if not patches:
            raise SystemExit(f"No patches found for {component}")
        for patch in patches:
            if git(repo, "apply", "--reverse", "--check", str(patch), check=False).returncode == 0:
                print(f"Already applied: {rel} ({patch.name})")
            elif git(repo, "apply", "--check", str(patch), check=False).returncode == 0:
                pending.append((repo, patch))
            else:
                detail = git(repo, "apply", "--check", str(patch), check=False).stderr
                raise SystemExit(f"Conflicting edits in {rel} ({patch.name}); no patches applied\n{detail}")
    fw = root / "kernel/firmware"
    if git(fw, "rev-parse", "HEAD").stdout.strip() != expected["firmware"]:
        raise SystemExit("Firmware revision differs from sources.lock.json")
    for name in ("boot_xr819.bin", "fw_xr819.bin", "sdd_xr819.bin"):
        if not (fw / "xr819" / name).is_file():
            raise SystemExit(f"Missing XR819 firmware: {name}")
    if args.check:
        print(f"Preflight passed ({len(pending)} repositories pending)")
        return
    for repo, patch in pending:
        git(repo, "apply", str(patch))
        # Preserve imported driver formatting; check the new integration edits.
        git(repo, "diff", "--check", "--", ".", ":!drivers/net/wireless/xradio")
        print(f"Applied: {repo.relative_to(root)}")


if __name__ == "__main__":
    main()
