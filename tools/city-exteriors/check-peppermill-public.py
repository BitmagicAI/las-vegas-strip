"""Audit the retail neighbors and the new public interior source."""
import json,math
from pathlib import Path
base=Path('.bitmagic/city-exterior-backups/peppermill-public');out=Path('build/strip-landmarks')
a=json.loads((base/'peppermillRetail-exterior.json').read_text());b=json.loads((out/'peppermillRetail-exterior.json').read_text())
neighbor=lambda g:g['source'].startswith('retail/') and g['source']!='retail/way/160585815'
assert [g for g in a['meshes'] if neighbor(g)]==[g for g in b['meshes'] if neighbor(g)]
assert [g for g in a['labels'] if neighbor(g)]==[g for g in b['labels'] if neighbor(g)]
# All prior collision retained, with only a threshold slab appended to close a gap.
ca=json.loads((base/'peppermillRetail-exterior-collision.json').read_text());cb=json.loads((out/'peppermillRetail-exterior-collision.json').read_text())
assert cb['vertices'][:len(ca['vertices'])]==ca['vertices']
assert cb['indices'][:len(ca['indices'])]==ca['indices']
assert len(cb['indices'])-len(ca['indices'])==36
i=json.loads((out/'peppermillRetail-interior.json').read_text());count=bad=0
for g in i['meshes']:
 for f in g['faces']:
  p=[g['vertices'][j] for j in f];assert all(math.isfinite(v) for q in p for v in q)
  u=[p[1][j]-p[0][j] for j in range(3)];v=[p[2][j]-p[0][j] for j in range(3)];c=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  bad+=sum(x*x for x in c)<1e-16;count+=1
assert bad==0,(bad,count)
r={'neighborGroupsAndLabelsUnchanged':True,'allPriorExteriorCollisionPreserved':True,'addedThresholdColliderTriangles':12,'interiorFiniteNondegenerateTriangles':count,'layout':'Inferred, not surveyed; no whole-block completion claim'}
Path('docs/project-records/peppermill-public/audit.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
