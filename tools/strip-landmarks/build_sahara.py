from common import *
from sahara import exterior,KEY
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
p=OUT/'replacement-ids.json';ids=json.loads(p.read_text());ids=list(dict.fromkeys(ids+['way/135453935']));p.write_text(json.dumps(ids,indent=2))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
