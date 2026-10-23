"""Independent authored-tree crown and batch audit against nearby structures."""
import sys,json,math
from pathlib import Path
sys.path[:0]=['tools/strip-landmarks','tools/resort-blocks']
from common import *
from bellagio_garage import GARAGE,ROAD
O=Path('build/resort-blocks/bellagio');d=json.loads((O/'tree-placement.json').read_text());ts=d['trees']
protected=unary_union([footprint('relation/1599958'),GARAGE,ROAD,LineString([(-57,588),(-106,583),(-137,565),(-167,545),(-190,529)]).buffer(3),box(-57,581,-35,591),box(-255,424,-202,468)])
for i,t in enumerate(ts):
 x,_,z=t['position'];assert not protected.intersects(Point(x,z).buffer(t['crownRadius']))
 for o in ts[:i]:assert math.hypot(x-o['position'][0],z-o['position'][2])>=t['crownRadius']+o['crownRadius']
meshes=json.loads((O/'bellagioBlock-exterior.json').read_text())['meshes'];lods=[]
for n in range(3):
 ms=[m for m in meshes if m['source'].startswith('arrival-tree/') and m['source'].endswith('/'+str(n))]
 lods.append(dict(level=n,batches=len(ms),triangles=sum(len(m['vertices'])//3 for m in ms)))
assert lods[0]['triangles']>lods[1]['triangles']>lods[2]['triangles']
r=dict(trees=len(ts),cells=len({t['cell'] for t in ts}),lods=lods,clearance='4m full crowns clear protected architecture and each other',runtime='Seven distance transitions and hook cleanup tested by test-grove-lod.mjs')
(O/'tree-lod-audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
