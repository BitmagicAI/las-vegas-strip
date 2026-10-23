from common import *
from mgm_grand import exterior,KEY
B=Meshes();meta=exterior(B);meta['building']='mgm-grand';B.save_all()
p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')

r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()))
ids.update(['relation/6022477','way/115095165','way/116765496','way/116765497','way/116765498'])
r.write_text(json.dumps(sorted(ids)))
