"""Audit original gateway and preserve the existing collision prefix."""
import json,math
from pathlib import Path
p=Path('docs/project-records/caesars-garage-roofs');data=json.loads(Path('build/strip-landmarks/caesarsGarageRoofs-exterior.json').read_text());count=0;errors=[]
for g in data['meshes']:
 for f in g['faces']:
  count+=1;a,b,c=[g['vertices'][i]for i in f];u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  if not all(math.isfinite(x)for q in [a,b,c]for x in q)or sum(x*x for x in cross)<1e-16:errors.append(f)
a=json.loads(Path('.bitmagic/city-exterior-backups/caesars-garage-roofs/caesarsExterior-exterior-collision.json').read_text());b=json.loads(Path('build/strip-landmarks/caesarsExterior-exterior-collision.json').read_text());assert b['vertices'][:len(a['vertices'])]==a['vertices'];assert b['indices'][:len(a['indices'])]==a['indices']
r={'authoredTriangles':count,'addedCollisionTriangles':(len(b['indices'])-len(a['indices']))//3,'preservedCollisionPrefix':True,'errors':errors};(p/'geometry.json').write_text(json.dumps(r,indent=2)+'\n');print(r);assert not errors
