#!/usr/bin/env python3
"""Migrate exact deployed product files; preserve any user modifications."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

project = Path(__file__).resolve().parents[1]
repo = Path(sys.argv[1]).resolve() / 'device/glodroid'
old_hashes = {
    'BoardConfig.mk': '480e621f827835bb84fc3a314d243ab1e5e46a382bcc940a956ea7fde326fa10',
    'device.mk': '8a8cea30203234464a8cb5677c4779f0f667c9c131f8da6a44efd48cadb33ddd',
}
pending = []
for name, old_hash in old_hashes.items():
    target = repo / 'wukongpi' / name
    desired = (project / 'device/wukongpi' / name).read_bytes()
    if not target.exists() or target.read_bytes() == desired:
        continue
    if hashlib.sha256(target.read_bytes()).hexdigest() != old_hash:
        raise SystemExit(f'Custom edits in {target}; preserved. Review Bluetooth product migration.')
    pending.append((target, desired))
if pending:
    lock = json.loads((project / 'sources.lock.json').read_text())
    expected = next(x['commit'] for x in lock['sources'] if x['component'] == 'device')
    actual = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != expected:
        raise SystemExit('Device revision differs from sources.lock.json; product files unchanged.')
    for target, desired in pending:
        target.write_bytes(desired)
    print('Upgraded exact legacy Wukong Pi product files: enabled Bluetooth HAL and firmware.')
