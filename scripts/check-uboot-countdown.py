#!/usr/bin/env python3
"""Apply the additive countdown patch to the exact imported board config."""
from pathlib import Path
import subprocess
import tempfile
project=Path(__file__).resolve().parents[1]
patch=(project/'patches/uboot/0001-wukongpi-bringup.patch').read_text()
part=patch.split('+++ b/configs/wukongpi_defconfig\n',1)[1].split('\ndiff --git',1)[0]
old='\n'.join(line[1:] for line in part.splitlines() if line.startswith('+'))+'\n'
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);(root/'configs').mkdir();target=root/'configs/wukongpi_defconfig';target.write_text(old)
    subprocess.run(['git','-C',tmp,'init','--quiet'],check=True)
    subprocess.run(['git','-C',tmp,'apply',str(project/'patches/uboot/0003-wukongpi-zero-boot-countdown.patch')],check=True)
    assert target.read_text()==(project/'uboot/wukongpi_defconfig').read_text()
print('PASS: additive U-Boot config patch matches shipped board definition')
