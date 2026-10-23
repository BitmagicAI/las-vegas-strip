from common import *
from caesars_exterior import exterior,KEY,IDS,LOW
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.update(IDS+LOW+['way/1168129083','way/34000287','way/364846541','way/1340330691','way/1340330690','way/364846540','way/115672897','way/364846543','way/180831020']);p.write_text(json.dumps(sorted(ids)))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
