from common import *
from mandalay_bay import exterior,KEY
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')

r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.add('way/364846553');r.write_text(json.dumps(sorted(ids)))

from mandalay_bay import PODIUMS
from mandalay_pool_detail import IDS,CABANAS
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.update(PODIUMS+IDS+CABANAS);p.write_text(json.dumps(sorted(ids)))
