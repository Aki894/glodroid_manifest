# RTL8761BTV UART2 first hardware test

This profile targets Android/GloDroid with the locked Linux 5.15.21 kernel,
not Armbian. It assumes a measured module pad mapping, 3.3 V UART I/O,
common ground, external BT_DIS_N/EN pull-up, and no wake GPIOs. The module
model/pad orientation cannot be established from the chip marking alone.

| H3 physical pin | Signal | Module signal |
| --- | --- | --- |
| 11 / PA1 | UART2 RX | TX output |
| 13 / PA0 | UART2 TX | RX input |
| 15 / PA3 | UART2 CTS | RTS output |
| 22 / PA2 | UART2 RTS | CTS input |

UART2 is owned by kernel serdev/H5. Do not start rtk_hciattach on the same
port; a /dev/ttyS2 node is not required. UART0 remains the serial console.
The kernel initializes at 115200 with even parity, reads the vendor UART
baud/RTS-CTS configuration (1,500,000 baud with hardware flow control), and downloads the UART firmware through btrtl.
The new compatible uses the existing RTL8761B UART identification logic,
not the RTL8761BU USB image. Firmware is fetched from Radxa commit
72ef9b75374fdde945e0a19f6aba68e13d4d426d and checked by SHA-256 before patches
are applied. The build stages the verified pair under the kernel firmware
directory and embeds it with CONFIG_EXTRA_FIRMWARE, because initial HCI
setup runs before /vendor is mounted. It is also copied to
vendor/etc/firmware/rtl_bt with the filenames
expected by the kernel. Android inherits the existing GloDroid btlinux HAL,
Bluetooth manifest and feature permissions. ueventd grants access to the
Bluetooth controller's rfkill state without assuming an rfkill number.

No-wake wiring disables H5 runtime autosuspend. This is a first cold-boot
test profile, not validated suspend/resume or repeated enable/disable
support. Without an enable GPIO, reopening at the boot baud after firmware
has changed the UART speed may fail; fully power-cycle the module/board
when testing from a clean state. Assign and measure a spare EN GPIO before
implementing production reset and suspend behaviour.

## Incremental source update

Run from the port directory after pulling wukongpi-bringup:

```sh
python3 scripts/prepare-manifests.py /data/ccc/wukong-build/aosp
cd /data/ccc/wukong-build/aosp
repo sync -c -j2 --no-tags --no-clone-bundle --fail-fast vendor/realtek/rtkbt
cd /data/ccc/wukong-build/port
bash scripts/build.sh /data/ccc/wukong-build/aosp 4
```

The build scripts migrate only exact previous board files and reject custom
edits. This update changes both kernel/DT and Android vendor contents;
flash boot.img to boot and recovery_boot, boot_dtbo.img to dtbo_a, and
super.img in userspace fastboot. No userdata or metadata format is required.
Do not flash a mixture of old/new images.

## Windows ADB checks after a complete power cycle

```powershell
.\adb.exe shell getprop sys.boot_completed
.\adb.exe shell "ls -l /sys/class/bluetooth"
.\adb.exe shell "dmesg | grep -iE 'bluetooth|hci|rtl|firmware|1c28800'"
.\adb.exe shell "lshal | grep -i bluetooth"
.\adb.exe shell svc bluetooth enable
.\adb.exe shell dumpsys bluetooth_manager
.\adb.exe logcat -b all -d > bt-startup.txt
```

Initial firmware download runs during the kernel HCI setup;
inspect dmesg again after enabling. Success requires hci0, a registered HAL,
Bluetooth state ON, and discovering an actual device. If Settings still
crashes, use its AndroidRuntime stack trace to diagnose the app separately.
Do not repeatedly toggle Bluetooth to conceal H5 or reset failures.

Local validation covers patch application/idempotence, guarded migration,
DTS compilation, firmware structure/hashes, and source-level HAL matching.
A full Android build and physical UART communication require the school
server and board; they have not been verified here.

## Early firmware fix

The first hardware log identified RTL8761B over UART but requested firmware
at 3 seconds, before /vendor was mounted. Its HCI setup failed with -ENOENT.
Embedding the 41,361-byte firmware/config pair removes that filesystem timing
dependency. This fix changes only the kernel configuration and build staging;
on a board already flashed with the UART2 Bluetooth update, update boot and
recovery_boot with the rebuilt boot.img. Keep the existing DTBO and super.
Actual firmware download and Android activation remain hardware checks.
