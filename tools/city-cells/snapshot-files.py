"""Snapshot authored/runtime cell bytes for no-op checks; generated evidence stays outside Git."""
import hashlib
import json
import sys
from pathlib import Path
roots = ['build/geographic-strip/cells', 'build/optimized/build/geographic-strip/cells',
         'build/geographic-strip/collision-cells', 'build/baked/cells']
files = {}
for root in roots:
    for p in sorted(Path(root).glob('*')):
        if p.suffix not in ('.glb', '.bin', '.json'):
            continue
        files[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
if len(sys.argv) > 1:
    expected = json.loads(Path(sys.argv[1]).read_text())
    changed = sorted(k for k in files.keys() | expected.keys() if files.get(k) != expected.get(k))
    if changed:
        raise SystemExit('Changed cell files:\n' + '\n'.join(changed))
    print(f'PASS: {len(files)} cell source/runtime files and manifests are byte-identical')
else:
    print(json.dumps(files, indent=2, sort_keys=True))
