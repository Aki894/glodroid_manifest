#!/usr/bin/env python3
"""Preflight every repository before applying the locked bring-up patch series."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
PATHS = {
    "build": "build/make",
    "aidl": "system/tools/aidl",
    "mesa3d": "external/mesa3d",
    "device": "device/glodroid",
    "kernel": "kernel/glodroid-stable",
    "uboot": "external/u-boot",
    "drm_hwcomposer": "external/drm_hwcomposer",
}


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], check=check,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def pending_series(repo, patches):
    """Test every prefix in an isolated index; support overlapping upgrade patches."""
    import os
    import re
    import tempfile
    paths = sorted({m.group(1) for p in patches for m in
                    re.finditer(r'^diff --git a/(\S+) b/\S+$', p.read_text(), re.M)})
    with tempfile.TemporaryDirectory(prefix='wukong-patch-index-') as tmp:
        index = Path(tmp) / 'index'
        env = dict(os.environ, GIT_INDEX_FILE=str(index))
        def command(*args):
            return subprocess.run(['git', '-C', str(repo), *args], env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        detail = ''
        for applied in range(len(patches), -1, -1):
            if index.exists(): index.unlink()
            result = command('read-tree', 'HEAD')
            if result.returncode: raise RuntimeError(result.stderr)
            tracked = set(git(repo, 'ls-files', '-z').stdout.split('\0'))
            present = [p for p in paths if (repo / p).exists() or p in tracked]
            if present:
                result = command('add', '-A', '--', *present)
                if result.returncode: raise RuntimeError(result.stderr)
            valid = True
            for patch in reversed(patches[:applied]):
                result = command('apply', '--cached', '--reverse', str(patch))
                if result.returncode:
                    valid = False
                    break
            if not valid: continue
            # Reconstruct the full desired series from the recovered base.
            for patch in patches:
                result = command('apply', '--cached', str(patch))
                if result.returncode:
                    detail = result.stderr
                    valid = False
                    break
            if valid: return patches[applied:]
        raise RuntimeError(detail or 'Patch series has conflicting local edits')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--check", action="store_true", help="preflight only")
    parser.add_argument("--bsp-only", action="store_true", help="skip Android product and host tool patches")
    args = parser.parse_args()
    root = args.source.resolve()
    lock = json.loads((PROJECT / "sources.lock.json").read_text())
    expected = {x["component"]: x["commit"] for x in lock["sources"]}
    pending = []
    for component, rel in PATHS.items():
        if args.bsp_only and component in ("build", "aidl", "mesa3d"):
            continue
        repo = root / rel
        head = git(repo, "rev-parse", "HEAD").stdout.strip()
        if head != expected[component]:
            raise SystemExit(f"{rel}: expected {expected[component]}, got {head}; no patches applied")
        patches = sorted((PROJECT / "patches" / component).glob("*.patch"))
        if not patches:
            raise SystemExit(f"No patches found for {component}")
        try:
            remaining = pending_series(repo, patches)
        except RuntimeError as e:
            raise SystemExit(f"Conflicting edits in {rel}; no patches applied\n{e}")
        pending.extend((repo, patch) for patch in remaining)
        if not remaining: print(f"Already applied: {rel}")
    fw = root / "kernel/firmware"
    if git(fw, "rev-parse", "HEAD").stdout.strip() != expected["firmware"]:
        raise SystemExit("Firmware revision differs from sources.lock.json")
    for name in ("boot_xr819.bin", "fw_xr819.bin", "sdd_xr819.bin"):
        if not (fw / "xr819" / name).is_file():
            raise SystemExit(f"Missing XR819 firmware: {name}")
    bt_fw = root / "vendor/realtek/rtkbt"
    if git(bt_fw, "rev-parse", "HEAD").stdout.strip() != expected["bluetooth_firmware"]:
        raise SystemExit("RTL8761B firmware revision differs from sources.lock.json")
    hashes = {
        "rtl8761b_fw": "aabce407190d86f423bee2596a987f9b03ad5b58f8bc3f2eafd4c8d4be93c161",
        "rtl8761b_config": "efa8915db59c5bc30aaa23e1f264656bbf425fcaf091db0954c27752a1d8f7a0",
    }
    for name, digest in hashes.items():
        path = bt_fw / "rtkbt-firmware/lib/firmware/rtlbt" / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"Missing or modified UART Bluetooth firmware: {path}")
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
