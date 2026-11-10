import json,math
from pathlib import Path
base=Path('.bitmagic/city-exterior-backups/hgv-sky');out=Path('build/strip-landmarks');reports={}
for key in ['hgvExterior-exterior','skyExterior-exterior']:
 a=json.loads((base/(key+'.json')).read_text());b=json.loads((out/(key+'.json')).read_text())
 assert b['meshes'][:len(a['meshes'])]==a['meshes'];assert b['labels']==a['labels']
 ca=json.loads((base/(key+'-collision.json')).read_text());cb=json.loads((out/(key+'-collision.json')).read_text())
 assert cb['vertices'][:len(ca['vertices'])]==ca['vertices'];assert cb['indices'][:len(ca['indices'])]==ca['indices']
 count=0
 for g in b['meshes'][len(a['meshes']):]:
  for f in g['faces']:
   pts=[g['vertices'][i] for i in f];assert all(math.isfinite(v) for q in pts for v in q)
   u=[pts[1][j]-pts[0][j] for j in range(3)];v=[pts[2][j]-pts[0][j] for j in range(3)];c=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];assert sum(x*x for x in c)>1e-16;count+=1
 r={'preservedGroups':len(a['meshes']),'preservedLabels':True,'preservedCollision':True,'addedValidTriangles':count,'addedCollisionTriangles':(len(cb['indices'])-len(ca['indices']))//3}
 reports[key]=r
Path('docs/project-records/hgv-sky/audit.json').write_text(json.dumps(reports,indent=2)+'\n');print(reports)
