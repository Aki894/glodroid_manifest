#!/usr/bin/env python3
"""Exercise recorder rotation, active-session exit and symlink refusal off-device."""
from pathlib import Path
import subprocess
import tempfile

project=Path(__file__).resolve().parents[1]
script=(project/'device/wukongpi/board/wukong-bootlog.sh').read_text()
with tempfile.TemporaryDirectory() as tmp:
    base=Path(tmp);root=base/'recordings';bin=base/'bin';bin.mkdir()
    boot=base/'boot-id';uptime=base/'uptime';startup=base/'startup.json'
    boot.write_text('boot-one\n');uptime.write_text('12.34 15.00\n')
    startup.write_text('{"bootId":"boot-one","firstCarPlayActiveMs":1000}')
    for name,body in {
        'getprop': 'if [ "$#" = 0 ]; then echo properties; elif [ "$1" = sys.boot_completed ]; then echo 1; elif [ "$1" = sys.user.0.ce_available ]; then echo true; else echo running; fi',
        'dmesg':'echo kernel', 'sleep':'exit 0','sync':'exit 0',
        'logcat':'while [ "$#" -gt 0 ]; do if [ "$1" = -f ]; then shift; echo timing > "$1"; break; fi; shift; done',
    }.items():
        file=bin/name;file.write_text('#!/bin/sh\n'+body+'\n');file.chmod(0o755)
    import os
    env=dict(os.environ,PATH=str(bin)+':'+os.environ['PATH'])
    code=script.replace('/data/vendor/wukong-boot',str(root)).replace('/proc/sys/kernel/random/boot_id',str(boot)).replace('/proc/uptime',str(uptime)).replace('/data/user/0/com.shihab.diplay.hudtest/files/board-startup.json',str(startup))
    def run():return subprocess.run(['sh','-c',code],env=env,capture_output=True,timeout=15)
    assert run().returncode==0
    stages=(root/'current/stages.tsv').read_text()
    assert 'user_ce_available' in stages and 'boot_completed' in stages
    assert 'first_active_observed' in stages and 'collector_finished' in stages
    original=(root/'current/boot-id').read_bytes()
    assert run().returncode==0 and not (root/'previous').exists(), 'Same boot must not rotate'
    boot.write_text('boot-two\n');startup.write_text('{"bootId":"boot-one","firstCarPlayActiveMs":1000}')
    assert run().returncode==0
    assert (root/'previous/boot-id').read_bytes()==original
    assert 'first_active_observed' not in (root/'current/stages.tsv').read_text(), 'Previous app metadata must not stop capture'
    boot.write_text('boot-three\n')
    assert run().returncode==0
    assert (root/'previous/boot-id').read_text().strip()=='boot-two'
    import shutil
    shutil.rmtree(root/'current');(root/'current').symlink_to(base/'bin',target_is_directory=True)
    assert run().returncode!=0, 'Do not capture or rotate through a symlink'
print('PASS: two-boot retention, same-boot idempotence, active cutoff, stale metadata, unsafe symlink')
