#!/usr/bin/env python3
"""Check the effective configuration after olddefconfig, not just fragments."""
import sys
from pathlib import Path
config = {}
for line in Path(sys.argv[1]).read_text().splitlines():
    if line.startswith("CONFIG_") and "=" in line:
        name, value = line.split("=", 1)
        config[name] = value
required = {name: "y" for name in (
    "CONFIG_SWAP", "CONFIG_MEMCG", "CONFIG_MEMCG_SWAP", "CONFIG_PSI",
    "CONFIG_ZRAM", "CONFIG_ZSMALLOC", "CONFIG_CFG80211", "CONFIG_MAC80211",
    "CONFIG_MMC_SUNXI", "CONFIG_PWRSEQ_SIMPLE", "CONFIG_USB_MUSB_GADGET",
    "CONFIG_USB_CONFIGFS_F_FS", "CONFIG_USB_CONFIGFS_F_ACC",
    "CONFIG_USB_CONFIGFS_UEVENT", "CONFIG_SERIAL_8250_CONSOLE",
    "CONFIG_ANDROID_BINDER_IPC", "CONFIG_ANDROID_BINDERFS", "CONFIG_DRM_LIMA",
    "CONFIG_DRM_SUN4I", "CONFIG_DRM_SUN8I_DW_HDMI", "CONFIG_DRM_SUN8I_MIXER",
    "CONFIG_EXT4_FS", "CONFIG_EXT4_FS_POSIX_ACL")}
required.update(CONFIG_CMA_SIZE_MBYTES="32", CONFIG_XRADIO="m")
errors = [f"{name}: expected {value}, got {config.get(name, 'disabled')}"
          for name, value in required.items() if config.get(name) != value]
for name in ("CONFIG_XRADIO_5GHZ_SUPPORT", "CONFIG_USB_MUSB_HOST", "CONFIG_PSI_DEFAULT_DISABLED"):
    if config.get(name) in ("y", "m"):
        errors.append(f"{name} must be disabled")
if errors:
    raise SystemExit("\n".join(errors))
print(f"Effective kernel configuration verified ({len(required)} required settings)")
