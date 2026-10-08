#!/usr/bin/env bash
set -euo pipefail
PROJECT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
SOURCE=$(realpath -- "${1:?Usage: build.sh AOSP_SOURCE [JOBS]}")
JOBS=${2:-$(nproc)}
[[ -f "$SOURCE/build/envsetup.sh" ]] || { echo 'A complete AOSP workspace is required.' >&2; exit 1; }
# Capture Python before envsetup replaces PATH; do not resolve virtualenv symlinks.
HOST_PYTHON=$(python3 -c 'import sys; print(sys.executable)')
"$HOST_PYTHON" - <<'PYTHON'
import sys
try:
    import mesonbuild.coredata
    import mako
except ImportError as exc:
    raise SystemExit(f"Missing Mesa host dependency in {sys.executable}: {exc}. Activate the wukong-build virtualenv.")
if mesonbuild.coredata.version != "0.61.5":
    raise SystemExit(f"Expected Meson 0.61.5, got {mesonbuild.coredata.version} in {sys.executable}")
print(f"Mesa host Python: {sys.executable}; Meson: {mesonbuild.coredata.version}")
PYTHON
[[ -x "$SOURCE/prebuilts/build-tools/linux-x86/bin/ninja" ]] || { echo 'Missing AOSP prebuilt Ninja.' >&2; exit 1; }
[[ -x /usr/bin/pkg-config ]] || { echo 'Install pkg-config: apt-get install -y pkg-config' >&2; exit 1; }
python3 "$PROJECT/scripts/upgrade-kernel-dts.py" "$SOURCE"
python3 "$PROJECT/scripts/upgrade-kernel-config.py" "$SOURCE"
python3 "$PROJECT/scripts/upgrade-bluetooth-product.py" "$SOURCE" --prepare-patches
python3 "$PROJECT/scripts/audit-source.py" "$SOURCE"
python3 "$PROJECT/scripts/apply.py" "$SOURCE"
python3 "$PROJECT/scripts/stage-bluetooth-firmware.py" "$SOURCE"
cd "$SOURCE"
# AOSP environment scripts are not compatible with nounset.
set +u
source build/envsetup.sh
lunch wukongpi-userdebug
mkdir -p out/target/product/wukongpi
get_build_var PRODUCT_PACKAGES > out/target/product/wukongpi/product-packages.txt
python3 "$PROJECT/scripts/verify-packages.py" out/target/product/wukongpi/product-packages.txt
get_build_var PRODUCT_COPY_FILES > out/target/product/wukongpi/product-copy-files.txt
python3 "$PROJECT/scripts/verify-copy-files.py" "$SOURCE" out/target/product/wukongpi/product-copy-files.txt
# The make wrapper calls envsetup functions even after Ninja finishes.
# Keep nounset disabled until that wrapper returns.
make -j"$JOBS" MESA3D_HOST_PYTHON="$HOST_PYTHON" images
set -u
python3 "$PROJECT/scripts/verify-config.py" out/target/product/wukongpi/obj/KERNEL_OBJ/.config
repo manifest -r -o out/target/product/wukongpi/resolved-manifest.xml
printf '%s\n' "$SOURCE/out/target/product/wukongpi/images.tar.gz"
