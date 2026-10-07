#!/usr/bin/env python3
"""Keep build definitions; exclude only historical binary kernels/Darwin tools."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

# This is deliberately narrower than upstream lightweight.xml. Do not infer
# that a device repository is unused by the global Soong graph.
EXCLUDE = {
    'device/amlogic/yukawa-kernel', 'device/linaro/hikey-kernel',
    'device/linaro/poplar-kernel', 'device/ti/beagle-x15-kernel',
    'device/google/bonito-kernel', 'device/google/coral-kernel',
    'platform/prebuilts/clang/host/darwin-x86',
    'platform/prebuilts/go/darwin-x86',
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    root = args.source.resolve()
    upstream = root / '.repo/manifests'
    projects = {p.get('name'): p.get('path', p.get('name'))
                for p in ET.parse(upstream / 'aosp.xml').getroot().findall('project')}
    lightweight = ET.parse(upstream / 'lightweight.xml').getroot()
    overlay = ET.Element('manifest')
    retained = []
    for node in lightweight:
        if node.tag == 'include':
            continue
        if node.tag != 'remove-project':
            raise SystemExit(f'Unexpected lightweight element: {node.tag}')
        name = node.get('name')
        if name not in projects:
            continue
        if name in EXCLUDE:
            node.set('optional', 'true')
            overlay.append(node)
        else:
            retained.append(projects[name])
    destination = root / '.repo/local_manifests'
    destination.mkdir(parents=True, exist_ok=True)
    ET.indent(overlay)
    ET.ElementTree(overlay).write(destination / '00-upstream-lightweight.xml',
                                  encoding='utf-8', xml_declaration=True)
    project = Path(__file__).resolve().parents[1]
    (destination / 'wukongpi-minimal.xml').write_bytes(
        (project / 'manifests/wukongpi-minimal.xml').read_bytes())
    report = root / 'restored-build-projects.txt'
    report.write_text(''.join(p + '\n' for p in retained))
    print(f'Kept {len(overlay)} binary-only exclusions; retained {len(retained)} build-definition repositories.')
    print(f'Incremental sync project list: {report}')

if __name__ == '__main__':
    main()
