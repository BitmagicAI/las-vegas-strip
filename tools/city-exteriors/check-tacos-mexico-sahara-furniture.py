"""Prevent a walkable aisle from hiding seats intersecting the mapped exterior wall."""
import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import footprint,Point
p=footprint('way/907577008').buffer(-.05)
g=json.load(open('build/strip-landmarks/tacos-mexico-sahara-interior.json'))['meshes']
count=0;bad=[]
for m in g:
 if m['material'] not in ['tm-seat','tm-table','tm-frame','tm-metal']:continue
 for x,y,z in m['vertices']:
  count+=1
  if not p.covers(Point(x,z)):bad.append([m['material'],x,y,z])
r=dict(furnitureVertices=count,outsideMappedShell=bad)
Path('build/city-exteriors/tacos-mexico-sahara-furniture-audit.json').write_text(json.dumps(r,indent=2))
print(r);assert not bad
