#!/usr/bin/env python3
"""Top-down slice of the game's geometry for laying out film camera paths through buildings:
python3 tools/film/plan-slice.py <out.png> <x0> <z0> <x1> <z1> <y0> <y1> [--px 0.25] [--glb glob ...] [--path take]

Draws every triangle that crosses the height band y0..y1 (walls, columns, rails at camera height) in its footprint, coloured
by its mesh, with a 10 m grid (labels every 50 m) and, with --path, the take's world camera path (red, white dots each second).
Sources: the clearance tool's exterior GLBs plus any --glb (e.g. a landmark interior)."""
import glob, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location('clearance', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clearance.py'))
cl = importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)
a = sys.argv[1:]
out = a[0]; x0, z0, x1, z1, y0, y1 = map(float, a[1:7])
px = float(a[a.index('--px') + 1]) if '--px' in a else 0.25
extra = [a[i + 1] for i, v in enumerate(a) if v == '--glb']
take = a[a.index('--path') + 1] if '--path' in a else None
W, H = int((x1 - x0) / px), int((z1 - z0) / px)
img = Image.new('RGB', (W, H), (18, 18, 22)); dr = ImageDraw.Draw(img)
for gx in range(int(math.ceil(x0 / 10)) * 10, int(x1) + 1, 10):
    X = (gx - x0) / px; dr.line([(X, 0), (X, H)], fill=(40, 40, 50) if gx % 50 else (70, 70, 90))
    if gx % 50 == 0: dr.text((X + 2, 2), str(gx), fill=(150, 150, 170))
for gz in range(int(math.ceil(z0 / 10)) * 10, int(z1) + 1, 10):
    Z = (gz - z0) / px; dr.line([(0, Z), (W, Z)], fill=(40, 40, 50) if gz % 50 else (70, 70, 90))
    if gz % 50 == 0: dr.text((2, Z + 2), str(gz), fill=(150, 150, 170))
files = sorted({f for s in cl.SOURCES + extra for f in glob.glob(os.path.join(cl.ROOT, s))})
legend = {}
for f in files:
    tri, lab, names = cl.triangles(f)
    if not len(tri): continue
    off = cl.placement(f)
    if off is not None: tri = tri + off
    lo, hi = tri.min(1), tri.max(1)
    m = (hi[:, 0] >= x0) & (lo[:, 0] <= x1) & (hi[:, 2] >= z0) & (lo[:, 2] <= z1) & (hi[:, 1] >= y0) & (lo[:, 1] <= y1)
    for t, l in zip(tri[m], lab[m]):
        nm = names[l]; h = abs(hash(nm.split(':')[-1])) ; col = (80 + h % 160, 80 + (h // 160) % 160, 80 + (h // 25600) % 160)
        legend[nm.split(':')[-1]] = col
        dr.polygon([((p[0] - x0) / px, (p[2] - z0) / px) for p in t], outline=col)
if take:
    tk = json.load(open(os.path.join(cl.ROOT, 'tools/film/takes', take + '.json')))
    for seg in tk.get('camera', []):
        if seg.get('anchor', 'world') != 'world': continue
        k = seg['keys']; pts = [((q['pos'][0] - x0) / px, (q['pos'][2] - z0) / px) for q in k]
        dr.line(pts, fill=(255, 60, 60), width=2)
        for q in k:
            if abs(q['t'] - round(q['t'])) < 1e-3: P = ((q['pos'][0] - x0) / px, (q['pos'][2] - z0) / px); dr.ellipse([P[0] - 3, P[1] - 3, P[0] + 3, P[1] + 3], fill=(255, 255, 255)); dr.text((P[0] + 4, P[1] - 4), f"{seg['from'] + q['t']:.0f}|{q['pos'][1]:.0f}", fill=(255, 220, 220))
y = 14
for nm, col in sorted(legend.items())[:40]: dr.text((W - 260, y), nm[:40], fill=col); y += 12
img.save(out); print(out, W, H, len(legend), 'meshes')
