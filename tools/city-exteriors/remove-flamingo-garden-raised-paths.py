"""Correct only erroneously elevated garden paths in the authored garden footprint."""
import sys,runpy,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from flamingo_garden import garden_mask
helper=runpy.run_path('tools/city-exteriors/cut-flamingo-garden.py');subtract=helper['subtract'];area=garden_mask();a=area.bounds
out=Path('build/geographic-strip');bak=Path('.bitmagic/city-exterior-backups/flamingo-garden-paths-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
for name in ['city-meshes.json','city-colliders.json']:
 if not(bak/name).exists():shutil.copy2(out/name,bak/name)
def key(vs):return tuple(sorted(tuple(round(c,4)for c in q)for q in vs))
gs=json.loads((out/'city-meshes.json').read_text());changed={};report=[]
for g in gs:
 if not g['material'].startswith('bridge-'):continue
 v=g['vertices'];keep=[];n=0
 for f in g['faces']:
  vs=np.array([v[i]for i in f]);pieces=subtract(vs,area)
  if pieces is None:keep.append(f);continue
  n+=1;changed[key(vs)]=[w@vs for w in pieces]
  for w in pieces:start=len(v);v.extend((w@vs).tolist());keep.append([start,start+1,start+2])
 g['faces']=keep
 if n:report.append(dict(material=g['material'],triangles=n))
(out/'city-meshes.json').write_text(json.dumps(gs,separators=(',',':')))
cs=json.loads((out/'city-colliders.json').read_text());n=0
for c in cs:
 v=c['vertices'];keep=[]
 for i in range(0,len(c['indices']),3):
  f=c['indices'][i:i+3];vs=[v[k*3:k*3+3]for k in f];pieces=changed.get(key(vs))
  if pieces is None:keep.extend(f);continue
  n+=1
  for q in pieces:start=len(v)//3;v.extend(q.ravel().tolist());keep.extend([start,start+1,start+2])
 c['indices']=keep
(out/'city-colliders.json').write_text(json.dumps(cs,separators=(',',':')))
r=dict(visual=report,collisionTriangles=n,scope='Only bridge-material faces in actual ground-level Flamingo garden. New path network owns their traversable replacement; road bridges elsewhere untouched.');Path('build/city-exteriors/flamingo-garden-paths-cut.json').write_text(json.dumps(r,indent=2));print(r)
