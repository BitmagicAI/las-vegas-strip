"""Isolated experiment: restore only Airgas's owned shell to current city data.
The current state (after its installer) is the after side. No live city files change.
"""
import json, sys, shutil, hashlib
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import footprint, Point
root=Path('.bitmagic/city-cells/building-experiment'); root.mkdir(parents=True,exist_ok=True)
area=footprint('way/464694104').buffer(.005)
xmin,zmin,xmax,zmax=area.bounds
def owned(v):
 return max(p[1] for p in v)>.5 and all(xmin<=p[0]<=xmax and zmin<=p[2]<=zmax and area.covers(Point(p[0],p[2])) for p in v)
def key(v):return tuple(sorted(tuple(round(c,4) for c in p) for p in v))
current=Path('build/geographic-strip');backup=Path('.bitmagic/city-exterior-backups/airgas-highland')
groups=json.loads((current/'city-meshes.json').read_text());original=json.loads((backup/'city-meshes.json').read_text())
lookup={(g['cell'],g['material']):g for g in groups}; restored=set();affected=set()
for old in original:
 if old['material'] not in ('building-estimated','building-tagged','utility') and not old['material'].startswith('tag/'):continue
 target=lookup[(old['cell'],old['material'])]
 existing={key([target['vertices'][i] for i in f]) for f in target['faces']}
 for f in old['faces']:
  vs=[old['vertices'][i] for i in f]
  if not owned(vs):continue
  k=key(vs)
  if k in existing:continue
  start=len(target['vertices']);target['vertices'].extend(vs);target['faces'].append(list(range(start,start+3)));restored.add(k);affected.add(old['cell']);existing.add(k)
assert 0<len(restored)<700,len(restored)
(root/'city-meshes.json').write_text(json.dumps(groups,separators=(',',':')))
del original,groups,lookup
colliders=json.loads((current/'city-colliders.json').read_text());original=json.loads((backup/'city-colliders.json').read_text());lookup={g['id']:g for g in colliders};count=0
for old in original:
 if old['id'] not in affected:continue
 target=lookup[old['id']];v=old['vertices'];tv=target['vertices'];ti=target['indices']
 existing={key([tv[j*3:j*3+3] for j in ti[i:i+3]]) for i in range(0,len(ti),3)}
 for i in range(0,len(old['indices']),3):
  vs=[v[j*3:j*3+3] for j in old['indices'][i:i+3]];k=key(vs)
  if k not in restored or k in existing:continue
  start=len(tv)//3;tv.extend(c for p in vs for c in p);ti.extend(range(start,start+3));existing.add(k);count+=1
assert count==len(restored),(count,len(restored))
(root/'city-colliders.json').write_text(json.dumps(colliders,separators=(',',':')))
shutil.copy2(current/'city-materials.json',root/'city-materials.json')
source=Path('tools/geographic-strip/export_city.py').read_text().replace("OUT=Path('build/geographic-strip')",'OUT=Path('+repr(str(root))+')')
(root/'export-fixture.py').write_text(source)
report={'building':'way/464694104','restoredVisualTriangles':len(restored),'restoredCollisionTriangles':count,'sourceCells':sorted(affected),'visualCells':sorted({','.join(str(int(x)//5) for x in c.split(',')) for c in affected}),'scope':'Only this shell restored to current data in isolated fixture; live city untouched'}
(root/'fixture.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
