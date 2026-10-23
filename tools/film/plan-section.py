#!/usr/bin/env python3
"""Side section of the game's geometry for laying out film camera paths: python3 tools/film/plan-section.py <out.png>
<axis x|z> <at> <half-width> <u0> <u1> <y0> <y1> [--px 0.1] [--glb glob ...] [--path take]

Draws triangles that cross the slab |axis - at| < half-width, projected on (the other horizontal axis, height), with a 1 m
grid (labels every 5 m) and, with --path, the take's world camera path inside the slab (red)."""
import glob, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
import importlib.util
spec = importlib.util.spec_from_file_location('clearance', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clearance.py'))
cl = importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)
a = sys.argv[1:]
out, axis, at, hw, u0, u1, y0, y1 = a[0], a[1], *map(float, a[2:8])
px = float(a[a.index('--px') + 1]) if '--px' in a else 0.1
extra = [a[i + 1] for i, v in enumerate(a) if v == '--glb']
take = a[a.index('--path') + 1] if '--path' in a else None
ax, ou = (0, 2) if axis == 'x' else (2, 0)
W, H = int((u1 - u0) / px), int((y1 - y0) / px)
img = Image.new('RGB', (W, H), (18, 18, 22)); dr = ImageDraw.Draw(img)
X = lambda u: (u - u0) / px; Y = lambda y: H - (y - y0) / px
for g in range(int(math.ceil(u0)), int(u1) + 1):
    dr.line([(X(g), 0), (X(g), H)], fill=(34, 34, 42) if g % 5 else (60, 60, 78))
    if g % 5 == 0: dr.text((X(g) + 2, 2), str(g), fill=(150, 150, 170))
for g in range(int(math.ceil(y0)), int(y1) + 1):
    dr.line([(0, Y(g)), (W, Y(g))], fill=(34, 34, 42) if g % 5 else (60, 60, 78))
    if g % 5 == 0: dr.text((2, Y(g) + 2), str(g), fill=(150, 150, 170))
files = sorted({f for s in cl.SOURCES + extra for f in glob.glob(os.path.join(cl.ROOT, s))})
legend = {}
for f in files:
    tri, lab, names = cl.triangles(f)
    if not len(tri): continue
    off = cl.placement(f)
    if off is not None: tri = tri + off
    lo, hi = tri.min(1), tri.max(1)
    m = (hi[:, ax] >= at - hw) & (lo[:, ax] <= at + hw) & (hi[:, ou] >= u0) & (lo[:, ou] <= u1) & (hi[:, 1] >= y0) & (lo[:, 1] <= y1)
    for t, l in zip(tri[m], lab[m]):
        nm = names[l].split(':')[-1]; h = abs(hash(nm)); col = (80 + h % 160, 80 + (h // 160) % 160, 80 + (h // 25600) % 160)
        legend[nm] = col; dr.polygon([(X(p[ou]), Y(p[1])) for p in t], outline=col)
if take:
    tk = json.load(open(os.path.join(cl.ROOT, 'tools/film/takes', take + '.json')))
    for seg in tk.get('camera', []):
        if seg.get('anchor', 'world') != 'world': continue
        pts = [(X(k['pos'][ou]), Y(k['pos'][1])) for k in seg['keys'] if abs(k['pos'][ax] - at) < hw + 2]
        if len(pts) > 1: dr.line(pts, fill=(255, 60, 60), width=2)
y = 14
for nm, col in sorted(legend.items())[:40]: dr.text((W - 220, y), nm[:34], fill=col); y += 12
img.save(out); print(out, W, H, len(legend), 'meshes')
