"""Preservation, cell ownership and vault attachment checks for additive coffers."""
import hashlib,json,math,sys
from pathlib import Path
from patch_paris_arc_coffers import patch,SOURCE
source=Path(sys.argv[1] if len(sys.argv)>1 else '.bitmagic/city-exterior-backups/paris-arc-2026-11-07/parisBlock-exterior.json')
old=json.loads(source.read_text())
new,audit=patch(old)
assert new['meshes'][:len(old['meshes'])]==old['meshes']
assert new['labels']==old['labels']
assert patch(new)[0]==new, 'Patch must be idempotent'
added=new['meshes'][len(old['meshes']):]
# Find retained barrel triangles from original geometry, independent of coffer frames.
barrel=[]
for mesh in old['meshes']:
 if not mesh['source'].startswith('arrival-arc@'):continue
 for face in mesh['faces']:
  pts=[mesh['vertices'][i] for i in face]
  if all(abs(math.hypot(p[1]-12.5,p[2]-490.7)-4.6)<1e-5 and p[1]>=12.5-1e-5 for p in pts):
   barrel.extend(pts)
assert barrel, 'Retained barrel surface must exist'
lo=min(p[0] for p in barrel);hi=max(p[0] for p in barrel)
angles=sorted(set(round(math.atan2(p[1]-12.5,490.7-p[2]),8) for p in barrel))
maxstep=max(b-a for a,b in zip(angles,angles[1:]))
minradius=4.6*math.cos(maxstep/2)
for mesh in added:
 for p in mesh['vertices']:
  assert all(math.isfinite(v) for v in p)
  assert lo<p[0]<hi and p[1]>12.7, 'Decoration must stay inside barrel span and above circulation'
  r=math.hypot(p[1]-12.5,p[2]-490.7)
  assert r<minradius-.05 or r>4.6+.02, 'Frames must bridge backing, avoiding coplanar surfaces'
 for face in mesh['faces']:
  pts=[mesh['vertices'][i] for i in face]
  cell=f"@{math.floor(sum(p[0] for p in pts)/192)}_{math.floor(sum(p[2] for p in pts)/192)}"
  assert mesh['source']==SOURCE+cell
  u=[pts[1][k]-pts[0][k] for k in range(3)];v=[pts[2][k]-pts[0][k] for k in range(3)]
  assert sum(x*x for x in [u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]])>1e-12
report={**audit,'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'idempotent':True,'barrelSpan':[lo,hi],'minimumBackingRadius':minradius,
        'cellOwnership':True,'finiteNondegenerate':True,'highClearance':True}
Path('docs/project-records/paris-frontage-refinement/geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
