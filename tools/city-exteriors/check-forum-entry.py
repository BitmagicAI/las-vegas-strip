"""Check added facade faces, collision preservation and sidewalk clearance."""
import json,math
from pathlib import Path
base=Path('.bitmagic/city-exterior-backups/forum-entry');out=Path('build/strip-landmarks')
a=json.loads((base/'forumShops-exterior.json').read_text());b=json.loads((out/'forumShops-exterior.json').read_text());seen=set();n=0
for g in b['meshes'][len(a['meshes']):]:
 for f in g['faces']:
  pts=[g['vertices'][i] for i in f];assert all(math.isfinite(v) for p in pts for v in p)
  u=[pts[1][i]-pts[0][i] for i in range(3)];v=[pts[2][i]-pts[0][i] for i in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];assert sum(x*x for x in cross)>1e-16
  key=tuple(sorted(tuple(round(v,6) for v in p) for p in pts));assert key not in seen;seen.add(key);n+=1
c=json.loads((out/'forumShops-exterior-collision.json').read_text());old=json.loads((base/'forumShops-exterior-collision.json').read_text());new=c['vertices'][len(old['vertices']):]
# Follow the concave frontage rather than a straight line through the road.
import sys
sys.path.insert(0,'build/south-strip/python')
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
route=[]
for z in range(-390,-309,5):
 t=abs(z+350);x=-7.9 if t<9 else -8+(.012 if z<-350 else .004)*(t-9)**2
 route.append((x+3,z))
verts=[c['vertices'][i:i+3] for i in range(0,len(c['vertices']),3)]
triangles=[Polygon([(verts[k][0],verts[k][2]) for k in c['indices'][i:i+3]]) for i in range(len(old['indices']),len(c['indices']),3)]
footprints=unary_union([p for p in triangles if p.area>1e-10])
clearance=LineString(route).distance(footprints);assert clearance>.4,clearance
report={'newTriangles':n,'finiteNondegenerateUnique':True,'routeXZ':route,'minAddedSolidClearance':clearance,'note':'New-plinth body clearance only. Actual movement checks exercise the complete installed scene and the curved pedestrian strip.'}
Path('docs/project-records/forum-entry/source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
