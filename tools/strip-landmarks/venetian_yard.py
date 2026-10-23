"""Canal-side pedestrian grounds, fit around mapped water, buildings and roads.
Widths/planting rhythm are aerial-reference estimates, not surveyed elevations.
"""
import json,math
from shapely.geometry import Point,LineString,box
from shapely.ops import unary_union
from common import footprint,BYID,parts,Frame
from venetian_canal import outlines
from venetian_pool_garden import gardens

def yard(B):
 B.source='venetian-quays';B.detail=0
 water=unary_union([p for _,p in outlines()])
 bounds=water.buffer(18)
 buildings=unary_union([footprint(k) for k in BYID if footprint(k).intersects(bounds)])
 roads=[];walks=[]
 for r in json.load(open('build/strip-survey/survey.json'))['roads']:
  line=LineString([(x,-z) for x,z in r['points']])
  if not line.intersects(bounds):continue
  if r['class'] in ('footway','path','steps','pedestrian'):walks.append(line.buffer(2.2))
  else:roads.append(line.buffer(16 if r['class']=='primary' else 5.5))
 traffic=unary_union(roads);walk=unary_union(walks)
 # Protect every existing road and entrance. The lower promenade is a low slab
 # around the mapped basin, not a new road or a large whole-site flat platform.
 quay=water.buffer(10,join_style=2).difference(water.buffer(.50,join_style=2)).difference(buildings.buffer(.15)).difference(traffic)
 B.planar('sandstone',quay,.245,True)
 # Alternating pale stone courses follow the water rather than a generic roof tile.
 for d in [2.6,5.1,7.6]:
  band=water.buffer(d+.10,join_style=2).difference(water.buffer(d-.10,join_style=2)).intersection(quay)
  B.planar('ivory',band,.251)
 # Palm planters occupy the outer edge only; preserve a generous continuous quay.
 allowed=quay.difference(water.buffer(4)).difference(walk).difference(buildings.buffer(3.5))
 main=outlines()[0][1]
 if main.area<1000:main=outlines()[1][1]
 boundary=main.buffer(7,join_style=2).exterior
 candidates=[]
 for i in range(int(boundary.length//10)):
  p=boundary.interpolate(i*10)
  if p.x>205:continue
  if allowed.covers(p.buffer(1.7)) and all(p.distance(Point(*q))>8 for q in candidates):candidates.append((p.x,p.y))
 # Shared static near foliage, no new runtime systems or lights.
 gardens(B,allowed,water,lambda p:p,.245,points=candidates,crown_clearance=3.5)
 B.detail=0
 print('Venetian grounds:',round(quay.area,1),'m2;',len(candidates),'clearance-checked palms')
