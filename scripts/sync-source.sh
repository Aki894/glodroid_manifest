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
# Explicit opt-in for experiments on constrained storage; not a size guarantee.
WUKONG_SKIP_DISK_CHECK=${WUKONG_SKIP_DISK_CHECK:-0}
case "$WUKONG_SKIP_DISK_CHECK" in
    0)
        if (( FREE_KIB < 300 * 1024 * 1024 )); then
            echo 'Prepare at least 300 GiB of free disk for the full AOSP source and build.' >&2
            echo 'To attempt a constrained build, explicitly set WUKONG_SKIP_DISK_CHECK=1.' >&2
            exit 1
        fi
        ;;
    1)
        echo "Disk preflight skipped explicitly; available: $(( FREE_KIB / 1024 / 1024 )) GiB. Actual source/build usage is not yet measured." >&2
        ;;
    *)
        echo 'WUKONG_SKIP_DISK_CHECK must be 0 or 1.' >&2
        exit 1
        ;;
esac
repo init -u https://github.com/GloDroid/glodroid_manifest.git \
    -b b939e72146bf71bbb73cdeba374ba1d78db6a236 -m default.xml --depth=1 \
    --repo-url="${WUKONG_REPO_URL:-https://github.com/GerritCodeReview/git-repo.git}" \
    --no-clone-bundle
python3 "$PROJECT/scripts/prepare-manifests.py" "$PWD"
repo sync -c -j"$JOBS" --no-tags --no-clone-bundle --fail-fast
repo manifest -r -o upstream-resolved-manifest.xml
