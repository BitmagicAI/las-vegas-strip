from common import *
from park_eataly import exterior
import copy
p=OUT/'park-exterior.json';c=OUT/'park-exterior-collision.json';b=Path('.bitmagic/city-exterior-backups/park-eataly-2026-10-14');b.mkdir(parents=True,exist_ok=True)
for src in [p,c]:
 if not (b/src.name).exists():(b/src.name).write_bytes(src.read_bytes())
a=json.loads((b/p.name).read_text());B=Meshes();B.property='park-exterior'
for g in a['meshes']:
 if g['source']=='eataly-south-frontage':continue
 B.groups[(g['property'],g['source'],g['material'],g['detail'])]=copy.deepcopy(g)
B.labels=[l for l in a['labels'] if l.get('source')!='eataly-south-frontage'];B.solids[B.property]=json.loads((b/c.name).read_text());exterior(B);B.save_all()
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.add('way/1437033263');p.write_text(json.dumps(sorted(ids)))
print('Park Eataly',sum(len(g['faces']) for g in B.groups.values()),'triangles',len(B.groups),'batches')
