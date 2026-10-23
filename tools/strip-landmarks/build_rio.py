from common import *
from rio_exterior import exterior,KEY,LOW
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.update(LOW);p.write_text(json.dumps(sorted(ids)))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
