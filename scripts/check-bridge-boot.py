#!/usr/bin/env python3
"""Exercise missing/pre-existing/failing interface setup without real hardware."""
from pathlib import Path
import subprocess
import tempfile

project=Path(__file__).resolve().parents[1]
script=(project/'device/wukongpi/board/wukong-bridge.sh').read_text()
function=script.split('prepare_network() {',1)[1].split('\n}\n',1)[0]
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    (root/'net/wlan0').mkdir(parents=True)
    trace=root/'trace'
    iw=root/'iw'
    iw.write_text(f'#!/bin/sh\necho iw >> {trace}\n[ ! -f {root}/fail ] || exit 1\nmkdir -p {root}/net/p2p0\n')
    ip=root/'ip';ip.write_text(f'#!/bin/sh\necho ip >> {trace}\n')
    iw.chmod(0o755);ip.chmod(0o755)
    body=function.replace('/sys/class/net',str(root/'net')).replace('/system/bin/iw',str(iw)).replace('/system/bin/ip',str(ip))
    def prepare():subprocess.run(['sh','-c','prepare_network() {'+body+'\n}\nprepare_network'],check=True)
    prepare();assert trace.read_text().splitlines()==['iw','ip']
    prepare();assert trace.read_text().splitlines()==['iw','ip'], 'Existing group must not be touched'
    (root/'net/p2p0').rmdir();(root/'fail').touch()
    subprocess.run(['sh','-c','prepare_network() {'+body+'\n}\nprepare_network'],check=False)
    assert trace.read_text().splitlines()==['iw','ip','iw'], 'Failed creation must not bring another interface up'
    (root/'fail').unlink();prepare()
    assert trace.read_text().splitlines()==['iw','ip','iw','iw','ip']
print('PASS: initial interface, no existing-group churn, creation failure and retry')
