"""Sample only authored lawn polygons, retaining existing terrain collision."""
import sys,json,random,math
from pathlib import Path
sys.path[:0]=['tools/strip-landmarks','tools/resort-blocks']
from common import *
root=Path('build/resort-blocks/bellagio')
meshes=json.loads((root/'bellagioBlock-exterior.json').read_text())['meshes']
polys=[]
for m in meshes:
 if m['source']=='south-arrival-landscape' and m['material']=='sage':
  for face in m['faces']:
   ps=[m['vertices'][i] for i in face]
   polys.append(Polygon([(p[0],p[2]) for p in ps]))
lawn=unary_union(polys).buffer(-.13)
rng=random.Random(8106);grass=[]
x0,z0,x1,z1=lawn.bounds
for x in np.arange(x0,x1,.18):
 for z in np.arange(z0,z1,.18):
  xx,zz=x+rng.uniform(-.075,.075),z+rng.uniform(-.075,.075)
  if not lawn.covers(Point(xx,zz)):continue
  # Uniform mown lawn: no raised/taller perimeter band.
  grass.append([round(xx,3),.512,round(zz,3),round(rng.random()*math.tau,3),round(rng.uniform(.85,1.05),3)])
trees=json.loads((root/'tree-placement.json').read_text())['trees']
Path('public/foliage/bellagio-placements.json').write_text(json.dumps(dict(trees=trees,grass=grass),separators=(',',':')))
print(f'{len(trees)} crown-cleared trees; {len(grass)} lawn tufts, all inside inset grass polygons')
