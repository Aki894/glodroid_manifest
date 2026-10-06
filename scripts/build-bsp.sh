#!/usr/bin/env bash
set -euo pipefail
PROJECT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
SOURCE=$(realpath -- "${1:?Usage: build-bsp.sh SOURCE OUTPUT [JOBS]}")
mkdir -p -- "${2:?Output directory required}"
OUTPUT=$(realpath -- "$2")
JOBS=${3:-$(nproc)}
python3 "$PROJECT/scripts/apply.py" "$SOURCE" --bsp-only
export ARCH=arm
export CROSS_COMPILE="$SOURCE/prebuilts/gcc/linux-x86/arm/gcc-linaro-arm-linux-gnueabihf/bin/arm-linux-gnueabihf-"
KERNEL="$SOURCE/kernel/glodroid-stable"
DEVICE="$SOURCE/device/glodroid"
UBOOT="$SOURCE/external/u-boot"
mkdir -p "$OUTPUT/kernel" "$OUTPUT/uboot" "$OUTPUT/artifacts"

make -C "$KERNEL" O="$OUTPUT/kernel" sunxi_defconfig
"$KERNEL/scripts/kconfig/merge_config.sh" -m -O "$OUTPUT/kernel" \
    "$OUTPUT/kernel/.config" \
    "$DEVICE/platform/kernel/android-base.config" \
    "$DEVICE/platform/kernel/android-recommended.config" \
    "$DEVICE/platform/kernel/android-extra.config" \
    "$DEVICE/platform/kernel/android-recommended-arm.config" \
    "$DEVICE/platform/kernel/android-extra-arm.config" \
    "$DEVICE/platform/common/sunxi/sunxi-common.config" \
    "$DEVICE/wukongpi/wukongpi.config"
make -C "$KERNEL" O="$OUTPUT/kernel" olddefconfig
python3 "$PROJECT/scripts/verify-config.py" "$OUTPUT/kernel/.config"
make -C "$KERNEL" O="$OUTPUT/kernel" -j"$JOBS" zImage sun8i-h2-plus-wukongpi.dtb modules
make -C "$UBOOT" O="$OUTPUT/uboot" wukongpi_defconfig
"$UBOOT/scripts/kconfig/merge_config.sh" -m -O "$OUTPUT/uboot" \
    "$OUTPUT/uboot/.config" "$DEVICE/platform/common/uboot.config" \
    "$DEVICE/platform/common/sunxi/uboot.config"
make -C "$UBOOT" O="$OUTPUT/uboot" olddefconfig
make -C "$UBOOT" O="$OUTPUT/uboot" -j"$JOBS"
cpp -P -I "$DEVICE/platform/uboot" \
    -Dplatform_sunxi -Ddevice_wukongpi \
    -D__SYSFS_MMC0_PATH__=soc/1c0f000.mmc \
    -D__SYSFS_MMC1_PATH__=soc/1c11000.mmc \
    "$DEVICE/platform/uboot/bootscript.cpp" > "$OUTPUT/artifacts/boot.txt"
"$OUTPUT/uboot/tools/mkimage" -A arm -O linux -T script -C none -a 0 -e 0 \
    -d "$OUTPUT/artifacts/boot.txt" "$OUTPUT/artifacts/boot.scr"
cp "$OUTPUT/kernel/arch/arm/boot/zImage" "$OUTPUT/artifacts/"
cp "$OUTPUT/kernel/arch/arm/boot/dts/sun8i-h2-plus-wukongpi.dtb" "$OUTPUT/artifacts/"
cp "$OUTPUT/kernel/drivers/net/wireless/xradio/xradio_wlan.ko" "$OUTPUT/artifacts/"
cp "$OUTPUT/uboot/u-boot-sunxi-with-spl.bin" "$OUTPUT/artifacts/"
cp "$OUTPUT/kernel/.config" "$OUTPUT/artifacts/kernel.config"
cp "$OUTPUT/uboot/.config" "$OUTPUT/artifacts/uboot.config"
cp "$PROJECT/sources.lock.json" "$OUTPUT/artifacts/"
printf '%s\n' 'BSP components only. Not an Android image; do not flash this folder as a system.' \
    > "$OUTPUT/artifacts/README.txt"
(cd "$OUTPUT/artifacts" && sha256sum zImage *.dtb *.ko *.bin boot.scr > SHA256SUMS)
