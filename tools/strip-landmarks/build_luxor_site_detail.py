from common import *
import copy
from luxor_north_detail import exterior as north,ID
from luxor_service_detail import exterior as service
from luxor_sphinx import exterior as sphinx
from luxor_pool_detail import exterior as pool
key='luxorExterior-exterior';backup=Path('.bitmagic/city-exterior-backups/luxor-site-2026-10-14');backup.mkdir(parents=True,exist_ok=True)
for suffix in ['.json','-collision.json']:
 p=OUT/(key+suffix)
 if not (backup/p.name).exists():(backup/p.name).write_bytes(p.read_bytes())
a=json.loads((backup/(key+'.json')).read_text());B=Meshes();B.property=key
for old in a['meshes']:
 if old['source'].startswith('podium/'):continue
 g=copy.deepcopy(old)
 if g['material']=='ph-roof':g['material']='luxor-membrane-paint'
 B.groups[(g['property'],g['source'],g['material'],g['detail'])]=g
B.labels=a['labels'];B.solids[key]=json.loads((backup/(key+'-collision.json')).read_text())
towerids=north(B);ids=[ID,'way/115647257']+service(B)+sphinx(B)+pool(B)
# Mapped small stepped wings are already drawn by the retained tower mesh. Transfer
# their collision before removing their duplicate mapped boxes.
owned=set(json.load(open('build/highrises/replacement-ids.json')))
C=Meshes();C.property=key
for i in towerids:
 if i in owned:continue
 p=footprint(i);r=BYID[i];C.shell(p,r['base'],r['height'],'x',roof=False);C.planar('x',p,r['height'],True);ids.append(i)
c=B.solids[key];other=C.solids[key];offset=len(c['vertices'])//3;c['vertices'].extend(other['vertices']);c['indices'].extend(i+offset for i in other['indices'])
B.save_all()
p=OUT/'replacement-ids.json';d=set(json.loads(p.read_text()));d.update(ids);p.write_text(json.dumps(sorted(d)))
p=OUT/'venues.json';v=json.loads(p.read_text());m=next(m for m in v if m['key']=='luxorExterior');m['bounds']=[-545,2050,-70,2440];p.write_text(json.dumps(v,separators=(',',':')))
print(len(B.groups),'groups',sum(len(g['faces']) for g in B.groups.values()),'triangles',len(c['indices'])//3,'collisiontriangles',ids)
