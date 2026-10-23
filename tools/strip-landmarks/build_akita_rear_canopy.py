from common import *
from akita_rear_canopy import exterior,KEY
B=Meshes();meta=exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces'])for g in B.groups.values()),'triangles')
r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.update(['way/457939127']);r.write_text(json.dumps(sorted(ids)))
