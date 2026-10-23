from building_surfaces import BuildingSurfaces
from shapely.geometry import box
from surface_geometry import triangles

class NoDoors:
 def wall(self,a,b,lo,hi):
  import math
  length=math.dist(a,b)
  return [[[a[0]+(b[0]-a[0])*x/length,y,a[1]+(b[1]-a[1])*x/length] for x,y in list(t.exterior.coords)[:-1]] for t in triangles(box(0,lo,length,hi))]

def record(ident,shape,h,base=0,part=False):return dict(id=ident,shape=shape,height=h,base=base,part=part,kind='height')
def area(vertices):
 import numpy as np
 a,b,c=map(lambda p:np.array(p),vertices)
 return float(np.linalg.norm(np.cross(b-a,c-a))*.5)
def walls(norm,r):
 return sum(area(t) for a,b in zip(r['shape'].exterior.coords,list(r['shape'].exterior.coords)[1:]) for t in norm.wall(r['id'],a,b,r['base'],r['height'],NoDoors()))
# Duplicate OSM outline and part: a single skin (not two same-depth surfaces).
r=[record('outline',box(0,0,10,10),10),record('part',box(0,0,10,10),10,part=True)];n=BuildingSurfaces(r)
assert abs(sum(walls(n,x) for x in r)-400)<1e-7
assert sum(n.roof(x['id'],x['shape'],x['height']).area for x in r)==100
# Podium + taller wing sharing one external wall: preserve its higher levels.
r=[record('podium',box(0,0,20,20),6),record('tower',box(0,0,10,10),80,part=True)];n=BuildingSurfaces(r)
assert abs(sum(walls(n,x) for x in r)-(80*6+40*74))<1e-7
assert sum(n.roof(x['id'],x['shape'],x['height']).area for x in r)==400
# Touching solids have no internal double-sided wall; unrelated wings survive.
r=[record('a',box(0,0,10,10),10),record('b',box(10,0,20,10),10)];n=BuildingSurfaces(r)
assert abs(sum(walls(n,x) for x in r)-600)<1e-7
# Elevated part must retain lower walls/roof when an actual air gap exists.
r=[record('low',box(0,0,10,10),5),record('high',box(0,0,10,10),20,base=8,part=True)];n=BuildingSurfaces(r)
assert n.roof('low',r[0]['shape'],5).area==100
assert abs(sum(walls(n,x) for x in r)-680)<1e-7
print('PASS: duplicate outlines, podium/tower joints, adjacent wings, elevated parts')

# The authored Veer models must never coexist with their OSM replacements.
import json
from pathlib import Path
index={r['id'] for r in json.loads(Path('build/geographic-strip/building-index.json').read_text())}
assert not index.intersection({'way/52134834','way/52134835'})
print('PASS: no duplicate OSM Veer tower instances')
