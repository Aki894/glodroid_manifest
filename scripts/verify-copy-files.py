#!/usr/bin/env python3
"""Verify resolved PRODUCT_COPY_FILES sources without editing AOSP sources."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
entries = Path(sys.argv[2]).read_text().split()
missing = []
for entry in entries:
    source = entry.split(':', 1)[0]
    if not (root / source).is_file():
        missing.append(source)
for source in sorted(set(missing)):
    print(f'Missing PRODUCT_COPY_FILES source: {source}')
if missing:
    raise SystemExit('Copy-file preflight failed; do not remove missing files from the product to bypass it.')
print(f'Copy-file preflight passed ({len(entries)} entries).')
