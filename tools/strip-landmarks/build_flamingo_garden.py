from common import *
from flamingo_garden import exterior,KEY,IDS
B=Meshes();meta=exterior(B);B.save_all();(OUT/(KEY+'-venue.pending.json')).write_text(json.dumps(meta,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces'])for g in B.groups.values()),'triangles')

if (OUT/(KEY+"-exterior.glb")).exists():
 p=OUT/"replacement-ids.json";ids=set(json.loads(p.read_text()));ids.update(IDS);p.write_text(json.dumps(sorted(ids)))
