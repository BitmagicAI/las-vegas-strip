"""Update only HGV's existing shell collision to its per-wing elevations."""
import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from luxor_facades import Access
plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='hgv-boulevard');access=Access(plan)
out={'vertices':[],'indices':[]}
for p in parts(footprint('relation/6138877')):
 h=14 if p.area<800 else (90 if p.bounds[3]-p.bounds[1]>p.bounds[2]-p.bounds[0] else 123)
 ps=list(p.exterior.coords)
 tris=[]
 for a,b in zip(ps,ps[1:]):tris.extend(access.wall(a,b,0,h))
 for t in triangles(p):tris.append([(x,h,z) for x,z in list(t.exterior.coords)[:-1]])
 for tri in tris:
  start=len(out['vertices'])//3;out['vertices'].extend(c for v in tri for c in v);out['indices'].extend([start,start+1,start+2])
p=Path('build/highrises/hgv-boulevard-collision.json');backup=Path('build/city-exteriors/before/hgv-collision.json');backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():backup.write_bytes(p.read_bytes())
p.write_text(json.dumps(out,separators=(',',':')))
print(len(out['indices'])//3,'collision triangles')
