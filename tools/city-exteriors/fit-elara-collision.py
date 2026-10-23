"""Retain low entrance approach triangles; replace only the obsolete tall shell."""
import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from luxor_facades import Access
from elara_exterior import tower_shape
p=Path('build/highrises/elara-collision.json');backup=Path('build/city-exteriors/before/elara-collision.json');backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():backup.write_bytes(p.read_bytes())
src=json.loads(backup.read_text());v=src['vertices'];out={'vertices':[],'indices':[]};ts=[]
for i in range(0,len(src['indices']),3):
 t=[v[k*3:k*3+3] for k in src['indices'][i:i+3]]
 if max(pt[1] for pt in t)<6:ts.append(t)
access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='elara'))
for poly in parts(tower_shape()):
 ps=list(poly.exterior.coords)
 for a,b in zip(ps,ps[1:]):ts.extend(access.wall(a,b,0,183))
for t in ts:
 n=len(out['vertices'])//3;out['vertices'].extend(c for pt in t for c in pt);out['indices'].extend([n,n+1,n+2])
p.write_text(json.dumps(out,separators=(',',':')))
print('Elara fitted shell',len(ts),'triangles; low entry geometry retained')
