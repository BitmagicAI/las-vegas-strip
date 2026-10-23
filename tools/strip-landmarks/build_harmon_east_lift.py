from common import *
from harmon_east_lift import exterior,KEY,ID
B=Meshes();meta=exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
(OUT/(KEY+'-venue.pending.json')).write_text(json.dumps(meta,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces'])for g in B.groups.values()),'triangles')
r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.add(ID);r.write_text(json.dumps(sorted(ids)))
