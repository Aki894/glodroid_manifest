#!/usr/bin/env python3
"""Check the entire device patch series on a disposable pinned checkout."""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

project = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--device-source', help='Optional local repository to clone without network')
args = parser.parse_args()
lock = json.loads((project / 'sources.lock.json').read_text())
source = next(x for x in lock['sources'] if x['component'] == 'device')
with tempfile.TemporaryDirectory(prefix='wukong-headless-') as tmp:
    tmp = Path(tmp)
    repo = tmp / 'device/glodroid'
    repo.parent.mkdir()
    url = args.device_source or 'https://github.com/GloDroid/glodroid_device.git'
    subprocess.run(['git', 'clone', '--quiet', url, str(repo)], check=True)
    subprocess.run(['git', '-C', str(repo), 'checkout', '--quiet', source['commit']], check=True)
    patches = sorted((project / 'patches/device').glob('*.patch'))
    for patch in patches:
        subprocess.run(['git', '-C', str(repo), 'apply', str(patch)], check=True)
    for patch in patches:
        subprocess.run(['git', '-C', str(repo), 'apply', '--reverse', '--check', str(patch)], check=True)
    subprocess.run(['git', '-C', str(repo), 'diff', '--check'], check=True)
    for name in ['device.mk', 'board/wukong-bridge.sh', 'board/init.wukong-bridge.rc']:
        assert (repo / 'wukongpi' / name).read_bytes() == (project / 'device/wukongpi' / name).read_bytes(), name
    # Simulate an existing Bluetooth-enabled board before the new helper COPY_FILES block.
    target = repo / 'wukongpi/device.mk'
    desired = target.read_bytes()
    target.write_bytes(desired.split(b'\n# Fixed root provisioning entry point')[0])
    subprocess.run(['python3', str(project / 'scripts/upgrade-bluetooth-product.py'), str(tmp)], check=True)
    assert target.read_bytes() == desired
    subprocess.run(['python3', str(project / 'scripts/upgrade-bluetooth-product.py'), str(tmp)], check=True)
    # An unrelated local edit must fail without being overwritten.
    custom = desired + b'\n# local change\n'
    target.write_bytes(custom)
    result = subprocess.run(['python3', str(project / 'scripts/upgrade-bluetooth-product.py'), str(tmp)], capture_output=True)
    assert result.returncode != 0 and target.read_bytes() == custom
print('PASS: pinned patches, repeated preflight, helper copies, exact migration and preservation of local edits')
