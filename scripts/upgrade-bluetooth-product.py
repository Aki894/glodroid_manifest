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
    'device.mk': ('c4a21c56386740952f9b42cbb969e6069509fb55614388800fba44ca2c938d65', '1e5e4a317ee087a1347bc3d9f4a07f5936e95195d7d09cbcfc3932614066a6a0', '8a8cea30203234464a8cb5677c4779f0f667c9c131f8da6a44efd48cadb33ddd', 'f9fe0895da7e999c8407fb50fdc8a16fc3aac2b768652a8e141f7e4ac3d9c3b2', 'efcfba17a5800008c991fff9978340a8aacf0a7e15a4375dced48f4d338292d0'),
}
pending = []
for name, old_hash in old_hashes.items():
    target = repo / 'wukongpi' / name
    desired = (project / 'device/wukongpi' / name).read_bytes()
    if name == 'device.mk' and '--prepare-patches' in sys.argv:
        # Prepare legacy migrations at the previous patch boundary, so the
        # new overlapping patch can still be applied as a complete series.
        if target.exists() and target.read_bytes() == desired: continue
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == 'c4a21c56386740952f9b42cbb969e6069509fb55614388800fba44ca2c938d65': continue
        desired = desired.split(b'\n# Dedicated forwarding appliance')[0].rstrip() + b'\n'
        desired = b''.join(line for line in desired.splitlines(keepends=True) if b'/board/wukong-bootlog.sh:' not in line)
    if not target.exists() or target.read_bytes() == desired:
        continue
    if hashlib.sha256(target.read_bytes()).hexdigest() not in (old_hash if isinstance(old_hash, tuple) else (old_hash,)):
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
    print('Upgraded exact known Wukong Pi product files: Bluetooth and board provisioning.')
