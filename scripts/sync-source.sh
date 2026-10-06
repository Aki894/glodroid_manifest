#!/usr/bin/env bash
set -euo pipefail
PROJECT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
SOURCE=${1:?Usage: sync-source.sh EMPTY_SOURCE_DIRECTORY [JOBS]}
JOBS=${2:-4}
mkdir -p -- "$SOURCE"
cd -- "$SOURCE"
command -v repo >/dev/null || { echo 'Install the Android repo tool first.' >&2; exit 1; }
if [[ -e .repo ]]; then
    echo 'An existing repo workspace was found. Sync it manually; this script will not reset it.' >&2
    exit 1
fi
FREE_KIB=$(df -Pk . | awk 'NR == 2 {print $4}')
if (( FREE_KIB < 300 * 1024 * 1024 )); then
    echo 'Prepare at least 300 GiB of free disk for the full AOSP source and build.' >&2
    exit 1
fi
repo init -u https://github.com/GloDroid/glodroid_manifest.git \
    -b b939e72146bf71bbb73cdeba374ba1d78db6a236 -m lightweight.xml --depth=1
mkdir -p .repo/local_manifests
cp "$PROJECT/manifests/wukongpi-minimal.xml" .repo/local_manifests/wukongpi-minimal.xml
repo sync -c -j"$JOBS" --no-tags --fail-fast
repo manifest -r -o upstream-resolved-manifest.xml
