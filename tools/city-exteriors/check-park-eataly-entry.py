"""Check additive source preservation and valid original entrance detail."""
import json,math,hashlib
from pathlib import Path
base=Path('.bitmagic/city-exterior-backups/park-eataly-entry');out=Path('build/strip-landmarks')
a=json.loads((base/'park-exterior.json').read_text());b=json.loads((out/'park-exterior.json').read_text())
assert b['meshes'][:len(a['meshes'])]==a['meshes'];assert a['labels']==b['labels']
assert (base/'park-exterior-collision.json').read_bytes()==(out/'park-exterior-collision.json').read_bytes()
seen=set();n=0
for g in b['meshes'][len(a['meshes']):]:
 for f in g['faces']:
  p=[g['vertices'][i] for i in f];assert all(math.isfinite(v) for q in p for v in q)
  u=[p[1][i]-p[0][i] for i in range(3)];v=[p[2][i]-p[0][i] for i in range(3)]
  c=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];assert sum(x*x for x in c)>1e-16
  key=tuple(sorted(tuple(round(v,6) for v in q) for q in p));assert key not in seen;seen.add(key);n+=1
report={'preservedGroups':len(a['meshes']),'oldLabelsUnchanged':True,'collisionByteIdentical':True,'addedFiniteNondegenerateUniqueTriangles':n}
Path('docs/project-records/park-eataly-entry/audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
