from common import *
from harrahs_roof_detail import exterior
import copy
key='harrahs-exterior';backup=Path('.bitmagic/city-exterior-backups/harrahs-roof-2026-10-14');backup.mkdir(parents=True,exist_ok=True)
for suffix in ['.json','-collision.json']:
 p=OUT/(key+suffix)
 if not (backup/p.name).exists():(backup/p.name).write_bytes(p.read_bytes())
a=json.loads((backup/(key+'.json')).read_text());B=Meshes();B.property=key
for g in a['meshes']:
 g=copy.deepcopy(g)
 if g['source']=='harrahs-podium' and g['material']=='roof':g['material']='harrahs-membrane-paint'
 B.groups[(g['property'],g['source'],g['material'],g['detail'])]=g
B.labels=a['labels'];B.solids[key]=json.loads((backup/(key+'-collision.json')).read_text());exterior(B);B.save_all()
print(key,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
