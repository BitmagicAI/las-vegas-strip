import json,math,hashlib
from pathlib import Path
p=json.load(open('build/strip-landmarks/ti-exterior.json'));r={'triangles':0,'newTriangles':0,'degenerate':0,'nonfinite':0,'batches':len(p['meshes'])}
for g in p['meshes']:
 r['triangles']+=len(g['faces'])
 if not g['source'].startswith('ti-') or g['source']=='ti-podium':continue
 r['newTriangles']+=len(g['faces'])
 for f in g['faces']:
  a,b,c=[g['vertices'][i] for i in f];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  if sum(x*x for x in n)<1e-14:r['degenerate']+=1
  if not all(math.isfinite(x) for v in [a,b,c] for x in v):r['nonfinite']+=1
old=json.load(open('.bitmagic/city-exterior-backups/ti-frontage-2026-10-14/ti-exterior-collision.json'));new=json.load(open('build/strip-landmarks/ti-exterior-collision.json'))
r['originalCollisionPrefixPreserved']=all(new[k][:len(old[k])]==old[k] for k in old)
old=json.load(open('.bitmagic/city-exterior-backups/ti-frontage-2026-10-14/ti-exterior.json'))
def retained(doc):return {(g['source'],g['material'],g['detail']):hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest() for g in doc['meshes'] if g['source']!='treasure-island-arrival' and not(g['source']=='ti-podium' and g['detail']==1) and not g['source'].startswith(('ti-frontage/','ti-ship/','ti-cove','ti-roof'))}
a,b=retained(old),retained(p);r['changedRetainedGroups']=[str(k) for k in a if a[k]!=b.get(k)]
Path('build/city-exteriors/ti-geometry-audit.json').write_text(json.dumps(r,indent=2));print(r)
assert not r['degenerate'] and not r['nonfinite'] and not r['changedRetainedGroups'] and r['originalCollisionPrefixPreserved']
