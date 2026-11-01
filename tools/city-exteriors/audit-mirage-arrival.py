"""Validate authored faces and exact preservation of unrelated collision triangles."""
import json,math
from pathlib import Path
p=Path('docs/project-records/mirage-arrival');data=json.loads(Path('build/strip-landmarks/mirageArrival-exterior.json').read_text());count=0;errors=[]
for g in data['meshes']:
 for f in g['faces']:
  count+=1;a,b,c=[g['vertices'][i] for i in f];u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  if not all(math.isfinite(x)for q in [a,b,c]for x in q)or sum(x*x for x in cross)<1e-16:errors.append(f)
a=json.loads(Path('.bitmagic/city-exterior-backups/mirage-arrival/mirageExterior-exterior-collision.json').read_text());b=json.loads(Path('build/strip-landmarks/mirageExterior-exterior-collision.json').read_text());assert b['vertices'][:len(a['vertices'])]==a['vertices']
old={tuple(a['indices'][i:i+3])for i in range(0,len(a['indices']),3)};kept={tuple(b['indices'][i:i+3])for i in range(0,len(b['indices']),3)if max(b['indices'][i:i+3])<len(a['vertices'])//3};assert kept<=old;assert len(old-kept)==36
r={'authoredTriangles':count,'removedCollisionTriangles':36,'preservedCollisionTriangles':len(kept),'addedCollisionTriangles':len(b['indices'])//3-len(kept),'oldCollisionVerticesPreserved':True,'errors':errors};(p/'geometry.json').write_text(json.dumps(r,indent=2)+'\n');print(r);assert not errors
