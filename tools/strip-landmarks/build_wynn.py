from common import *
from wynn_encore import exterior,KEY
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')

# All mapped podiums now have an authored owner. Keep coarse city boxes out.
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()))
ids.update('way/'+i for i in ['27910891','205501268','111322055','111322079','111322083','111413431','111413433','128266659','135291730','142899198','142899199','156626862','886592894','886592897'])
p.write_text(json.dumps(sorted(ids)))
