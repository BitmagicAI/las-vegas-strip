#!/usr/bin/env python3
"""Draw drivable roads and film routes: python3 tools/film/route-map.py <out.png> x0 x1 z0 z1 [route-json ...] (routes: [[x,z,v],...])."""
import json, sys, os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__)); import roads
out, x0, x1, z0, z1 = sys.argv[1], *map(float, sys.argv[2:6])
S = 1600 / (x1 - x0); W, H = 1600, int((z1 - z0) * S)
img = Image.new('RGB', (W, H), (18, 20, 24)); d = ImageDraw.Draw(img)
P = lambda x, z: ((x - x0) * S, (z - z0) * S)
pos, edges = roads.network()
for a, es in edges.items():
    for b, c, hw, name in es:
        col = {'primary': (110, 110, 130), 'service': (60, 60, 70)}.get(hw, (85, 85, 100))
        d.line([P(*pos[a]), P(*pos[b])], fill=col, width=2 if hw == 'primary' else 1)
colors = [(255, 80, 60), (80, 220, 255), (255, 220, 60), (120, 255, 120)]
for k, f in enumerate(sys.argv[6:]):
    pts = json.load(open(f))
    d.line([P(p[0], p[1]) for p in pts], fill=colors[k % 4], width=3)
    d.ellipse([*map(lambda v: v - 5, P(pts[0][0], pts[0][1])), *map(lambda v: v + 5, P(pts[0][0], pts[0][1]))], fill=colors[k % 4])
for name, x, z in [('Bellagio', -250, 400), ('Paris/Eiffel', 74, 400), ('Caesars', -150, -80), ('Flamingo', 120, -50), ('LINQ', 300, -200), ('Venetian', 230, -690), ('Cosmo', -120, 680), ('Aria', -330, 960), ('NYNY', -168, 1533), ('PH', 170, 700), ('Sphere', 983, -584)]:
    if x0 <= x <= x1 and z0 <= z <= z1: d.text(P(x, z), name, fill=(255, 255, 255))
img.save(out); print(out, W, H)
