import json,math
from pathlib import Path
key='luxorExterior-exterior';base=Path('.bitmagic/city-exterior-backups/luxor-site-2026-10-14');p=Path('build/strip-landmarks')
a=json.loads((p/(key+'.json')).read_text());b=json.loads((base/(key+'.json')).read_text());gkey=lambda g:(g['source'],g['material'],g['detail']);new={gkey(g):g for g in a['meshes']};count=0
for g in b['meshes']:
 if g['source'].startswith('podium/'):continue
 if g['material']=='ph-roof':g=dict(g,material='luxor-membrane-paint')
 assert new[gkey(g)]==g;count+=1
n=0
for g in a['meshes']:

 for f in g['faces']:
  aa,bb,cc=[g['vertices'][i] for i in f];u=[bb[i]-aa[i] for i in range(3)];v=[cc[i]-aa[i] for i in range(3)];c=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  assert all(math.isfinite(x) for pt in [aa,bb,cc] for x in pt);assert sum(x*x for x in c)>1e-18;n+=1
r=dict(retainedTowerGroups=count,totalTriangles=n,batches=len(a['meshes']),finiteCoordinates=True,degenerateTriangles=0);Path('build/city-exteriors/luxor-site-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
