from common import *
from park_mgm import exterior
p=OUT/'park-exterior.json';c=OUT/'park-exterior-collision.json';backup=Path('build/city-exteriors/before/park');backup.mkdir(parents=True,exist_ok=True)
for a in [p,c]:
 dest=backup/a.name
 if not dest.exists():dest.write_bytes(a.read_bytes())
old=json.loads((backup/p.name).read_text());collision=(backup/c.name).read_bytes()
B=Meshes();exterior(B);B.save_all();new=json.loads(p.read_text())
# Remove only the old generic podium skin; retain the existing arrival objects.
keep=[]
for g in old['meshes']:
 if g['source']=='park-podium' and (g['material'] in ['sage','roof','ivory','darkglass'] or (g['material']=='steel' and g['detail']==1)):continue
 keep.append(g)
new['meshes']+=keep;new['labels']+=old['labels'];p.write_text(json.dumps(new,separators=(',',':')));c.write_bytes(collision)
print(len(new['meshes']),'batches',sum(len(g['faces']) for g in new['meshes']),'triangles; original collision retained')
