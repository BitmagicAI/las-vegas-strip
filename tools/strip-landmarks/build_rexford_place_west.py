from common import *
from rexford_place_west import exterior,KEY
B=Meshes();meta=exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.update(['way/1236621163', 'way/1236621164', 'way/1236621165', 'way/1236621166', 'way/1236621167', 'way/1236621168', 'way/1236621169', 'way/1236621170', 'way/1236621171', 'way/1236621172', 'way/1236621180']);r.write_text(json.dumps(sorted(ids)))
