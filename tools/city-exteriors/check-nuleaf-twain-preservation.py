import json
from pathlib import Path
old=json.load(open('.bitmagic/city-exterior-backups/nuleaf-twain/city-meshes.json'))
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
    x,y,z=a['vertices'][i];assert 1710.00<=x<=1732.38 and -617.35<=z<=-606.73
   removed+=1
 assert j==len(b['faces'])
r=dict(groups=len(old),removedFaces=removed,verticesAndMetadataUnchanged=True,retainedFaceOrderUnchanged=True)
Path('build/city-exteriors/nuleaf-twain-preservation.json').write_text(json.dumps(r,indent=2));print(r)
