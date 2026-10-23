from common import *
from nyny_park_restaurants import exterior
import copy
key='newYorkFrontage-exterior';backup=Path('.bitmagic/city-exterior-backups/nyny-restaurants-2026-10-14');backup.mkdir(parents=True,exist_ok=True)
for suffix in ['.json','-collision.json']:
 p=OUT/(key+suffix)
 if not (backup/p.name).exists():(backup/p.name).write_bytes(p.read_bytes())
a=json.loads((backup/(key+'.json')).read_text());B=Meshes();B.property=key
for g in a['meshes']:B.groups[(g['property'],g['source'],g['material'],g['detail'])]=copy.deepcopy(g)
B.labels=copy.deepcopy(a['labels']);B.solids[key]=json.loads((backup/(key+'-collision.json')).read_text());exterior(B);B.save_all()
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.add('way/567194734');p.write_text(json.dumps(sorted(ids)))
print(key,sum(len(g['faces']) for g in B.groups.values()),'triangles',len(B.groups),'batches')
