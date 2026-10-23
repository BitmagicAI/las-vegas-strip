"""Remove old internal bridge guard panels only where the new guarded plaza joins.
Decks, supports, outside perimeter railings and all other cells remain unchanged.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
p=footprint('way/1421481100').simplify(.28,preserve_topology=True)
mask=p.buffer(7,resolution=24).intersection(box(-128,772,-37,861)).union(box(-58,848,-47,855)).difference(p).intersection(box(-110,770,-30,865)).buffer(-.25)
backup=Path('.bitmagic/city-exterior-backups/citycenter63-2026-10-19');backup.mkdir(parents=True,exist_ok=True)
def inside(v):
 a=np.array(v,float)
 if a[:,1].min()<6.08 or a[:,1].max()>7.4:return False
 if a[:,0].min()<-110 or a[:,0].max()>-37 or a[:,2].min()<772 or a[:,2].max()>861:return False
 return all(mask.contains(Point(q[0],q[2])) for q in a)
report={}
for fname in ['city-meshes.json','city-colliders.json']:
 path=Path('build/geographic-strip')/fname
 if not (backup/fname).exists():(backup/fname).write_bytes(path.read_bytes())
 d=json.loads(path.read_text());removed=0
 for g in d:
  if fname=='city-meshes.json':
   if g['cell'] not in ['-1,4','-1,5'] or g['material'] not in ['bridge-metal','bridge-concrete','bridge-glass','bridge-light']:continue
   v=g['vertices'];old=g['faces'];g['faces']=[f for f in old if not inside([v[i] for i in f])];removed+=len(old)-len(g['faces'])
  else:
   if g['id'] not in ['-1,4','-1,5']:continue
   v=np.array(g['vertices']).reshape(-1,3);faces=np.array(g['indices']).reshape(-1,3);kept=[f.tolist() for f in faces if not inside(v[f])];removed+=len(faces)-len(kept);g['indices']=[i for f in kept for i in f]
 path.write_text(json.dumps(d,separators=(',',':')));report[fname]=removed
Path('build/city-exteriors/citycenter63-bridge-join.json').write_text(json.dumps(report,indent=2));print(report)
