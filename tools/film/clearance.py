#!/usr/bin/env python3
"""Clearance of film camera flights against the game's visible exterior geometry (the source GLBs: OSM city, resort blocks,
landmarks, highrises, the south Strip, the Sphere), so a flight is checked before it is recorded.

  python3 tools/film/clearance.py <take> [<take> ...] [--min 4] [--hotel tower:floor:bay:side] [--extra glob ...]

For every world-anchored camera segment of each take (tools/film/takes/<take>.json) it samples the camera path every
0.5 m (the same uniform Catmull-Rom the film director plays), and reports the nearest triangle distance along it, with
every stretch closer than --min metres (default 4) and the mesh it comes from. Exits 1 when a take has such a stretch.
Triangles are cached per GLB in build/film/clearance-cache/ (npz).
"""
import glob, hashlib, json, math, os, struct, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES = ['build/geographic-strip/city.glb', 'build/resort-blocks/*/*-exterior.glb', 'build/strip-landmarks/*-exterior.glb',
           'build/highrises/*.glb', 'build/south-strip/*.glb', 'build/sphere/*exterior*.glb', 'build/geographic-strip/detailed.glb']
CACHE = os.path.join(ROOT, 'build/film/clearance-cache')
CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}

def node_matrix(n):
    if 'matrix' in n: return np.array(n['matrix'], dtype=np.float64).reshape(4, 4).T
    t = n.get('translation', [0, 0, 0]); x, y, z, w = n.get('rotation', [0, 0, 0, 1]); s = n.get('scale', [1, 1, 1])
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    M = np.eye(4); M[:3, :3] = R * np.array(s); M[:3, 3] = t; return M

def placement(path):
    """Where the game puts a GLB authored around its own origin (the Sphere: SphereVenue at sphere.json's centre)."""
    if os.sep + 'sphere' + os.sep in path: return np.array(json.load(open(os.path.join(ROOT, 'build/sphere/sphere.json')))['center'], np.float32)
    return None

def triangles(path):
    """World-space triangles (N, 3, 3) float32 and a material/node label per triangle."""
    os.makedirs(CACHE, exist_ok=True)
    st = os.stat(path); key = hashlib.sha1(f'{path}{st.st_size}{st.st_mtime}'.encode()).hexdigest()[:16]
    cf = os.path.join(CACHE, key + '.npz')
    if os.path.exists(cf): z = np.load(cf, allow_pickle=True); return z['tri'], z['lab'], list(z['names'])
    b = open(path, 'rb').read(); L = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + L])
    off = 20 + L; L2 = struct.unpack('<I', b[off:off + 4])[0]; bin_ = memoryview(b)[off + 8:off + 8 + L2]
    if 'EXT_meshopt_compression' in j.get('extensionsUsed', []): raise SystemExit(f'{path}: meshopt-compressed; use the original')
    def acc(i):
        a = j['accessors'][i]; v = j['bufferViews'][a['bufferView']]; dt = np.dtype(CT[a['componentType']]); n = NC[a['type']]
        start = v.get('byteOffset', 0) + a.get('byteOffset', 0); stride = v.get('byteStride', 0) or dt.itemsize * n
        raw = np.frombuffer(bin_, dtype=np.uint8, count=stride * (a['count'] - 1) + dt.itemsize * n, offset=start)
        out = np.lib.stride_tricks.as_strided(raw, shape=(a['count'], n * dt.itemsize), strides=(stride, 1)).copy().view(dt).reshape(a['count'], n)
        if a.get('normalized'): out = out.astype(np.float32) / np.iinfo(dt).max
        return out
    tris, labs, names = [], [], []
    def walk(i, parent):
        n = j['nodes'][i]; M = parent @ node_matrix(n)
        if 'mesh' in n:
            for p in j['meshes'][n['mesh']]['primitives']:
                if p.get('mode', 4) != 4: continue
                pos = acc(p['attributes']['POSITION']).astype(np.float64)
                pos = pos @ M[:3, :3].T + M[:3, 3]
                idx = acc(p['indices']).reshape(-1) if 'indices' in p else np.arange(len(pos))
                t = pos[idx.reshape(-1, 3)].astype(np.float32)
                mat = j['materials'][p['material']].get('name', '') if 'material' in p else ''
                names.append(f"{os.path.basename(path)}:{n.get('name', '')}:{mat}"); tris.append(t); labs.append(np.full(len(t), len(names) - 1, np.int32))
        for c in n.get('children', []): walk(c, M)
    for s in j['scenes']:
        for i in s['nodes']: walk(i, np.eye(4))
    tri = np.concatenate(tris) if tris else np.zeros((0, 3, 3), np.float32); lab = np.concatenate(labs) if labs else np.zeros(0, np.int32)
    np.savez(cf, tri=tri, lab=lab, names=np.array(names, dtype=object)); return tri, lab, names

def cr(keys, local):
    """The film director's camera curve (Film.cameraAt): uniform Catmull-Rom in key time, eased into the first and out of
    the last key."""
    i = 0
    while i < len(keys) - 2 and keys[i + 1]['t'] <= local: i += 1
    k0, k1, k2, k3 = keys[max(0, i - 1)], keys[i], keys[min(len(keys) - 1, i + 1)], keys[min(len(keys) - 1, i + 2)]
    span = max(1e-6, k2['t'] - k1['t']); u = 0 if len(keys) == 1 else min(1, max(0, (local - k1['t']) / span))
    e = u * u * (3 - 2 * u)
    x = e * .5 + u * .5 if (i == 0 and len(keys) > 2) or (i == len(keys) - 2 and len(keys) > 2) else e if len(keys) == 2 else u
    f = lambda a, b, c, d: .5 * ((2 * b) + (-a + c) * x + (2 * a - 5 * b + 4 * c - d) * x * x + (-a + 3 * b - 3 * c + d) * x ** 3)
    return np.array([f(k0['pos'][q], k1['pos'][q], k2['pos'][q], k3['pos'][q]) for q in range(3)])

def point_tri_dist(p, T):
    """Distances from point p (3,) to triangles T (N,3,3) (closest-point on triangle, Ericson)."""
    a, b, c = T[:, 0].astype(np.float64), T[:, 1].astype(np.float64), T[:, 2].astype(np.float64)
    ab, ac, ap = b - a, c - a, p - a
    d1, d2 = (ab * ap).sum(1), (ac * ap).sum(1)
    bp = p - b; d3, d4 = (ab * bp).sum(1), (ac * bp).sum(1)
    cp = p - c; d5, d6 = (ab * cp).sum(1), (ac * cp).sum(1)
    va, vb, vc = d3 * d6 - d5 * d4, d5 * d2 - d1 * d6, d1 * d4 - d3 * d2
    denom = va + vb + vc; denom = np.where(np.abs(denom) < 1e-12, 1e-12, denom)
    v, w = vb / denom, vc / denom
    q = a + ab * v[:, None] + ac * w[:, None]                                   # interior
    def seg(s, e):
        d = e - s; t = np.clip(((p - s) * d).sum(1) / np.maximum((d * d).sum(1), 1e-12), 0, 1); return s + d * t[:, None]
    inside = (va >= 0) & (vb >= 0) & (vc >= 0)
    cands = np.stack([seg(a, b), seg(b, c), seg(c, a)])
    dd = np.linalg.norm(cands - p, axis=2).min(0)
    return np.where(inside, np.linalg.norm(q - p, axis=1), dd)

def hotel_triangles(spec):
    """--hotel <tower>:<floor>:<bay>:<side>: the streamed interior a camera run passes (lobby, entry, the stair storeys up to
    the floor, that floor's corridor and end cap, the one room), placed like HotelStreaming (HotelGeometry.moduleMatrix).
    Doors are left out: the run opens them."""
    tid, floor, bay, side = spec.split(':'); floor, bay, side = int(floor), int(bay), int(side)
    towers = {t['id']: t for f in ('towers', 'highrise-towers', 'landmark-towers') for t in json.load(open(os.path.join(ROOT, f'src/work/hotels/{f}.json')))}
    t = towers[tid]; STORY, BAY, FIRST, DOOR_X = 3.6, 6, -8.1, 1.85
    def matrix(p, rot=0):
        M = np.eye(4)
        if t.get('linear'): a, b, c, d = t['linear']; M[:3, :3] = [[a, 0, b], [0, 1, 0], [c, 0, d]]
        else: cy, sy = math.cos(t['yaw']), math.sin(t['yaw']); M[:3, :3] = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
        o = t['origin']; x, y, z = p
        if t.get('linear'): a, b, c, d = t['linear']; w = [o[0] + a * x + b * z, o[1] + y, o[2] + c * x + d * z]
        else: cy, sy = math.cos(t['yaw']), math.sin(t['yaw']); w = [o[0] + cy * x + sy * z, o[1] + y, o[2] - sy * x + cy * z]
        M[:3, 3] = w
        R = np.eye(4); c_, s_ = math.cos(rot), math.sin(rot); R[:3, :3] = [[c_, 0, s_], [0, 1, 0], [-s_, 0, c_]]
        return M @ R
    parts = [(f"build/hotels/{tid}-lobby.glb", (0, 0, 0), 0), (f"build/hotels/{t['set']}-entry.glb", (0, 0, 0), 0)]
    parts += [(f"build/hotels/{t['set']}-stair.glb", (0, f * STORY, 0), 0) for f in range(0, floor + 1)]
    parts += [(f"build/hotels/{t['set']}-corridor.glb", (0, floor * STORY, FIRST - b * BAY), 0) for b in range(t['bays'])]
    parts += [(f"build/hotels/{t['set']}-cap.glb", (0, floor * STORY, FIRST - (t['bays'] - 1) * BAY - 3.15 + 2.42), 0)]
    parts += [(f"build/hotels/{t['set']}-room.glb", (side * DOOR_X, floor * STORY, FIRST - bay * BAY), 0 if side > 0 else math.pi)]
    T, L, N = [], [], []
    for f, p, rot in parts:
        path = os.path.join(ROOT, f)
        if not os.path.exists(path): print('  (missing', f, ')'); continue
        tri, lab, names = triangles(path); M = matrix(p, rot)
        flat = tri.reshape(-1, 3).astype(np.float64); flat = flat @ M[:3, :3].T + M[:3, 3]
        T.append(flat.reshape(-1, 3, 3).astype(np.float32)); L.append(lab + len(N)); N += names
    return np.concatenate(T), np.concatenate(L), N

def keys_path(keys):
    """Samples of the director's curve every 1/120 s (walking the keys once), thinned to one per 0.5 m."""
    dur = keys[-1]['t']; pts, times, i, tt = [], [], 0, 0.0
    while tt <= dur:
        while i < len(keys) - 2 and keys[i + 1]['t'] <= tt: i += 1
        pts.append(_cr_at(keys, i, tt)); times.append(tt); tt += 1 / 120
    P = np.array(pts); seglen = np.linalg.norm(np.diff(P, axis=0), axis=1)
    keep = np.concatenate([[True], np.cumsum(seglen) // 0.5 != np.concatenate([[0], np.cumsum(seglen)[:-1]]) // 0.5])
    return P[keep], np.array(times)[keep]

def _cr_at(keys, i, local):
    k0, k1, k2, k3 = keys[max(0, i - 1)], keys[i], keys[min(len(keys) - 1, i + 1)], keys[min(len(keys) - 1, i + 2)]
    span = max(1e-6, k2['t'] - k1['t']); u = 0 if len(keys) == 1 else min(1, max(0, (local - k1['t']) / span))
    e = u * u * (3 - 2 * u)
    x = e * .5 + u * .5 if (i == 0 and len(keys) > 2) or (i == len(keys) - 2 and len(keys) > 2) else e if len(keys) == 2 else u
    f = lambda a, b, c, d: .5 * ((2 * b) + (-a + c) * x + (2 * a - 5 * b + 4 * c - d) * x * x + (-a + 3 * b - 3 * c + d) * x ** 3)
    return [f(k0['pos'][q], k1['pos'][q], k2['pos'][q], k3['pos'][q]) for q in range(3)]

class Grid:
    """Triangles bucketed by the 24 m (x, z) cells their bounds cover (huge ones, e.g. ground planes, kept apart)."""
    C = 24.0
    def __init__(self, T):
        self.T = T; self.tmin, self.tmax = T.min(1), T.max(1)
        ix0, ix1 = np.floor(self.tmin[:, 0] / self.C).astype(np.int64), np.floor(self.tmax[:, 0] / self.C).astype(np.int64)
        iz0, iz1 = np.floor(self.tmin[:, 2] / self.C).astype(np.int64), np.floor(self.tmax[:, 2] / self.C).astype(np.int64)
        small = (ix1 - ix0 < 8) & (iz1 - iz0 < 8); self.huge = np.nonzero(~small)[0]
        keys, ids = [], []
        for dx in range(8):
            for dz in range(8):
                m = small & (ix0 + dx <= ix1) & (iz0 + dz <= iz1)
                if m.any(): keys.append((ix0[m] + dx) * 1_000_003 + (iz0[m] + dz)); ids.append(np.nonzero(m)[0])
        keys, ids = np.concatenate(keys), np.concatenate(ids); o = np.argsort(keys, kind='stable')
        self.keys, self.ids = keys[o], ids[o]
    def near(self, p, r=30.0):
        out = [self.huge]
        for ix in range(int(np.floor((p[0] - r) / self.C)), int(np.floor((p[0] + r) / self.C)) + 1):
            for iz in range(int(np.floor((p[2] - r) / self.C)), int(np.floor((p[2] + r) / self.C)) + 1):
                k = ix * 1_000_003 + iz; a, b = np.searchsorted(self.keys, [k, k + 1]); out.append(self.ids[a:b])
        c = np.unique(np.concatenate(out))
        m = np.all(self.tmax[c] >= p - r, 1) & np.all(self.tmin[c] <= p + r, 1)
        return c[m]

def main():
    args = sys.argv[1:]; mind = float(args[args.index('--min') + 1]) if '--min' in args else 4.0
    hotel = args[args.index('--hotel') + 1] if '--hotel' in args else None
    extra = [args[i + 1] for i, a in enumerate(args) if a == '--extra']   # more GLBs (globs), e.g. a landmark interior
    takes = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] not in ('--min', '--hotel', '--extra'))]
    files = sorted({f for s in SOURCES + extra for f in glob.glob(os.path.join(ROOT, s))})
    paths = []
    for t in takes:
        take = json.load(open(os.path.join(ROOT, 'tools/film/takes', t + '.json')))
        for si, seg in enumerate(take.get('camera', [])):
            if seg.get('anchor', 'world') != 'world': continue
            P, times = keys_path(seg['keys']); paths.append((t, si, P, times + seg.get('from', 0)))
    if not paths: sys.exit('no world-anchored camera segments')
    lo = np.min([p[2].min(0) for p in paths], 0) - 40; hi = np.max([p[2].max(0) for p in paths], 0) + 40
    T, labels, names = [], [], []
    for f in files:
        tri, lab, nm = triangles(f)
        if not len(tri): continue
        off = placement(f)
        if off is not None: tri = tri + off
        tmin, tmax = tri.min(1), tri.max(1)
        m = np.all(tmax >= lo, 1) & np.all(tmin <= hi, 1)
        if m.any(): T.append(tri[m]); labels.append(lab[m] + len(names)); names += nm
    if hotel:
        ht, hl, hn = hotel_triangles(hotel); T.append(ht); labels.append(hl + len(names)); names += hn
    T = np.concatenate(T); labels = np.concatenate(labels); grid = Grid(T)
    bad_any = False
    for take, si, P, times in paths:
        dists, near = np.full(len(P), 1e9), np.full(len(P), -1)
        for k, p in enumerate(P):
            c = grid.near(p)
            if not len(c): continue
            d = point_tri_dist(p, T[c]); a = int(d.argmin()); dists[k] = d[a]; near[k] = labels[c][a]
        print(f'{take} camera {si}: {len(P)} samples, min clearance {dists.min():.1f} m at t {times[dists.argmin()]:.1f} s {np.round(P[dists.argmin()], 1).tolist()}'
              f' ({names[near[dists.argmin()]] if near[dists.argmin()] >= 0 else "-"})')
        close = dists < mind; i = 0
        while i < len(P):
            if close[i]:
                j = i
                while j + 1 < len(P) and close[j + 1]: j += 1
                k = i + int(dists[i:j + 1].argmin())
                print(f'   < {mind:g} m: t {times[i]:.1f}-{times[j]:.1f} s, nearest {dists[k]:.1f} m at {np.round(P[k], 1).tolist()} {names[near[k]]}')
                bad_any = True; i = j + 1
            else: i += 1
    sys.exit(1 if bad_any else 0)

if __name__ == '__main__':
    main()
