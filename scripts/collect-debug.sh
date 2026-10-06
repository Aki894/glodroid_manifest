#!/usr/bin/env bash
set -euo pipefail
ADB=${ADB:-adb}
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT=${1:-wukongpi-debug-$STAMP}
mkdir -p -- "$OUT"
if [[ -n ${ANDROID_SERIAL:-} ]]; then export ANDROID_SERIAL; fi
"$ADB" wait-for-device
"$ADB" shell getprop > "$OUT/getprop.txt"
"$ADB" shell 'cat /proc/uptime /proc/meminfo /proc/pressure/memory; cat /sys/block/zram0/mm_stat' \
    > "$OUT/memory.txt" 2>&1 || true
"$ADB" shell dumpsys meminfo > "$OUT/dumpsys-meminfo.txt"
"$ADB" shell dumpsys usb > "$OUT/usb.txt"
"$ADB" shell dumpsys wifi > "$OUT/wifi.txt"
"$ADB" shell dumpsys SurfaceFlinger > "$OUT/surfaceflinger.txt"
"$ADB" shell 'dmesg; ls -l /sys/bus/sdio/devices; ls /sys/class/udc; cat /proc/modules' \
    > "$OUT/kernel.txt" 2>&1 || true
"$ADB" logcat -b all -d -v threadtime > "$OUT/logcat.txt"
"$ADB" exec-out 'cat /proc/config.gz' > "$OUT/config.gz" 2>/dev/null || true
printf 'Debug bundle: %s\n' "$OUT"
