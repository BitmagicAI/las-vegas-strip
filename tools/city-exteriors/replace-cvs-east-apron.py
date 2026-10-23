"""Remove only the remaining false five-metre parking shell, from current city data.
Satellite shows a ground service apron beside CVS and along Versailles, not a shop.
Backups are recovery snapshots only, never a regeneration input.
"""
import sys,json,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
out=Path('build/geographic-strip');bak=Path('.bitmagic/city-exterior-backups/cvs-east-apron-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
for n in ['city-meshes.json','city-colliders.json']:
 if not(bak/n).exists():shutil.copy2(out/n,bak/n)
p=footprint('way/543422869').buffer(.01)
def key(v):return tuple(sorted(tuple(round(c,4)for c in q)for q in v))
gs=json.loads((out/'city-meshes.json').read_text());removed=set()
for g in gs:
 if g['material']!='building-estimated':continue
 keep=[]
 for f in g['faces']:
  vs=[g['vertices'][i]for i in f]
  if min(v[0]for v in vs)>=67.999 and max(v[1]for v in vs)>.1 and all(-.001<=v[1]<=5.001 and p.covers(Point(v[0],v[2]))for v in vs):removed.add(key(vs))
  else:keep.append(f)
 g['faces']=keep
(out/'city-meshes.json').write_text(json.dumps(gs,separators=(',',':')))
cs=json.loads((out/'city-colliders.json').read_text());n=0
for c in cs:
 v=c['vertices'];keep=[]
 for k in range(0,len(c['indices']),3):
  f=c['indices'][k:k+3]
  if key([v[i*3:i*3+3]for i in f])in removed:n+=1
  else:keep.extend(f)
 c['indices']=keep
(out/'city-colliders.json').write_text(json.dumps(cs,separators=(',',':')))
r=dict(removedVisualTriangles=len(removed),removedCollisionTriangles=n,scope='Remaining east five-metre mapped shell543422869 only; current data input, other assets preserved.')
Path('build/city-exteriors/cvs-east-apron-cut.json').write_text(json.dumps(r,indent=2));print(r)
