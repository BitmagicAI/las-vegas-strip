"""Compact base-map data for the info video's map animation: the raw OpenStreetMap survey (build/strip-survey/survey.json:
building footprints with their recorded or estimated heights) and the game's road network (build/geographic-strip/
road-network.json). World metres (x east, z south), rounded to 0.1 m. Writes build/info-video/page/data/map.json.
python3 tools/info-video/export_map.py"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = json.load(open(os.path.join(ROOT, 'build/strip-survey/survey.json')))
R = json.load(open(os.path.join(ROOT, 'build/geographic-strip/road-network.json')))
q = lambda v: round(v, 1)
blds = []
for b in S['buildings']:
    for poly in b['polygons']:
        ring = poly[0]
        blds.append([q(b.get('base') or 0), q(b['height'] or 3), 1 if b.get('kind') == 'height' else 0, [c for x, y in ring for c in (q(x), q(-y))]])
roads = [[r.get('highway', ''), q(r.get('width', 6)), [c for p in r['points'] for c in (q(p[0]), q(p[2]))]] for r in R['roads']]
strip = [c for p in R['stripRoute'] for c in (q(p[0]), q(p[2]))]
xs = [v for b in blds for v in b[3][0::2]]; zs = [v for b in blds for v in b[3][1::2]]
import math
R0 = 6378137.0; LON0, LAT0 = -115.173, 36.116
def ll(lon, lat): return (q((lon - LON0) * math.pi / 180 * R0 * math.cos(math.radians(LAT0))), q(-(lat - LAT0) * math.pi / 180 * R0))
def flat(coords): return [c for lon, lat in coords for c in ll(lon, lat)]
pav = json.load(open(os.path.join(ROOT, 'build/geographic-strip/county/pavement.geojson')))['features']
con = json.load(open(os.path.join(ROOT, 'build/geographic-strip/county/concrete.geojson')))['features']
pavement = []
for f in pav:
    g = f['geometry']; polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
    for poly in polys: pavement.append(flat(poly[0]))
concrete = []
for f in con:
    g = f['geometry']; lines = [g['coordinates']] if g['type'] == 'LineString' else g['coordinates']
    for ln in lines: concrete.append([f['properties'].get('TYPE', 0), flat(ln)])
out = dict(source='OpenStreetMap contributors (ODbL), Overpass extract ' + S['summary']['timestamp'], bounds=[min(xs), min(zs), max(xs), max(zs)],
           buildings=blds, roads=roads, strip=strip, pavement=pavement, concrete=concrete)
p = os.path.join(ROOT, 'build/info-video/page/data/map.json')
json.dump(out, open(p, 'w'), separators=(',', ':'))
print(len(blds), 'footprints', len(roads), 'roads', len(pavement), 'pavement', len(concrete), 'concrete', 'bounds', out['bounds'], os.path.getsize(p) // 1024, 'KB')
