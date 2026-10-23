#!/usr/bin/env python3
"""World-space bounds of a GLB's meshes grouped by material (or node name with --nodes), from accessor min/max and node
transforms: python3 tools/film/glb-bounds.py <file.glb> [regex] [--nodes]. For laying out film camera flights."""
import json, re, struct, sys
import numpy as np
path = sys.argv[1]; pat = re.compile(sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else '.', re.I)
by_node = '--nodes' in sys.argv
b = open(path, 'rb').read(); L = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + L])
def mat(n):
    if 'matrix' in n: return np.array(n['matrix']).reshape(4, 4).T
    t = n.get('translation', [0, 0, 0]); r = n.get('rotation', [0, 0, 0, 1]); s = n.get('scale', [1, 1, 1])
    x, y, z, w = r
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    M = np.eye(4); M[:3, :3] = R * np.array(s); M[:3, 3] = t; return M
groups = {}
def walk(i, parent):
    n = j['nodes'][i]; M = parent @ mat(n)
    if 'mesh' in n:
        for p in j['meshes'][n['mesh']]['primitives']:
            a = j['accessors'][p['attributes']['POSITION']]
            if 'min' not in a: continue
            key = n.get('name', '') if by_node else j['materials'][p['material']].get('name', '') if 'material' in p else '(none)'
            if not pat.search(key): continue
            lo, hi = np.array(a['min']), np.array(a['max'])
            corners = np.array([[x, y, z, 1] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) @ M.T
            g = groups.setdefault(key, [np.full(3, 1e9), np.full(3, -1e9), 0])
            g[0] = np.minimum(g[0], corners[:, :3].min(0)); g[1] = np.maximum(g[1], corners[:, :3].max(0)); g[2] += 1
    for c in n.get('children', []): walk(c, M)
for s in j['scenes']:
    for i in s['nodes']: walk(i, np.eye(4))
for k, (lo, hi, c) in sorted(groups.items()):
    print(f'{k[:48]:48s} n={c:4d}  x {lo[0]:8.1f}..{hi[0]:8.1f}  y {lo[1]:6.1f}..{hi[1]:6.1f}  z {lo[2]:8.1f}..{hi[2]:8.1f}  centre ({(lo[0]+hi[0])/2:.1f}, {(lo[2]+hi[2])/2:.1f})')
