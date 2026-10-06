# WukongPi bring-up source and product audit

Revision 2 keeps the locked GloDroid v0.7.2 snapshot and XR819 support.
This is an incremental bring-up trim, not the final CarPlay appliance product.

## Source download

`sync-source.sh` installs `manifests/wukongpi-minimal.xml` into
`.repo/local_manifests` after initializing the locked upstream manifest and
before the first `repo sync`. The upstream manifest is not replaced or rebased.
The overlay removes these 15 repositories by both name and path:

- GloDroid external preinstalled APKs.
- Megous and Broadcom kernels.
- RTL8189ES and RTL8189FS vendor modules (their makefile registration is also gated).
- GloDroid AArch64, ARM-EABI and OpenRISC toolchains; ARM Linux hard-float GCC remains.
- Crust and its ARM Trusted Firmware; this ARMv7 product does not build BL31/SCP.
- Raspberry Pi firmware and nonfree firmware.
- Megous firmware, Amlogic boot FIP and Rockchip rkbin.

The stable kernel, U-Boot, XR819-containing Armbian firmware, Mesa/Lima,
minigbm, DRM composer and ARM hard-float compiler remain. Camera build support
libraries and shared AOSP repositories remain to avoid unverified global Soong
dependencies. Removing a root package does not imply removing its entire source
repository or every transitive dependency.

## Product packages

The new build/make patch is locked to
`51005914bdad1ec58554739eddbfcc21fdf3927a`. Product guards apply only to WukongPi.
They filter 19 entries where they are defined, before product inheritance is
resolved, rather than trying to subtract inherited packages in device.mk:

- Full base: LiveWallpapersPicker, PhotoTable.
- Product: Browser2, Calendar, Camera2, DeskClock, Gallery2, Music, QuickSearchBox.
- System extension: Launcher3QuickStep, WallpaperCropper.
- System: BasicDreams, BluetoothMidiService, BuiltInPrintService, EasterEgg,
  NfcNci, PrintRecommendationService, PrintSpooler, SecureElement.

The duplicate GloDroid Launcher3QuickStep addition is also gated. The existing
camera HAL and extra APK guards are retained. A product-specific copy of the
common init file removes the preinstall service and boot-completed trigger;
all other common init actions are retained.

Settings, Provision and SystemUI stay available for bring-up. There is no HOME
launcher in this product; use serial/ADB for operation and diagnostics. This is
not a finished automatic bridge startup path. Shared providers, telephony-related
framework components, location, VPN, networking, audio, USB, package management,
Binder, graphics and recovery/update plumbing are deliberately retained.
Bluetooth hardware/HAL remains disabled until a Bluetooth-capable module is fitted.

After lunch, build.sh saves the resolved PRODUCT_PACKAGES to
`out/target/product/wukongpi/product-packages.txt` and checks exclusions and
essential bring-up packages before `make images`. This checks root package
selection, not the complete transitive installation graph.

## Validation and limits

- Device patch checked forward/reverse against the actual locked device commit.
- Build patch checked forward/reverse against exact locked upstream product files.
- GNU Make evaluated all four modified AOSP product files: exclusions active for
  WukongPi and original entries retained for Orange Pi PC.
- All overlay removals matched unique upstream name/path pairs; essential BSP
  repositories checked as retained.
- Shell/Python syntax and patch whitespace checked on modified source.

Full AOSP compilation and boot are not yet validated. Runtime RAM savings and
download/build disk savings have not been measured. The 300 GiB free-space gate
is retained; the current 148 GiB server space cannot be claimed sufficient.

For a fresh checkout that has not synchronized AOSP, pull the branch and run
the normal sync script. If a workspace already exists, the sync script refuses
to reset it. Review/copy the overlay into its `.repo/local_manifests` and sync
manually. Previously downloaded repositories are not automatically deleted by
this workflow. Already-applied revision 1 patches need a reviewed migration;
apply.py intentionally refuses partially matching edits instead of resetting them.
