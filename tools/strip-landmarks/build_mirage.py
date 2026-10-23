from common import *
from mirage_exterior import exterior,KEY
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')

p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.add('way/1468774558');p.write_text(json.dumps(sorted(ids)))
