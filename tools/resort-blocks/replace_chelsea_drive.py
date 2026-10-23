"""Remove only two inferred raised service drives replaced by the arrival court.

Match original bridge-generator triangle plans, never a broad geographic deletion.
The road separation pass adjusts their Y coordinates by up to 0.1 m.
Run before city export; safe to repeat after a geographic rebuild.
"""
import json
from pathlib import Path
out=Path('build/geographic-strip')
ids=('682151838/','682151847/')
key=lambda pts:tuple(sorted((round(p[0],4),round(p[2],4)) for p in pts))
keys=set()
for c in json.loads((out/'bridge-only-colliders.json').read_text()):
 if not c['id'].startswith(ids):continue
 v=c['vertices'];ix=c['indices']
 for i in range(0,len(ix),3):keys.add(key([v[j*3:j*3+3] for j in ix[i:i+3]]))
meshes=json.loads((out/'city-meshes.json').read_text());visual=0
for g in meshes:
 if not g['material'].startswith('bridge-'):continue
 before=len(g['faces']);g['faces']=[f for f in g['faces'] if key([g['vertices'][i] for i in f]) not in keys or max(g['vertices'][i][1] for i in f)>3.8];visual+=before-len(g['faces'])
(out/'city-meshes.json').write_text(json.dumps(meshes,separators=(',',':')))
cells=json.loads((out/'city-colliders.json').read_text());collision=0
for c in cells:
 if not -600<c['center'][0]<-200 or not 500<c['center'][1]<900:continue
 v=c['vertices'];ix=c['indices'];keep=[]
 for i in range(0,len(ix),3):
  tri=ix[i:i+3]
  if key([v[j*3:j*3+3] for j in tri]) in keys and max(v[j*3+1] for j in tri)<=3.8:collision+=1
  else:keep.extend(tri)
 c['indices']=keep
(out/'city-colliders.json').write_text(json.dumps(cells,separators=(',',':')))
print('Chelsea service drives replaced:',visual,'visual triangles;',collision,'collision triangles')
