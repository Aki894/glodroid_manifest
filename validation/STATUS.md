# Bring-up validation, 2026-10-07

| Check | Result |
|---|---|
| Locked source revisions | PASS, see sources.lock.json |
| Patch preflight, clean worktrees | PASS |
| Applying all four repository patches | PASS |
| Repeat application without changes | PASS |
| Shell/Python syntax | PASS |
| Workflow YAML parsing | PASS |
| Effective Linux configuration after olddefconfig | PASS, 20 required settings |
| Linux 5.15.21 zImage + modules | PASS, ARM GCC 7.4.1 |
| WukongPi kernel DTB | PASS |
| XR819 module | PASS, ELF 32-bit ARM EABI5 |
| U-Boot + SPL + binman image | PASS, ARM GCC 7.4.1 |
| Android bootscript generation and mkimage | PASS |
| Complete AOSP/Soong image build | NOT RUN, current environment has only 30 GiB free |
| Android boot / ADB / headless on hardware | NOT RUN |
| Android XR819 STA / USB AOA on hardware | NOT RUN |
| 512 MB runtime memory and repeated reboot | NOT RUN |
| GitHub Actions build | To be checked from the corresponding run |

DTS readback: model=Wukong Pi, mmc1 Wi-Fi compatible=xradio,xr819,
USB OTG dr_mode=peripheral. Effective CONFIG_XRADIO=m,
CONFIG_MEMCG=y, CONFIG_MEMCG_SWAP=y, CONFIG_PSI=y,
CONFIG_ZRAM=y, CONFIG_USB_CONFIGFS_F_ACC=y, CMA_SIZE_MBYTES=32.

Local build host: Linux x86-64, Python 3.12, extracted native build dependencies,
setuptools 75.8.2 for U-Boot pylibfdt/binman. Some upstream compiler warnings remain;
the final build commands exited successfully. Ubuntu 20.04 is the target host
for the complete GloDroid build. Components are not a bootable Android image.
