from common import *
from pedestrian_lifts import SITES,exterior
for site in SITES:
 B=Meshes();meta=exterior(B,site)
 for label in B.labels:label['detail']=0
 B.save_all();(OUT/(site['key']+'-venue.pending.json')).write_text(json.dumps(meta,separators=(',',':')))
 print(site['key'],len(B.groups),'batches',sum(len(g['faces'])for g in B.groups.values()),'triangles')
r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.update(s['id']for s in SITES);r.write_text(json.dumps(sorted(ids)))
