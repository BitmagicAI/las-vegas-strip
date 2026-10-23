from common import *
from harley_dealership import exterior,KEY
B=Meshes();meta=exterior(B);B.save_all()
p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')

r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.update(['way/674358786','way/816094564']);r.write_text(json.dumps(sorted(ids)))
