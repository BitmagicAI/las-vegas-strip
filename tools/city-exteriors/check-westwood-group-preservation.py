import json,sys
sys.path.insert(0,"tools/strip-landmarks")
from common import footprint,Point,unary_union
owned=unary_union([footprint(i) for i in ['way/276428190','way/464694095']]).buffer(.005)
from pathlib import Path
old=json.load(open('.bitmagic/city-exterior-backups/westwood-group/city-meshes.json'))
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
    x,y,z=a['vertices'][i];assert owned.covers(Point(x,z))
   removed+=1
 assert j==len(b['faces'])
r=dict(groups=len(old),removedFaces=removed,verticesAndMetadataUnchanged=True,retainedFaceOrderUnchanged=True)
Path('build/city-exteriors/westwood-group-preservation.json').write_text(json.dumps(r,indent=2));print(r)
# Collision must lose only the same claimed shell triangles, not nearby roads.
oldc=json.load(open('.bitmagic/city-exterior-backups/westwood-group/city-colliders.json'))
newc=json.load(open('build/geographic-strip/city-colliders.json'))
assert len(oldc)==len(newc)
collision_removed=0
for a,b in zip(oldc,newc):
 assert {k:v for k,v in a.items() if k!='indices'}=={k:v for k,v in b.items() if k!='indices'}
 j=0
 for i in range(0,len(a['indices']),3):
  tri=a['indices'][i:i+3]
  if tri==b['indices'][j:j+3]:j+=3
  else:
   vs=[a['vertices'][q*3:q*3+3]for q in tri]
   assert all(owned.covers(Point(v[0],v[2]))for v in vs)
   assert max(v[1]for v in vs)>.5
   collision_removed+=1
 assert j==len(b['indices'])
assert collision_removed==removed
r['removedCollisionFaces']=collision_removed;r['otherCollisionUnchanged']=True
Path('build/city-exteriors/westwood-group-preservation.json').write_text(json.dumps(r,indent=2));print(r)
