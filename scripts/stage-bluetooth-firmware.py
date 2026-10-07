#!/usr/bin/env python3
"""Stage locked UART firmware for built-in loading before /vendor is mounted."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

project = Path(__file__).resolve().parents[1]
root = Path(sys.argv[1]).resolve()
lock = json.loads((project / 'sources.lock.json').read_text())
expected = {row['component']: row['commit'] for row in lock['sources']}
for component, path in [('kernel', 'kernel/glodroid-stable'),
                        ('bluetooth_firmware', 'vendor/realtek/rtkbt')]:
    actual = subprocess.check_output(['git', '-C', str(root / path), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != expected[component]:
        raise SystemExit(f'{path}: unexpected revision; firmware was not staged')
hashes = {

        "rtl8761b_fw": "aabce407190d86f423bee2596a987f9b03ad5b58f8bc3f2eafd4c8d4be93c161",
        "rtl8761b_config": "efa8915db59c5bc30aaa23e1f264656bbf425fcaf091db0954c27752a1d8f7a0",
}
pending = []
for name, digest in hashes.items():
    source = root / 'vendor/realtek/rtkbt/rtkbt-firmware/lib/firmware/rtlbt' / name
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise SystemExit(f'Modified UART firmware: {source}; no files staged')
    target = root / 'kernel/glodroid-stable/firmware/rtl_bt' / (name + '.bin')
    if target.exists() and target.read_bytes() != data:
        raise SystemExit(f'Custom staged firmware: {target}; preserved')
    pending.append((target, data))
for target, data in pending:
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
print('Staged verified RTL8761B firmware/config for early built-in loading (41361 bytes).')
