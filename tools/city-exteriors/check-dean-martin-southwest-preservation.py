import json
from pathlib import Path
old=json.load(open('.bitmagic/city-exterior-backups/dean-martin-southwest/city-meshes.json'))
new=json.load(open('build/geographic-strip/city-meshes.json'))
assert len(old)==len(new)
removed=0
for a,b in zip(old,new):
 assert {k:v for k,v in a.items() if k!='faces'}=={k:v for k,v in b.items() if k!='faces'}
 j=0
 for f in a['faces']:
  if j<len(b['faces']) and f==b['faces'][j]:j+=1
  else:
   assert a['material'] in ('building-estimated','building-tagged','utility') or a['material'].startswith('tag/')
   for i in f:
    x,y,z=a['vertices'][i];assert -923.40<=x<=-900.56 and 2178.57<=z<=2240.21
   removed+=1
 assert j==len(b['faces'])
r=dict(groups=len(old),removedFaces=removed,verticesAndMetadataUnchanged=True,retainedFaceOrderUnchanged=True)
Path('build/city-exteriors/dean-martin-southwest-preservation.json').write_text(json.dumps(r,indent=2));print(r)
