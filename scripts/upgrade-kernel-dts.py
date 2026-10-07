#!/usr/bin/env python3
"""Upgrade only exact, previously deployed Wukong Pi device trees."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

project = Path(__file__).resolve().parents[1]
repo = Path(sys.argv[1]).resolve() / "kernel/glodroid-stable"
target = repo / "arch/arm/boot/dts/sun8i-h2-plus-wukongpi.dts"
desired = (project / "kernel/sun8i-h2-plus-wukongpi.dts").read_bytes()
if not target.exists() or target.read_bytes() == desired:
    sys.exit(0)
old_hashes = {
    "b192f3a037fcd19aaa37bfb495f093000d26efbeff0046835884b24867a42e37",  # Before KMS
    "9250af2fd0503ba9b1570d9a3dad0d27a8df4973b61ad460d39c2cce6cd684bc",  # KMS, before codec
}
if hashlib.sha256(target.read_bytes()).hexdigest() not in old_hashes:
    raise SystemExit(f"Custom edits in {target}; preserved. Review before applying board DTS updates.")
lock = json.loads((project / "sources.lock.json").read_text())
expected = next(x["commit"] for x in lock["sources"] if x["component"] == "kernel")
actual = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
if actual != expected:
    raise SystemExit("Kernel revision differs from sources.lock.json; DTS was not changed.")
target.write_bytes(desired)
print("Upgraded exact legacy Wukong Pi DTS: enabled internal KMS controller graph and H3 audio codec.")
