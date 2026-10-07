#!/usr/bin/env python3
"""Check known required definitions; provide an advisory literal-defaults scan.

Soong is authoritative for includes, generated modules, namespaces, variants
and library dependencies. The broad text scan is never a fatal graph check.
"""
import argparse
import os
from pathlib import Path
import re

TOKENS = re.compile(r'"(?:\\.|[^"\\])*"|/\*[\s\S]*?\*/|//[^\n]*')
NAMES = re.compile(r'\bname\s*:\s*"([^"\n]+)"')
DEFAULTS = re.compile(r'\bdefaults\s*:\s*\[([^\]]*)\]', re.S)
STRINGS = re.compile(r'"([^"\n]+)"')
REQUIRED = {
    'device/google/cuttlefish/Android.bp': {'cuttlefish_buildhost_only'},
    'prebuilts/gcc/linux-x86/host/x86_64-w64-mingw32-4.8/Android.bp': {'libwinpthread'},
}

def strip_comments(text):
    return TOKENS.sub(lambda m: m.group() if m.group().startswith('"')
                      else '\n' * m.group().count('\n'), text)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    root = args.source.resolve()
    absent = []
    for relative, names in REQUIRED.items():
        path = root / relative
        found = set(NAMES.findall(strip_comments(path.read_text(errors='replace')))) if path.is_file() else set()
        absent.extend(f'{name}: {relative}' for name in sorted(names - found))
    if absent:
        for entry in absent:
            print('Missing verified required source definition: ' + entry)
        raise SystemExit('Required-source preflight failed; restore the listed repositories.')
    providers = set()
    references = []
    count = 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {'.git', '.repo', 'out', 'venvs'}]
        # Android.bp can import other filenames via build = [...].
        for filename in files:
            if not filename.endswith('.bp'):
                continue
            path = Path(directory) / filename
            text = strip_comments(path.read_text(errors='replace'))
            providers.update(NAMES.findall(text))
            for match in DEFAULTS.finditer(text):
                line = text.count('\n', 0, match.start()) + 1
                for name in STRINGS.findall(match.group(1)):
                    references.append((name, str(path.relative_to(root)), line))
            count += 1
    unresolved = sorted(set(x for x in references if x[0] not in providers))
    print(f'Source audit: {count} .bp files, {len(providers)} literal named modules, {len(references)} defaults references.')
    for name, path, line in unresolved[:20]:
        print(f'Advisory unresolved literal defaults: {name}: {path}:{line}')
    if unresolved:
        print(f'{len(unresolved)} advisory references remain. This text scan does not model all Blueprint semantics; Soong will validate the actual graph.')
    print('Verified required-source checks passed; continuing to authoritative Soong validation.')

if __name__ == '__main__':
    main()
