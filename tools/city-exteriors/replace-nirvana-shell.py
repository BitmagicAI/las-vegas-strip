"""Remove exactly the mapped Nirvana Hotel shell; preserve unrelated city data."""
import sys,json,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks');from common import footprint,Point,unary_union
out=Path('build/geographic-strip');bak=Path('.bitmagic/city-exterior-backups/nirvana-2026-10-20');bak.mkdir(parents=True,exist_ok=True)
for name in ['city-meshes.json','city-colliders.json','building-index.json']:
 if not (bak/name).exists():shutil.copy2(out/name,bak/name)
p=unary_union([footprint(i) for i in ['way/364846548']]).buffer(.005)
def key(vs):return tuple(sorted(tuple(round(c,4) for c in v) for v in vs))
def building(g):return g['material'] in ('building-estimated','building-tagged','utility') or g['material'].startswith('tag/')
gs=json.loads((bak/'city-meshes.json').read_text());removed=set()
for g in gs:
 if not building(g):continue
 keep=[]
 for face in g['faces']:
  vs=[g['vertices'][i] for i in face]
  if all(p.covers(Point(v[0],v[2])) for v in vs) and max(v[1] for v in vs)>.5:removed.add(key(vs))
  else:keep.append(face)
 g['faces']=keep
assert 10<len(removed)<150,len(removed)
(out/'city-meshes.json').write_text(json.dumps(gs,separators=(',',':')))
cs=json.loads((bak/'city-colliders.json').read_text());n=0
for c in cs:
 v=c['vertices'];idx=c['indices'];keep=[]
 for k in range(0,len(idx),3):
  tri=idx[k:k+3]
  if key([v[i*3:i*3+3] for i in tri]) in removed:n+=1
  else:keep.extend(tri)
 c['indices']=keep
(out/'city-colliders.json').write_text(json.dumps(cs,separators=(',',':')))
report=dict(removed=len(removed),colliderTrianglesRemoved=n,added=0,scope='Only building-material triangles wholly in Nirvana mapped footprint; all other triangles retained exactly.')
Path('build/city-exteriors/nirvana-ownership-audit.json').write_text(json.dumps(report,indent=2));print(report)
