#!/usr/bin/env bash
set -euo pipefail
PROJECT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
SOURCE=$(realpath -- "${1:?Usage: build.sh AOSP_SOURCE [JOBS]}")
JOBS=${2:-$(nproc)}
[[ -f "$SOURCE/build/envsetup.sh" ]] || { echo 'A complete AOSP workspace is required.' >&2; exit 1; }
python3 "$PROJECT/scripts/apply.py" "$SOURCE"
cd "$SOURCE"
# AOSP environment scripts are not compatible with nounset.
set +u
source build/envsetup.sh
lunch wukongpi-userdebug
set -u
make -j"$JOBS" images
python3 "$PROJECT/scripts/verify-config.py" out/target/product/wukongpi/obj/KERNEL_OBJ/.config
repo manifest -r -o out/target/product/wukongpi/resolved-manifest.xml
printf '%s\n' "$SOURCE/out/target/product/wukongpi/images.tar.gz"
