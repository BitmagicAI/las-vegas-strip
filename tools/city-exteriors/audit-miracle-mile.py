"""Assert surgical facade refresh, clean geometry, unchanged physics and other owners."""
import json,math,hashlib
from pathlib import Path
base=Path('.bitmagic/city-exterior-backups/miracle-mile-2026-10-14');out=Path('build/strip-landmarks');name='planetHollywood-exterior'
a=json.loads((base/(name+'.json')).read_text());b=json.loads((out/(name+'.json')).read_text())
def changed(s):return s.startswith('mall-west-') or s in ['north-entrance','south-entrance']
def keep(d):return {(g['source'],g['material'],g['detail']):g for g in d['meshes'] if not changed(g['source'])}
assert keep(a)==keep(b),'Unrelated facade geometry changed'
assert (base/(name+'-collision.json')).read_bytes()==(out/(name+'-collision.json')).read_bytes(),'Collision changed'
invalid=0
for g in b['meshes']:
 if not changed(g['source']):continue
 for f in g['faces']:
  x,y,z=[g['vertices'][i] for i in f];u=[y[i]-x[i] for i in range(3)];v=[z[i]-x[i] for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  invalid+=not all(math.isfinite(q) for p in [x,y,z] for q in p) or sum(q*q for q in n)<1e-14
assert not invalid
r={'beforeTriangles':sum(len(g['faces']) for g in a['meshes']),'afterTriangles':sum(len(g['faces']) for g in b['meshes']),'afterBatches':len(b['meshes']),'retainedGroupsUnchanged':len(keep(a)),'collisionByteIdentical':True,'invalidNewFaces':invalid}
Path('build/city-exteriors/miracle-mile-audit.json').write_text(json.dumps(r,indent=2));print(r)
