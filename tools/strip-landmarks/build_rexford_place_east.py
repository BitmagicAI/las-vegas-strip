from common import *
from rexford_place_east import exterior,KEY
B=Meshes();meta=exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.update(['way/1236746614', 'way/1236746613', 'way/1236746612', 'way/1236746611', 'way/1236621178', 'way/1236621177', 'way/1236621179', 'way/1236621176', 'way/1236621175', 'way/1236621174', 'way/1236621173']);r.write_text(json.dumps(sorted(ids)))
