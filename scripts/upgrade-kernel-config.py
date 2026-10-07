#!/usr/bin/env python3
"""Upgrade only the exact previous Wukong Pi kernel configuration fragment."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

project = Path(__file__).resolve().parents[1]
repo = Path(sys.argv[1]).resolve() / "device/glodroid"
target = repo / "wukongpi/wukongpi.config"
desired = (project / "device/wukongpi/wukongpi.config").read_bytes()
if not target.exists() or target.read_bytes() == desired:
    sys.exit(0)
old_hashes = {"4e9bb408b37de2d060c36eee4923b7fdaf64117e917588ea8edfacd6c5aa0984", "1d9f7bbe79d671802847484a195ef6c42d7a8508c07765952cee6dead85c3213"}
if hashlib.sha256(target.read_bytes()).hexdigest() not in old_hashes:
    raise SystemExit(f"Custom edits in {target}; preserved. Review before applying kernel configuration updates.")
lock = json.loads((project / "sources.lock.json").read_text())
expected = next(x["commit"] for x in lock["sources"] if x["component"] == "device")
actual = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
if actual != expected:
    raise SystemExit("Device revision differs from sources.lock.json; kernel fragment was not changed.")
target.write_bytes(desired)
print("Upgraded exact legacy Wukong Pi fragment: enabled ext4 ACLs and RTL8761B H5 serdev.")
