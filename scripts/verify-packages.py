#!/usr/bin/env python3
"""Check the resolved AOSP product, after inheritance, before compiling images."""
import sys
from pathlib import Path

REMOVED = {
    'LiveWallpapersPicker', 'PhotoTable', 'Browser2', 'Calendar', 'Camera2',
    'DeskClock', 'Gallery2', 'Music', 'QuickSearchBox', 'Launcher3QuickStep',
    'WallpaperCropper', 'BasicDreams', 'BluetoothMidiService',
    'BuiltInPrintService', 'EasterEgg', 'NfcNci', 'PrintRecommendationService',
    'PrintSpooler', 'SecureElement', 'FDroid', 'SkyTube', 'fenix',
    'shade-launcher3', 'camera.libcamera',
    'android.hardware.camera.provider@2.5-external-service',
    'android.hardware.camera.provider@2.5-service_64',
}
REQUIRED = {'Settings', 'SystemUI', 'Provision', 'FusedLocation', 'VpnDialogs',
            'wpa_supplicant', 'hostapd', 'wificond', 'libGLES_android'}

def main():
    packages = set(Path(sys.argv[1]).read_text().split())
    unexpected = REMOVED & packages
    missing = REQUIRED - packages
    if unexpected or missing:
        raise SystemExit(f'Package audit failed: unexpected={sorted(unexpected)}, missing={sorted(missing)}')
    print(f'Minimal product package audit passed ({len(packages)} root packages).')

if __name__ == '__main__':
    main()
