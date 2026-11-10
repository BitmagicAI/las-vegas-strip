"""Reproducible deck/pool samples; omit the newly furnished solid footprints."""
import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from wynn_court_furniture import furnish_club
club=footprint('way/156626862');court=club.convex_hull.buffer(.12,join_style=2).difference(club).buffer(-.2)
water=LineString([(640,-1527),(629,-1505),(615,-1482),(602,-1460)]).buffer(5.5,resolution=24).union(Point(640,-1527).buffer(7.5,resolution=24)).union(Point(602,-1460).buffer(7.5,resolution=24)).intersection(court.buffer(-3.5))
b=Meshes();b.property='test';furnish_club(b,court,water)
c=b.solids['test'];v=c['vertices'];occupied=[]
for i in range(0,len(c['indices']),3):
 tri=Polygon([(v[j*3],v[j*3+2]) for j in c['indices'][i:i+3]])
 if tri.area>1e-8:occupied.append(tri)
occupied=unary_union(occupied).buffer(.15)
pts=[]
for x in range(590,662,2):
 for z in range(-1540,-1440,2):
  p=Point(x,z)
  if water.buffer(-.3).contains(p):pts.append([x,-1.25,z,'pool-bed'])
  elif court.buffer(-.35).difference(water.buffer(.5)).difference(occupied).contains(p):pts.append([x,.28,z,'clear-deck'])
p=Path('build/city-exteriors/encore-court-points.json');p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(pts));print(len(pts),'support samples')
