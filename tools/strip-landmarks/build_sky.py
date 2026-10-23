from common import *
from sky_exterior import exterior,KEY
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')
# Keep collider dimensions consistent with the corrected visible owners.
from sky_exterior import records,Access,BuildingSurfaces
rs=records();surface=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='sky'))
collision={'vertices':[],'indices':[]}
for r in rs:
 for poly in parts(r['shape']):
  ps=list(poly.exterior.coords);ts=[]
  for a,b in zip(ps,ps[1:]):ts.extend(surface.wall(r['id'],a,b,0,r['height'],access))
  for q in parts(surface.roof(r['id'],poly,r['height'])):
   for t in triangles(q):ts.append([(x,r['height'],z) for x,z in list(t.exterior.coords)[:-1]])
  for t in ts:
   n=len(collision['vertices'])//3;collision['vertices'].extend(c for v in t for c in v);collision['indices'].extend([n,n+1,n+2])
p=Path('build/highrises/sky-collision.json');backup=Path('build/city-exteriors/before/sky-collision.json');backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():backup.write_bytes(p.read_bytes())
p.write_text(json.dumps(collision,separators=(',',':')))
