"""Surgical TI exterior pass. Retain tower, interior, entrances and city roads."""
from common import *
from ti_frontage import build,IDS
import copy
path=OUT/'ti-exterior.json';backup=Path('.bitmagic/city-exterior-backups/ti-frontage-2026-10-14');backup.mkdir(parents=True,exist_ok=True)
for name in ['ti-exterior.json','ti-exterior-collision.json']:
 if not (backup/name).exists():(backup/name).write_bytes((OUT/name).read_bytes())
old=json.loads((backup/path.name).read_text());B=Meshes();B.property='ti-exterior';B.solids[B.property]=json.loads((backup/'ti-exterior-collision.json').read_text())
config=next(x for x in json.loads((OUT/'next-plan.json').read_text()) if x['key']=='ti');x,z,yaw=config['frame'];F=Frame(B,x,z,yaw);pos=F.p(config['width']/2+20,0,-5);S=Frame(B,pos[0],pos[2],yaw+.2)
removed=0
for g in old['meshes']:
 g=copy.deepcopy(g)
 if g['source']=='ti-podium' and g['detail']==1:
  vv=g['vertices'];g['faces']=[f for f in g['faces'] if not (sum(vv[i][0] for i in f)/3>195 and -918<sum(vv[i][2] for i in f)/3<-864)]
 if g['source']=='treasure-island-arrival':
  # The former ship/lagoon was placed on the north side of the hotel. Its
  # isolated bounds do not touch the entry canopy, which remains intact.
  vv=g['vertices'];ff=[]
  for f in g['faces']:
   cx=sum(vv[i][0] for i in f)/3-S.x;cz=sum(vv[i][2] for i in f)/3-S.z
   lx=S.co*cx-S.si*cz;lz=S.si*cx+S.co*cz
   if abs(lx)<15 and abs(lz)<26:removed+=1
   else:ff.append(f)
  g['faces']=ff
 if g['faces']:B.groups[(g['property'],g['source'],g['material'],g['detail'])]=g
B.labels=old['labels'];build(B)
# Shapely clipping may leave collinear roof triangles at cut boundaries.
for g in B.groups.values():
 if g['source'].startswith('ti-frontage/'):
  v=np.array(g['vertices']);g['faces']=[f for f in g['faces'] if np.linalg.norm(np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]]))>1e-7]
B.save_all()
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.update(IDS);p.write_text(json.dumps(sorted(ids)))
print('removed old off-site ship triangles',removed,'total',sum(len(g['faces']) for g in B.groups.values()),'batches',len(B.groups))
