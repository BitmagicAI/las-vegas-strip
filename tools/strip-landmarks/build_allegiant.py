from common import *
from allegiant import exterior,KEY,IDS
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[meta if x['key']==KEY else x for x in v] if any(x['key']==KEY for x in v) else v+[meta];p.write_text(json.dumps(v,separators=(',',':')))
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.update(IDS);p.write_text(json.dumps(sorted(ids)))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
