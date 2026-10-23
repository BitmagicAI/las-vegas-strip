from common import *
from paradise_road_small_frontage import exterior,KEY
B=Meshes();meta=exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces'])for g in B.groups.values()),'triangles')
r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.update(['way/986507542', 'way/986507541', 'way/986507532', 'way/969288406', 'way/969288402', 'way/969288399', 'way/969288398', 'way/969288397']);r.write_text(json.dumps(sorted(ids)))
