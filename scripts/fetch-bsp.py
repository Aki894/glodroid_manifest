#!/usr/bin/env python3
"""Fetch only the small BSP dependencies, not all AOSP projects."""
import argparse
import json
import subprocess
from pathlib import Path
from apply import PATHS, PROJECT

parser = argparse.ArgumentParser()
parser.add_argument("destination", type=Path)
args = parser.parse_args()
root = args.destination.resolve()
paths = dict(PATHS, firmware="kernel/firmware",
             bluetooth_firmware="vendor/realtek/rtkbt", toolchain=
             "prebuilts/gcc/linux-x86/arm/gcc-linaro-arm-linux-gnueabihf")
paths.pop("build", None)
paths.pop("aidl", None)
paths.pop("mesa3d", None)
for row in json.loads((PROJECT / "sources.lock.json").read_text())["sources"]:
    component = row["component"]
    if component not in paths:
        continue
    dest = root / paths[component]
    if dest.exists():
        head = subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"], text=True).strip()
        if head != row["commit"]:
            raise SystemExit(f"Refusing to overwrite {dest}: unexpected commit")
        continue
    dest.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "remote", "add", "origin", row["repository"]], check=True)
    subprocess.run(["git", "-C", str(dest), "fetch", "--depth=1", "origin", row["commit"]], check=True)
    subprocess.run(["git", "-C", str(dest), "checkout", "--detach", "FETCH_HEAD"], check=True)
