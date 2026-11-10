"""Remove only old podium visuals/collision within the new Hilton canopy footprint.
Road/ground surfaces, the existing high-rise guest entry and all other cells remain.
Run after a geographic rebuild; idempotent against the current collision source.
"""
import sys,json,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from resorts_world_arrival import cut_triangle,BASE
p=Path('build/geographic-strip/city-meshes.json')
if not (BASE/p.name).exists():shutil.copy2(p,BASE/p.name)
groups=json.loads(p.read_text());visual=[]
for g in groups:
 if g['material'] not in ['building-estimated','building-tagged'] or g['cell'] not in ['3,-14','3,-13']:continue
 v=g['vertices'];faces=[];ncut=0
 for f in g['faces']:
  t=[v[i]for i in f];pieces=cut_triangle(t) if max(q[1]for q in t)>3 else None
  if pieces is None:faces.append(f);continue
  ncut+=1
  for tri in pieces:
   n=len(v);v.extend(tri);faces.append([n,n+1,n+2])
 if ncut:g['faces']=faces;visual.append({'cell':g['cell'],'material':g['material'],'trianglesClipped':ncut})
if visual:p.write_text(json.dumps(groups,separators=(',',':')))
p=Path('build/geographic-strip/city-colliders.json')
if not (BASE/p.name).exists():shutil.copy2(p,BASE/p.name)
cells=json.loads(p.read_text());changed=[]
for c in cells:
 v=c['vertices'];indices=[];ncut=0
 for k in range(0,len(c['indices']),3):
  f=c['indices'][k:k+3];tri=[v[i*3:i*3+3]for i in f]
  pieces=cut_triangle(tri) if max(q[1]for q in tri)>3 else None
  if pieces is None:indices.extend(f);continue
  ncut+=1
  for t in pieces:
   n=len(v)//3;v.extend(x for q in t for x in q);indices.extend([n,n+1,n+2])
 if ncut:c['indices']=indices;changed.append({'cell':c['id'],'trianglesClipped':ncut})
if changed:p.write_text(json.dumps(cells,separators=(',',':')))
report=Path('docs/project-records/rw-arrival/collision-install.json')
prior=json.loads(report.read_text()) if report.exists() else {}
if visual or changed:report.write_text(json.dumps({'visual':visual or prior.get('visual',[]),'collision':changed or prior.get('collision',[])},indent=2)+'\n')
print({'visual':visual,'collision':changed})
