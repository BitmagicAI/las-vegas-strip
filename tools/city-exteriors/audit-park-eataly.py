import json,math
from pathlib import Path
p=Path('build/strip-landmarks/park-exterior.json');a=json.loads(p.read_text());b=json.loads(Path('.bitmagic/city-exterior-backups/park-eataly-2026-10-14/park-exterior.json').read_text());key=lambda g:(g['source'],g['material'],g['detail']);new={key(g):g for g in a['meshes']};retained=0;tri=0
for g in b['meshes']:
 if g['source']=='eataly-south-frontage':continue
 assert new[key(g)]==g;retained+=1
for g in a['meshes']:
 if g['source']!='eataly-south-frontage':continue
 for f in g['faces']:
  p,q,r=[g['vertices'][i] for i in f];u=[q[i]-p[i] for i in range(3)];v=[r[i]-p[i] for i in range(3)];c=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  assert all(math.isfinite(x) for y in [p,q,r] for x in y);assert sum(x*x for x in c)>1e-18;tri+=1
old=json.loads(Path('.bitmagic/city-exterior-backups/park-eataly-2026-10-14/park-exterior-collision.json').read_text());col=json.loads(Path('build/strip-landmarks/park-exterior-collision.json').read_text());assert col['vertices'][:len(old['vertices'])]==old['vertices'];assert col['indices'][:len(old['indices'])]==old['indices']
out=dict(retainedGroups=retained,eatalyTriangles=tri,totalTriangles=sum(len(g['faces']) for g in a['meshes']),addedCollisionTriangles=(len(col['indices'])-len(old['indices']))//3,originalCollisionPrefixPreserved=True)
Path('build/city-exteriors/park-eataly-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
