#!/usr/bin/env python3
"""How optimized is what the game ships? Reads the glTF JSON chunk of every GLB in the runtime asset list
(tools/release/asset-pack.json, the bytes the pack carries) and of the committed GLBs under src/ and public/, and counts:
buffer compression (EXT_meshopt_compression), quantization (KHR_mesh_quantization), texture formats and bytes
(PNG/JPEG/WebP/KTX2), index widths (uint32 indices that would fit 16 bits), normal and position encodings.
Also lists the biggest JSON data files, which ship as plain text.

python3 tools/optimize/audit-pack.py            # summary
python3 tools/optimize/audit-pack.py --json     # also .bitmagic/optimize/pack-audit.json, per file"""
import collections
import json
import os
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CT = {5120: 'int8', 5121: 'uint8', 5122: 'int16', 5123: 'uint16', 5125: 'uint32', 5126: 'float'}


def glb_json(path):
    with open(path, 'rb') as f:
        magic, _, _ = struct.unpack('<4sII', f.read(12))
        if magic != b'glTF':
            return None
        n, kind = struct.unpack('<I4s', f.read(8))
        return json.loads(f.read(n)) if kind == b'JSON' else None


def inspect(path):
    g = glb_json(path)
    if g is None:
        return None
    ext = set(g.get('extensionsUsed', []))
    acc = g.get('accessors', [])
    views = g.get('bufferViews', [])
    r = {'bytes': os.path.getsize(path), 'meshopt': 'EXT_meshopt_compression' in ext, 'quantized': 'KHR_mesh_quantization' in ext,
         'images': collections.Counter(), 'imageBytes': collections.Counter(), 'idx16': 0, 'idx32': 0, 'idx32fits16': 0,
         'idx32fitsBytes': 0, 'normals': collections.Counter(), 'positions': collections.Counter(), 'prims': 0}
    for im in g.get('images', []):
        mime = im.get('mimeType') or ('uri' if 'uri' in im else '?')
        r['images'][mime] += 1
        bv = im.get('bufferView')
        if bv is not None and bv < len(views):
            r['imageBytes'][mime] += views[bv].get('byteLength', 0)
    for m in g.get('meshes', []):
        for p in m.get('primitives', []):
            r['prims'] += 1
            a = p.get('attributes', {})
            verts = acc[a['POSITION']]['count'] if 'POSITION' in a else 0
            if 'POSITION' in a:
                r['positions'][CT.get(acc[a['POSITION']]['componentType'])] += 1
            if 'NORMAL' in a:
                r['normals'][CT.get(acc[a['NORMAL']]['componentType'])] += 1
            if 'indices' in p:
                ia = acc[p['indices']]
                if ia['componentType'] == 5125:
                    r['idx32'] += 1
                    if verts <= 65535:
                        r['idx32fits16'] += 1
                        r['idx32fitsBytes'] += ia['count'] * 2   # raw bytes saved before meshopt
                elif ia['componentType'] == 5123:
                    r['idx16'] += 1
    return r


def main():
    pack = json.load(open(ROOT / 'tools/release/asset-pack.json'))
    manifest = json.load(open(ROOT / 'build/optimized/manifest.json'))['files'] if (ROOT / 'build/optimized/manifest.json').exists() else {}
    files = []
    for f in pack['files']:
        if not f['path'].endswith('.glb'):
            continue
        e = manifest.get(f['path'])
        src = ROOT / e['optimized'] if f['kind'] == 'optimized' and e else ROOT / f['path']
        files.append(('pack', f['path'], src))
    for base in ('src', 'public'):
        for p in sorted((ROOT / base).rglob('*.glb')):
            files.append(('repo', str(p.relative_to(ROOT)), p))
    rows, tot = [], collections.Counter()
    imgs, imgb, norms, poss = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    for where, rel, src in files:
        r = inspect(src)
        if r is None:
            continue
        r.update(path=rel, where=where)
        rows.append(r)
        tot['files'] += 1; tot['bytes'] += r['bytes']
        tot['meshopt'] += r['meshopt']; tot['meshoptBytes'] += r['bytes'] if r['meshopt'] else 0
        tot['quantized'] += r['quantized']
        for k in ('idx16', 'idx32', 'idx32fits16', 'idx32fitsBytes', 'prims'):
            tot[k] += r[k]
        imgs.update(r['images']); imgb.update(r['imageBytes']); norms.update(r['normals']); poss.update(r['positions'])
    MiB = lambda b: f'{b / 1048576:.1f} MiB'
    print(f"{tot['files']} GLBs, {MiB(tot['bytes'])}")
    print(f"  meshopt buffers: {tot['meshopt']} files ({MiB(tot['meshoptBytes'])}); without: {tot['files'] - tot['meshopt']}")
    for r in sorted((r for r in rows if not r['meshopt']), key=lambda r: -r['bytes'])[:12]:
        print(f"      no meshopt: {MiB(r['bytes']):>10}  {r['path']} ({r['where']})")
    print(f"  quantized (KHR_mesh_quantization): {tot['quantized']} files")
    print(f"  positions: {dict(poss)}   normals: {dict(norms)}")
    print(f"  indices: {tot['idx16']} uint16, {tot['idx32']} uint32 of which {tot['idx32fits16']} would fit uint16 "
          f"(~{MiB(tot['idx32fitsBytes'])} raw)")
    print(f"  images: {dict(imgs)}")
    print(f"  image bytes: " + ', '.join(f'{k} {MiB(v)}' for k, v in imgb.most_common()))
    big_png = sorted(((r['imageBytes'].get('image/png', 0), r['path']) for r in rows), reverse=True)[:8]
    for b, p in big_png:
        if b:
            print(f"      PNG {MiB(b):>10}  {p}")
    js = sorted(((f['bytes'], f['path']) for f in pack['files'] if f['path'].endswith('.json')), reverse=True)
    print(f"JSON data: {len(js)} files, {MiB(sum(b for b, _ in js))} as plain text; largest:")
    for b, p in js[:6]:
        print(f"      {MiB(b):>10}  {p}")
    if '--json' in sys.argv:
        out = ROOT / '.bitmagic/optimize/pack-audit.json'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rows, indent=1, default=dict))
        print('->', out.relative_to(ROOT))


if __name__ == '__main__':
    main()
