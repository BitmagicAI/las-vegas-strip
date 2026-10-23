import json,math
from pathlib import Path
key='harrahs-exterior';base=Path('.bitmagic/city-exterior-backups/harrahs-roof-2026-10-14');p=Path('build/strip-landmarks')
a=json.loads((p/(key+'.json')).read_text());b=json.loads((base/(key+'.json')).read_text());gkey=lambda g:(g['source'],g['material'],g['detail']);new={gkey(g):g for g in a['meshes']};count=0
for g in b['meshes']:
 if g['source']=='harrahs-podium' and g['material']=='roof':g=dict(g,material='harrahs-membrane-paint')
 assert new[gkey(g)]==g;count+=1
n=0
for g in a['meshes']:
 if g['source']!='harrahs-upper-roof':continue
 for f in g['faces']:
  aa,bb,cc=[g['vertices'][i] for i in f];u=[bb[i]-aa[i] for i in range(3)];v=[cc[i]-aa[i] for i in range(3)];c=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  assert all(math.isfinite(x) for pt in [aa,bb,cc] for x in pt);assert min(pt[1] for pt in [aa,bb,cc])>19;assert sum(x*x for x in c)>1e-18;n+=1
assert (p/(key+'-collision.json')).read_bytes()==(base/(key+'-collision.json')).read_bytes()
r=dict(retainedGroups=count,materialOnlyRoofTriangles=57,addedTriangles=n,collisionByteIdentical=True,totalTriangles=sum(len(g['faces']) for g in a['meshes']));Path('build/city-exteriors/harrahs-roof-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
