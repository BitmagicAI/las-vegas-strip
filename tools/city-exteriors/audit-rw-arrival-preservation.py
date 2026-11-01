"""Verify unrelated city materials/records remain byte-equivalent as JSON values."""
import json,hashlib
from pathlib import Path
base=Path('.bitmagic/city-exterior-backups/rw-arrival');root=Path('build/geographic-strip');result={}
def digest(v):return hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
for filename in ['city-meshes.json','city-colliders.json']:
 def snapshot(path):
  data=json.loads(path.read_text());other=[];target=[]
  for g in data:
   selected=(g.get('cell',g.get('id')) in ['3,-13','3,-14'] and (filename=='city-colliders.json' or g['material'] in ['building-estimated','building-tagged']))
   (target if selected else other).append(digest(g))
  return other,target
 a,at=snapshot(base/filename);b,bt=snapshot(root/filename);assert a==b
 result[filename]={'unchangedOtherRecords':len(a),'changedTargetRecords':sum(x!=y for x,y in zip(at,bt))}
Path('docs/project-records/rw-arrival/preservation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
