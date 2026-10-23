from common import *
from showcase import exterior,KEY
B=Meshes();meta=exterior(B)
# Adjacent facade segments share capped mullions. Keep only one exact visual face.
seen=set();removed=0
for g in B.groups.values():
 if g['source'].startswith('showcase-iv') or g['source']=='walgreens-showcase':continue
 faces=[]
 for face in g['faces']:
  key=tuple(sorted(tuple(round(v,6) for v in g['vertices'][i]) for i in face))
  if key in seen:removed+=1;continue
  seen.add(key);faces.append(face)
 g['faces']=faces
print('Removed exact duplicate facade cap faces:',removed)
B.save_all()
p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')

r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.update(['way/115649938','way/95224290','way/27897909','way/115649937','way/92281772']);r.write_text(json.dumps(sorted(ids)))
