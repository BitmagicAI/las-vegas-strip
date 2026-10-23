#!/usr/bin/env python3
"""Coplanar overlapping triangles (z-fighting) among a hotel's streamed modules as HotelStreaming places them:
python3 tools/film/zfight.py <tower>:<floor>:<bay>:<side> [--box x0,y0,z0,x1,y1,z1] [--tol 0.004]
Reports pairs of triangles from different meshes whose planes coincide (within --tol metres) facing the same way (--both:
either way) and whose areas overlap: the surfaces that flicker on screen."""
import os, sys, numpy as np, importlib.util
spec = importlib.util.spec_from_file_location('clearance', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clearance.py'))
cl = importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)
a = sys.argv[1:]; tol = float(a[a.index('--tol') + 1]) if '--tol' in a else 0.004; both = '--both' in a
T, L, N = cl.hotel_triangles(a[0])
if '--box' in a:
    b = np.array(list(map(float, a[a.index('--box') + 1].split(','))))
    lo, hi = T.min(1), T.max(1); m = np.all(hi >= b[:3], 1) & np.all(lo <= b[3:], 1); T, L = T[m], L[m]
T = T.astype(np.float64)
n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); area = np.linalg.norm(n, axis=1); ok = area > 1e-6
T, L, n, area = T[ok], L[ok], n[ok] / area[ok, None], area[ok] / 2
d = (n * T[:, 0]).sum(1)
# canonical plane: flip so the largest normal component is positive
sgn = np.sign(n[np.arange(len(n)), np.abs(n).argmax(1)]); nc = n * sgn[:, None]; dc = d * sgn
key = np.round(nc * 200).astype(np.int64); keyd = np.round(dc / (tol * 2)).astype(np.int64)
groups = {}
for i, (k, kd) in enumerate(zip(map(tuple, key), keyd)):
    for dd in (kd - 1, kd, kd + 1): groups.setdefault((k, dd), []).append(i)
def overlap(i, j):
    # project both triangles to the plane's dominant axes and test 2D overlap (separating axis)
    ax = np.argsort(np.abs(nc[i]))[:2]; A, B = T[i][:, ax], T[j][:, ax]
    for P in (A, B):
        for e in range(3):
            v = P[(e + 1) % 3] - P[e]; perp = np.array([-v[1], v[0]])
            pa, pb = A @ perp, B @ perp
            if pa.max() <= pb.min() + 1e-4 or pb.max() <= pa.min() + 1e-4: return False
    return True
seen, found = set(), {}
for (k, kd), idx in groups.items():
    if len(idx) < 2: continue
    idx = np.array(sorted(set(idx)))
    for ii in range(len(idx)):
        i = idx[ii]
        for j in idx[ii + 1:]:
            if L[i] == L[j] or (i, j) in seen: continue
            seen.add((i, j))
            if abs(dc[i] - dc[j]) > tol or np.abs(nc[i] - nc[j]).max() > 0.01: continue
            if not both and (n[i] * n[j]).sum() < 0: continue      # back to back: neither shows through the other
            if overlap(i, j):
                pair = tuple(sorted((N[L[i]], N[L[j]]))); c = T[i].mean(0)
                f = found.setdefault(pair, [0, c, 0.0]); f[0] += 1; f[2] += min(area[i], area[j])
for (p, q), (cnt, c, ar) in sorted(found.items(), key=lambda kv: -kv[1][2]):
    print(f'{cnt:4d} pairs  ~{ar:6.2f} m2  at {np.round(c, 2).tolist()}  {p}  <->  {q}')
if not found: print('no coplanar overlaps')
