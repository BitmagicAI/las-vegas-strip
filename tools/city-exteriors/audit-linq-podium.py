import json,math
from pathlib import Path
key='linq-exterior';base=Path('.bitmagic/city-exterior-backups/linq-podium-2026-10-14');out=Path('build/strip-landmarks')
a=json.loads((out/(key+'.json')).read_text());b=json.loads((base/(key+'.json')).read_text());gkey=lambda g:(g['source'],g['material'],g['detail']);new={gkey(g):g for g in a['meshes']};changed=0
for g in b['meshes']:
 if g['source'] in ['linq-podium','linq-promenade','guest-linq'] and g['material']=='roof':g=dict(g,material='linq-membrane-paint');changed+=len(g['faces'])
 if g['source']=='linq-promenade' and g['material']=='shopglass':g=dict(g,material='linq-glass');changed+=len(g['faces'])
 assert new[gkey(g)]==g,gkey(g)
n=0
for g in a['meshes']:
 if g['source'] not in ['linq-lowrise-service','linq-promenade-upper']:continue
 for f in g['faces']:
  aa,bb,cc=[g['vertices'][i] for i in f];u=[bb[i]-aa[i] for i in range(3)];v=[cc[i]-aa[i] for i in range(3)];c=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  assert all(math.isfinite(x) for pt in [aa,bb,cc] for x in pt);assert sum(x*x for x in c)>1e-18
  if g['source']=='linq-lowrise-service':assert min(pt[1] for pt in [aa,bb,cc])>8.79
  n+=1
assert (out/(key+'-collision.json')).read_bytes()==(base/(key+'-collision.json')).read_bytes()
r=dict(retainedGroups=len(b['meshes']),materialOnlyTriangles=changed,addedTriangles=n,collisionByteIdentical=True,totalTriangles=sum(len(g['faces']) for g in a['meshes']));Path('build/city-exteriors/linq-podium-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
