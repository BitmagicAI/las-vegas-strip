import json,math
from pathlib import Path
p=Path('build/strip-landmarks/newYorkFrontage-exterior.json');a=json.loads(p.read_text());b=json.loads(Path('.bitmagic/city-exterior-backups/nyny-restaurants-2026-10-14/newYorkFrontage-exterior.json').read_text());key=lambda g:(g['source'],g['material'],g['detail']);new={key(g):g for g in a['meshes']};retained=0;tri=0
for g in b['meshes']:
 assert new[key(g)]==g;retained+=1
for g in a['meshes']:
 if g['source']!='park-restaurants':continue
 for f in g['faces']:
  p,q,r=[g['vertices'][i] for i in f];u=[q[i]-p[i] for i in range(3)];v=[r[i]-p[i] for i in range(3)];c=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  assert all(math.isfinite(x) for y in [p,q,r] for x in y);assert sum(x*x for x in c)>1e-18;tri+=1
old=json.loads(Path('.bitmagic/city-exterior-backups/nyny-restaurants-2026-10-14/newYorkFrontage-exterior-collision.json').read_text());col=json.loads(Path('build/strip-landmarks/newYorkFrontage-exterior-collision.json').read_text());assert col['vertices'][:len(old['vertices'])]==old['vertices'];assert col['indices'][:len(old['indices'])]==old['indices']
out=dict(retainedGroups=retained,restaurantTriangles=tri,totalTriangles=sum(len(g['faces']) for g in a['meshes']),addedCollisionTriangles=(len(col['indices'])-len(old['indices']))//3,originalCollisionPrefixPreserved=True)
Path('build/city-exteriors/nyny-restaurants-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
