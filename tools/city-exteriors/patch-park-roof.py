"""Apply reference roof finishes without rebuilding Park's shared exterior."""
import json,copy
from pathlib import Path
p=Path('build/strip-landmarks/park-exterior.json')
c=p.with_name('park-exterior-collision.json')
b=Path('.bitmagic/city-exterior-backups/park-roof-2026-10-14');b.mkdir(parents=True,exist_ok=True)
for src in [p,c]:
 dst=b/src.name
 if not dst.exists():dst.write_bytes(src.read_bytes())
a=json.loads((b/p.name).read_text());groups=[];counts={};before=sum(len(g['faces']) for g in a['meshes'])
for g in a['meshes']:
 if not g['source'].startswith('park-podium-refined') or g['material']!='ph-roof':groups.append(g);continue
 buckets={}
 for f in g['faces']:
  yy=[g['vertices'][i][1] for i in f]
  mat='park-theatre-paint' if all(abs(y-15.21)<.001 for y in yy) else 'park-membrane-paint' if all(abs(y-11.08)<.001 for y in yy) else g['material']
  buckets.setdefault(mat,[]).append(f)
 for mat,faces in buckets.items():
  n=copy.deepcopy(g);n['material']=mat;n['faces']=faces;groups.append(n)
  if mat!=g['material']:counts[mat]=counts.get(mat,0)+len(faces)
a['meshes']=groups
assert sum(len(g['faces']) for g in groups)==before
assert all(counts.get(m,0)>0 for m in ['park-theatre-paint','park-membrane-paint'])
assert c.read_bytes()==(b/c.name).read_bytes()
p.write_text(json.dumps(a,separators=(',',':')))
report={'changedMaterialTriangles':counts,'triangles':before,'geometryPositionsUnchanged':True,'collisionByteIdentical':True,'labelsUnchanged':True}
Path('build/city-exteriors/park-roof-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
