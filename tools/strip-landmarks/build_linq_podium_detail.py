from common import *
from linq_podium_detail import exterior
import copy
key='linq-exterior';backup=Path('.bitmagic/city-exterior-backups/linq-podium-2026-10-14');backup.mkdir(parents=True,exist_ok=True)
for suffix in ['.json','-collision.json']:
 p=OUT/(key+suffix)
 if not (backup/p.name).exists():(backup/p.name).write_bytes(p.read_bytes())
a=json.loads((backup/(key+'.json')).read_text());B=Meshes();B.property=key
for old in a['meshes']:
 g=copy.deepcopy(old)
 if g['source'] in ['linq-podium','linq-promenade','guest-linq'] and g['material']=='roof':g['material']='linq-membrane-paint'
 if g['source']=='linq-promenade' and g['material']=='shopglass':g['material']='linq-glass'
 B.groups[(g['property'],g['source'],g['material'],g['detail'])]=g
B.labels=a['labels'];B.solids[key]=json.loads((backup/(key+'-collision.json')).read_text());exterior(B);B.save_all()
print(len(B.groups),'groups',sum(len(g['faces']) for g in B.groups.values()),'triangles')
