# Headless board integration

Use DiPlay `integration/wukongpi-headless` board APK and CarProjection
`wukongpi-headless` board APK. Normal phone APKs do not have the root provisioner.

The additional device patch copies a fixed vendor init service and a wrapper.
After user unlock/boot completion, it runs BoardProvisioner from the installed
DiPlay APK as root. Only the configured two packages are granted runtime,
USB host/accessory and scoped VPN authorization. It does not disable global
USB permission dialogs, change gadget functions or grant arbitrary apps.

The UART Bluetooth driver/firmware and existing XR819 configuration are unchanged.
The service requires the current userdebug, permissive board SELinux setup;
it is not a finished enforcing/production policy. The privileged operations
are isolated from the non-root media/Web process. Pairing approval is restricted
to an explicit 120-second window and numeric-comparison/consent variants.
iPhone-side approval is still required.

Build using the usual port build script; this changes vendor files in super.img,
not the Bluetooth DTB or kernel. Keep the current successful boot.img. Install
the APKs before enabling the service. Do not format userdata during this update.
Use the paired repository install/readme instructions after CI verification.

Maintenance display-off uses Android 13 SurfaceControl physical display power;
protocol sessions never depend on a display Surface. HWC behavior and continued
wireless/USB operation with display output off remain hardware acceptance tests.

Paired deployment and Windows backup/rollback instructions:
https://github.com/Aki894/DiPlay/blob/integration/wukongpi-headless/docs/WUKONGPI-HEADLESS.md

The helper can be disabled persistently with `persist.wukong.bridge.enabled=0`.
The Windows rollback script uses this before restoring normal APKs. The installer
sets it back to 1 only after both board APKs and vendor init files are present.
`check-headless-port.py` validates clean application and reverse preflight of the
entire pinned device patch series, exact old-product migration, repeat execution,
and preservation of unrelated local edits.


下一阶段自动启动、现场管理、启动提速及保留数据的更新步骤见 [appliance-startup.md](appliance-startup.md)。
