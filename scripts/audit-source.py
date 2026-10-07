#!/usr/bin/env python3
"""Check known build sources and scan literal Soong defaults references.

This is a preflight, not a replacement for Soong: namespace visibility,
generated modules, variant selection, library links and source paths still
need the actual AOSP build. Only absent literal defaults are reported here.
"""
import argparse
import os
from pathlib import Path
import re

TOKENS = re.compile(r'"(?:\\.|[^"\\])*"|/\*[\s\S]*?\*/|//[^\n]*')
NAMES = re.compile(r'\bname\s*:\s*"([^"\n]+)"')
DEFAULTS = re.compile(r'\bdefaults\s*:\s*\[([^\]]*)\]', re.S)
STRINGS = re.compile(r'"([^"\n]+)"')

def strip_comments(text):
    return TOKENS.sub(lambda m: m.group() if m.group().startswith('"')
                      else '\n' * m.group().count('\n'), text)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    root = args.source.resolve()
    providers = set()
    references = []
    count = 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {'.git', '.repo', 'out', 'venvs'}]
        if 'Android.bp' not in files:
            continue
        path = Path(directory) / 'Android.bp'
        text = strip_comments(path.read_text(errors='replace'))
        providers.update(NAMES.findall(text))
        for match in DEFAULTS.finditer(text):
            line = text.count('\n', 0, match.start()) + 1
            for name in STRINGS.findall(match.group(1)):
                references.append((name, str(path.relative_to(root)), line))
        count += 1
    missing = sorted(set(x for x in references if x[0] not in providers))
    required = {'cuttlefish_buildhost_only', 'libwinpthread'}
    absent = sorted(required - providers)
    print(f'Source audit: {count} Android.bp files, {len(providers)} literal named modules, {len(references)} defaults references.')
    for name, path, line in missing[:80]:
        print(f'Absent defaults definition: {name}: {path}:{line}')
    if absent:
        print('Missing essential global definitions: ' + ', '.join(absent))
    if missing or absent:
        raise SystemExit('Source preflight failed. Review missing source definitions before retrying Soong.')
    print('Literal defaults preflight passed; full Soong validation is still required.')

if __name__ == '__main__':
    main()
