"""Replace only the claimed shell using current city data, never an old backup."""
import json,sys,shutil,hashlib
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import footprint,Point,unary_union
out=Path('build/geographic-strip');land=Path('build/strip-landmarks');idents=['way/390003970']
area=unary_union([footprint(i) for i in idents]).buffer(.005);xmin,zmin,xmax,zmax=area.bounds
bak=Path('.bitmagic/city-exterior-backups/twain-laundry');bak.mkdir(parents=True,exist_ok=True)
names=['city-meshes.json','city-colliders.json','building-index.json']
for name in names:
 if not (bak/name).exists():shutil.copy2(out/name,bak/name)
def key(vs):return tuple(sorted(tuple(round(c,4) for c in v) for v in vs))
gs=json.loads((out/names[0]).read_text());removed=set()
for g in gs:
 if g['material'] not in ('building-estimated','building-tagged','utility') and not g['material'].startswith('tag/'):continue
 keep=[]
 for face in g['faces']:
  vs=[g['vertices'][i] for i in face]
  if all(xmin<=v[0]<=xmax and zmin<=v[2]<=zmax for v in vs) and all(area.covers(Point(v[0],v[2])) for v in vs) and max(v[1] for v in vs)>.5:removed.add(key(vs))
  else:keep.append(face)
 g['faces']=keep
# Resume a partially completed install using only exact original owned-face keys.
# This never restores old city data or replaces another contributor's faces.
if not removed:
 original=json.loads((bak/names[0]).read_text())
 for g in original:
  if g['material'] not in ('building-estimated','building-tagged','utility') and not g['material'].startswith('tag/'):continue
  for face in g['faces']:
   vs=[g['vertices'][i] for i in face]
   if all(xmin<=v[0]<=xmax and zmin<=v[2]<=zmax for v in vs) and all(area.covers(Point(v[0],v[2])) for v in vs) and max(v[1] for v in vs)>.5:removed.add(key(vs))
 del original
assert len(removed)<300, 'Unexpected replacement size'
if removed:
 (out/names[0]).write_text(json.dumps(gs,separators=(',',':')))
 cs=json.loads((out/names[1]).read_text());count=0
 for c in cs:
  v=c['vertices'];idx=c['indices'];keep=[]
  for i in range(0,len(idx),3):
   tri=idx[i:i+3]
   if key([v[j*3:j*3+3] for j in tri]) in removed:count+=1
   else:keep.extend(tri)
  c['indices']=keep
 (out/names[1]).write_text(json.dumps(cs,separators=(',',':')))
 print('Removed owned shell triangles:',len(removed),'collision:',count)
 report=Path('build/city-exteriors/twain-laundry-ownership-audit.json');report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(dict(owners=idents,removedTriangles=len(removed),removedCollisionTriangles=count,scope='Current data only; other faces and colliders retained'),indent=2))
index=json.loads((out/names[2]).read_text());index=[b for b in index if b['id'] not in idents];(out/names[2]).write_text(json.dumps(index,separators=(',',':')))
# Read latest metadata immediately before updating only our key.
meta=json.loads((land/'twain-laundry-metadata.json').read_text());venues=json.loads((land/'venues.json').read_text());venues=[v for v in venues if v['key']!=meta['key']];venues.append(meta);(land/'venues.json').write_text(json.dumps(venues,separators=(',',':')))
r=land/'replacement-ids.json';ids=set(json.loads(r.read_text()));ids.update(idents);r.write_text(json.dumps(sorted(ids)))
