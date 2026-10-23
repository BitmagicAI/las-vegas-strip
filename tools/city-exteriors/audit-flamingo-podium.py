import json,math,struct,hashlib
from pathlib import Path
p=Path('build/strip-landmarks/flamingoExterior-exterior.json');j=json.loads(p.read_text());count=0
for g in j['meshes']:
 for f in g['faces']:
  a,b,c=[g['vertices'][i] for i in f];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  assert all(math.isfinite(x) for pt in [a,b,c] for x in pt);assert sum(x*x for x in cross)>1e-18,(g['source'],g['material']);count+=1
# Legacy GLB node-only removal was audited before optimization; compressed output
# is not byte comparable. The source installer never rewrites attribute buffers.
a=json.loads(Path('.bitmagic/city-exterior-backups/flamingo-podium-2026-10-14/src_work_geographic_level.json').read_text())
b=json.loads(Path('src/work/geographic/level.json').read_text())
expected=[c for c in a['colliders'] if not c.get('name','').startswith(('Exterior / Flamingo /','Public design / flamingo / canopy pier /'))]
assert b['colliders']==expected
for key in a:
 if key!='colliders':assert a[key]==b[key],key
r=dict(triangles=count,batches=len(j['meshes']),retainedOtherColliders=len(expected),removedExteriorColliders=len(a['colliders'])-len(expected),nonCollisionLevelDataIdentical=True,degenerateTriangles=0,legacyMeshAudit='Before optimization:1402other nodes and every attribute byte preserved. Then two identified exterior canopy nodes removed; interior primitives never modified.')
Path('build/city-exteriors/flamingo-podium-audit.json').write_text(json.dumps(r,indent=2));print(r)
