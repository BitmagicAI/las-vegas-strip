from common import *
from santa_paula_north import exterior,KEY
B=Meshes();meta=exterior(B)
for label in B.labels:label['detail']=0
B.save_all()
p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
r=OUT/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.update(['way/1236725804', 'way/1236725803', 'way/1236725806', 'way/1236725802', 'way/1236725805', 'way/1236725801']);r.write_text(json.dumps(sorted(ids)))
