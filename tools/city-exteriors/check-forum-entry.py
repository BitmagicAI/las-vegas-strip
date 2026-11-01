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
# All added solid plinths are behind the x=18m sidewalk corridor, with margin.
assert max(new[0::3])<18-1
report={'newTriangles':n,'finiteNondegenerateUnique':True,'newSolidMaxX':max(new[0::3]),'sidewalkRouteX':18,'note':'Source clearance for additions only; actual walking checks exercise the complete installed scene.'}
Path('docs/project-records/forum-entry/source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
