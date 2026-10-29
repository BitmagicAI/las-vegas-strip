#!/usr/bin/env python3
"""Refuses runtime models that are not optimized the way the city ships them. The owner's rule (2026-10-29): every
submission runs the optimizing-assets skill (tools/optimize/), so no model lands now and needs optimizing later.

  python3 tools/optimize/check-runtime-glbs.py                    # every GLB in runtime-assets/ and public/
  python3 tools/optimize/check-runtime-glbs.py --changed origin/main   # only GLBs that differ from that ref

`python3 tools/release/asset-pack.py check` runs the same rules on the files it would ship, and `stage` refuses to
mirror a set that breaks them. A runtime GLB passes when:

1. it is meshopt-compressed (EXT_meshopt_compression). Files under 16 KiB are exempt: the encoder keeps those
   ("the output is not smaller than the input").
2. its colour and emissive maps are not PNG, unless the WebP pass ran and kept one (the file then declares
   EXT_texture_webp, or the optimizer installed its webp-textures copy). Normal and ORM maps may stay lossless.
3. in a full checkout (build/optimized/manifest.json): asset-pack ships the installed optimized copy, not an original
   whose source changed after it was optimized. (A clone has no optimizer manifest; rules 1 and 2 still read the bytes.)
4. a GLB served from public/ (the garden foliage) is the copy tools/optimize/foliage-trees.mjs made from its current
   source in tools/foliage/models/ (tools/optimize/foliage-trees.json records both). Fix: node tools/optimize/foliage-trees.mjs

The fix for every failure is the same pipeline, run on the model's runtime path (build/...):
  node tools/optimize/optimize-runtime-glbs.mjs --list
  node tools/optimize/optimize-runtime-glbs.mjs --only=<name>
  node tools/optimize/optimize-runtime-glbs.mjs --variant=webp-textures --only=<name>
  node tools/optimize/install-optimized.mjs --only=<name>
  python3 tools/release/asset-pack.py stage
"""
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SMALL = 16 * 1024
FIX = 'optimize it: python3 tools/optimize/check-runtime-glbs.py --help'
# Checked and kept as they are, with the reason. Add an entry only with a measured reason.
KEPT = {
    'build/hotels/bellagio-corridor-end.glb': 'the WebP pass ran and its output equals the level copy: WebP was not '
                                              'smaller for its one 30 KB colour map',
}


def glb_json(path):
    with open(path, 'rb') as f:
        head = f.read(20)
        if head[:4] != b'glTF':
            return None
        return json.loads(f.read(struct.unpack('<I', head[12:16])[0]))


def colour_maps(doc):
    """MIME types of the images behind base-colour and emissive textures (a WebP source wins over its fallback)."""
    used = set()
    for m in doc.get('materials', []):
        for t in (m.get('pbrMetallicRoughness', {}).get('baseColorTexture'), m.get('emissiveTexture')):
            if t is not None:
                used.add(t['index'])
    out = []
    for i in sorted(used):
        t = doc['textures'][i]
        src = t.get('extensions', {}).get('EXT_texture_webp', {}).get('source', t.get('source'))
        if src is not None:
            out.append(doc['images'][src].get('mimeType', 'uri'))
    return out


def problems(runtime, data_path, entry=None, kind=None):
    """What is wrong with one runtime GLB. runtime: its path under build/; data_path: the bytes that ship; entry: its
    optimizer manifest entry in a full checkout; kind: asset-pack's label for those bytes ('optimized', 'original',
    ...), None when unknown."""
    data_path = Path(data_path)
    if '/characters/' in runtime or runtime in KEPT:  # characters load from their registered remote URLs
        return []
    doc = glb_json(data_path)
    if doc is None:
        return ['not a binary glTF']
    small = data_path.stat().st_size < SMALL
    used = set(doc.get('extensionsUsed', []))
    out = []
    if kind and kind.startswith('original') and not small:
        out.append(f'ships the {kind}, not its optimized copy')
    if not small and 'EXT_meshopt_compression' not in used:
        out.append('not meshopt-compressed')
    png = colour_maps(doc).count('image/png')
    if png and 'EXT_texture_webp' not in used and not (entry and entry.get('variant') == 'webp-textures'):
        out.append(f'{png} PNG colour map{"s" if png > 1 else ""}: the WebP pass did not run')
    return out


def optimizer_manifest():
    p = ROOT / 'build/optimized/manifest.json'
    return json.loads(p.read_text())['files'] if p.exists() else {}


def tracked_glbs(changed_from=None):
    cmd = ['git', 'diff', '--name-only', '--diff-filter=AM', changed_from, '--'] if changed_from else ['git', 'ls-files']
    files = subprocess.run(cmd + ['runtime-assets', 'public'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    if changed_from:  # a foliage source changed without its public/ copy
        sources = subprocess.run(cmd + ['tools/foliage/models'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        files += [f'public/foliage/{Path(f).name}' for f in sources if f.endswith('.glb') and f'public/foliage/{Path(f).name}' not in files]
    return [f for f in files if f.endswith('.glb')]


def foliage_problems(path, record):
    """Rule 4 for a GLB served from public/: made by foliage-trees.mjs from the source now in the repository."""
    import hashlib
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    entry = record.get(path)
    if not entry:
        return ['not made by tools/optimize/foliage-trees.mjs (no entry in tools/optimize/foliage-trees.json)']
    out = []
    if sha(ROOT / path) != entry['sha256']:
        out.append('differs from the copy tools/optimize/foliage-trees.mjs made')
    if not (ROOT / entry['source']).exists() or sha(ROOT / entry['source']) != entry['sourceSha256']:
        out.append(f'its source {entry["source"]} changed after the copy was made: node tools/optimize/foliage-trees.mjs')
    return out


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        return 0
    ref = sys.argv[sys.argv.index('--changed') + 1] if '--changed' in sys.argv else None
    manifest = optimizer_manifest()
    record_path = ROOT / 'tools/optimize/foliage-trees.json'
    record = json.loads(record_path.read_text())['files'] if record_path.exists() else {}
    bad = 0
    files = tracked_glbs(ref)
    for f in files:
        if f.startswith('public/'):
            found = problems(f, ROOT / f) + foliage_problems(f, record)
        else:
            runtime = 'build/' + f[len('runtime-assets/'):]
            found = problems(runtime, ROOT / f, manifest.get(runtime))
        if found:
            bad += 1
            print(f'{f}: ' + '; '.join(found))
    print(f'{len(files)} runtime GLBs checked, {bad} not optimized' + (f' ({FIX})' if bad else ''))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
