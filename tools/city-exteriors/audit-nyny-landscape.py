import json,math
from pathlib import Path
base=Path('.bitmagic/city-exterior-backups/nyny-landscape')
old=json.loads((base/'source.json').read_text());new=json.loads(Path('build/strip-landmarks/nynyArrival-exterior.json').read_text())
for label in old['labels']:label['detail']=0 # builder applies this metadata before saving
assert new['meshes'][:len(old['meshes'])]==old['meshes'];assert old['labels']==new['labels']
count=0;bad=[]
for g in new['meshes'][len(old['meshes']):]:
 for f in g['faces']:
  count+=1;a,b,c=[g['vertices'][i] for i in f];u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  if not all(math.isfinite(x)for p in [a,b,c]for x in p) or sum(x*x for x in n)<1e-16:bad.append(f)
a=json.loads((base/'nynyArrival-exterior-collision.json').read_text());b=json.loads(Path('build/strip-landmarks/nynyArrival-exterior-collision.json').read_text());assert a['vertices']==b['vertices'][:len(a['vertices'])] and a['indices']==b['indices'][:len(a['indices'])]
r=dict(oldGroupsPreserved=len(old['meshes']),oldTrianglesPreserved=sum(len(g['faces'])for g in old['meshes']),newTriangles=count,newCollisionTriangles=(len(b['indices'])-len(a['indices']))//3,errors=bad)
Path('docs/project-records/nyny-arrival-landscape/geometry.json').write_text(json.dumps(r,indent=2)+'\n');print(r);assert not bad
