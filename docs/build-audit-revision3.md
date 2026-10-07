# Build audit, revision 3

## Findings

The historical lightweight manifest removes repositories by board/host purpose.
Soong validates a global source graph before the selected product's install list
is compiled. Therefore a repository outside PRODUCT_PACKAGES can still supply
defaults, licenses or host libraries required by retained source.

Confirmed at the exact locked commits:

- `device/google/cuttlefish` defines `cuttlefish_buildhost_only` and its defaults.
  The retained opengl-transport virglrenderer build references it.
- `prebuilts/gcc/linux-x86/host/x86_64-w64-mingw32-4.8/Android.bp` defines
  `libwinpthread`, its notice filegroup and licenses. The current Linux host
  configuration defaults HOST_CROSS_OS to Windows; liblog/libhost require the
  Windows library variants. Defining a placeholder or ignoring missing
  dependencies would leave missing compiler inputs later.
- `common/lowram/device-common-1gb.mk` used a mutable LOCAL_PATH for
  init.lowram.rc. It now uses the actual common/lowram source path explicitly.
  No memory property or zram size is changed by this incremental patch.

## Source policy

prepare-manifests.py retains all existing non-kernel/non-Darwin projects
previously excluded by upstream lightweight.xml. The remaining 8 exclusions are
six other-board binary kernel repositories and Darwin Clang/Go prebuilts.
Ten build-definition repositories remain in the manifest, including Cuttlefish,
ATV, Bonito/Coral device/sepolicy, context hub, VR services, Linux GCC and MinGW.
The script emits restored-build-projects.txt for a scoped incremental sync.
This avoids synchronizing/resetting already-patched Android repositories.

The separate 15-entry WukongPi source overlay still removes unrelated GloDroid
kernels, external APKs, board firmware and unused toolchains. Its exclusions
were checked against target-dependent kernel/U-Boot/ATF/Crust build recipes.
The RTL8189 vendor makefile registrations are gated on non-WukongPi products.
ARM hard-float GCC, stable kernel, U-Boot, XR819/Armbian firmware, Mesa, minigbm,
DRM composer and camera build support libraries remain.

No commit in aosp.xml or sources.lock.json is updated. Product packages remain
trimmed; restoring source definitions is not selecting those devices or apps.
Current resolved root package count from the server is 722; it is not a measure
of installed package count, runtime RAM, image size or compilation completion.

## Preflight added

- audit-source.py traverses the actual workspace Android.bp files and checks
  absent literal defaults definitions, plus known Cuttlefish/MinGW definitions.
  It ignores comments and excludes .repo/.git/out from traversal. It does not
  implement Soong namespaces, generated modules, variants or the full link graph.
- verify-copy-files.py checks every resolved PRODUCT_COPY_FILES source exists.
- The previous package audit, exact source commit checks, all-repository patch
  preflight, kernel configuration checks and final manifest recording remain.

## Validation performed here

- Checked host cross-build selection in the actual locked build/make source.
- Read exact locked MinGW Android.bp and Cuttlefish source definitions.
- Evaluated both local manifest overlays against locked aosp.xml/glodroid.xml.
- Checked old and incremental device/build patches against exact locked source.
- Ran shell/Python syntax checks and positive/negative preflight checks for
  comment handling, missing defaults and missing copy-file inputs.
- Reviewed kernel fragment, ARMv7/GCC selection, vendor_dlkm module paths,
  USB configuration copy paths, camera/preinstall guards and zram fstab.

Full source-graph preflight and full AOSP compilation must still run on the
server's complete workspace. No full build or hardware boot is claimed here.
The headless/HAL, 512 MiB memory survival, XR819 networking and AOA behavior
remain hardware validation gates. Source restoration disk usage on the server
is not yet measured.
