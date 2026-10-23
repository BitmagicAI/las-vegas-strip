"""Replace only Palazzo exterior facade dressing, retaining shell and collision."""
from common import *
from palazzo_street import decorate,canopy
path=OUT/'palazzo-exterior.json';old=json.loads(path.read_text())
backup=Path('.bitmagic/city-exterior-backups/palazzo-street-2026-10-14');backup.mkdir(parents=True,exist_ok=True)
if not (backup/path.name).exists():(backup/path.name).write_bytes(path.read_bytes())
collision=OUT/'palazzo-exterior-collision.json'
if not (backup/collision.name).exists():(backup/collision.name).write_bytes(collision.read_bytes())
B=Meshes();B.property='palazzo-exterior'
B.solids[B.property]=json.loads((backup/collision.name).read_text())
for g in old['meshes']:
 if g['source'] in ['palazzo-street-facades','palazzo-mapped-canopy','palazzo-porte-cochere'] or (g['source']=='palazzo-podium' and g['detail']==1):continue
 B.groups[(g['property'],g['source'],g['material'],g['detail'])]=g
B.labels=[x for x in old['labels'] if x['source']!='palazzo-porte-cochere']
config=next(x for x in json.loads((OUT/'next-plan.json').read_text()) if x['key']=='palazzo')
venue=next(x for x in json.loads((OUT/'venues.json').read_text()) if x['key']=='palazzo')
mask=unary_union([LineString(c['points']).buffer(2.45,cap_style=2,join_style=2) for c in config['connections']])
decorate(B,footprint(config['source']),13,venue['portals'],mask)
canopy(B)
B.save_all()
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.add('way/180584267');p.write_text(json.dumps(sorted(ids)))
print(sum(len(g['faces']) for g in B.groups.values()),'triangles',len(B.groups),'batches')
