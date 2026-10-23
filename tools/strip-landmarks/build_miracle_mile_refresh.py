"""Refresh only Miracle Mile display skin; preserve all other PH geometry/collision."""
from common import *
from planet_hollywood import exterior
import copy
name='planetHollywood-exterior';backup=Path('.bitmagic/city-exterior-backups/miracle-mile-2026-10-14');backup.mkdir(parents=True,exist_ok=True)
for suffix in ['.json','-collision.json']:
 p=OUT/(name+suffix)
 if not (backup/p.name).exists():(backup/p.name).write_bytes(p.read_bytes())
old=json.loads((backup/(name+'.json')).read_text());fresh=Meshes();exterior(fresh)
def changed(source):return source.startswith('mall-west-') or source in ['north-entrance','south-entrance']
B=Meshes();B.property=name
for g in old['meshes']:
 if not changed(g['source']):B.groups[(g['property'],g['source'],g['material'],g['detail'])]=copy.deepcopy(g)
for k,g in fresh.groups.items():
 if changed(g['source']):B.groups[k]=g
B.labels=[x for x in old['labels'] if not changed(x['source'])]+[x for x in fresh.labels if changed(x['source'])]
B.solids[name]=json.loads((backup/(name+'-collision.json')).read_text());B.save_all()
print('Miracle Mile refresh',len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles; original collision unchanged')
