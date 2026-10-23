"""Remove mapped placeholder building triangles for the Flamingo garden pass only."""
import sys,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from flamingo_garden import IDS
out=Path('build/geographic-strip');bak=Path('.bitmagic/city-exterior-backups/flamingo-garden-city-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
for name in ['city-meshes.json','city-colliders.json','building-index.json']:
 if not(bak/name).exists():shutil.copy2(out/name,bak/name)
shapes=[footprint(i).buffer(.006)for i in IDS];bounds=unary_union(shapes).bounds
def key(vs):return tuple(sorted(tuple(round(c,4)for c in v)for v in vs))
gs=json.loads((out/'city-meshes.json').read_text());removed=set()
for g in gs:
 if not(g['material']in ('building-estimated','building-tagged','utility')or g['material'].startswith('tag/')):continue
 keep=[]
 for face in g['faces']:
  vs=[g['vertices'][i]for i in face]
  if max(v[0]for v in vs)<bounds[0]or min(v[0]for v in vs)>bounds[2]or max(v[2]for v in vs)<bounds[1]or min(v[2]for v in vs)>bounds[3]:keep.append(face);continue
  if any(all(p.covers(Point(v[0],v[2]))for v in vs)for p in shapes):removed.add(key(vs))
  else:keep.append(face)
 g['faces']=keep
assert len(removed)<3000,len(removed)
(out/'city-meshes.json').write_text(json.dumps(gs,separators=(',',':')))
cs=json.loads((out/'city-colliders.json').read_text());n=0
for c in cs:
 v=c['vertices'];keep=[]
 for k in range(0,len(c['indices']),3):
  face=c['indices'][k:k+3]
  if key([v[i*3:i*3+3]for i in face])in removed:n+=1
  else:keep.extend(face)
 c['indices']=keep
(out/'city-colliders.json').write_text(json.dumps(cs,separators=(',',':')))
report=dict(removed=len(removed),colliderTrianglesRemoved=n,scope='Only current building-material triangles inside ten replacement footprints. No road/interior regeneration.')
Path('build/city-exteriors/flamingo-garden-city-cut.json').write_text(json.dumps(report,indent=2));print(report)
