from common import *
from grand_chateau import exterior,KEY
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')

# The survey also contains an identical five-level podium part.
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.add('way/1421481074');p.write_text(json.dumps(sorted(ids)))
