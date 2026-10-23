"""Clip only west portion of543422869's5m mapped shell. Preserve eastern podium."""
import sys,json,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks');from common import *
out=Path('build/geographic-strip');bak=Path('.bitmagic/city-exterior-backups/cvs-horseshoe-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
for n in ['city-meshes.json','city-colliders.json','building-index.json']:
 if not(bak/n).exists():shutil.copy2(out/n,bak/n)
p=footprint('way/543422869').buffer(.005)
def key(v):return tuple(sorted(tuple(round(c,4) for c in q)for q in v))
def clip(v):
 r=[]
 for a,b in zip(v,v[1:]+v[:1]):
  ina=a[0]>=68;inb=b[0]>=68
  if ina:r.append(a)
  if ina!=inb:
   t=(68-a[0])/(b[0]-a[0]);r.append([a[i]+(b[i]-a[i])*t for i in range(3)])
 return [[r[0],r[i],r[i+1]] for i in range(1,len(r)-1)]
gs=json.loads((bak/'city-meshes.json').read_text());replacements={}
for g in gs:
 if g['material']!='building-estimated':continue
 keep=[]
 for f in g['faces']:
  vs=[g['vertices'][i]for i in f]
  if min(v[0]for v in vs)<68 and max(v[1]for v in vs)==5 and all(v[1]in [0,5]and p.covers(Point(v[0],v[2]))for v in vs):
   ts=clip(vs);replacements[key(vs)]=ts
   for t in ts:
    ix=len(g['vertices']);g['vertices'].extend(t);keep.append([ix,ix+1,ix+2])
  else:keep.append(f)
 g['faces']=keep
assert replacements
(out/'city-meshes.json').write_text(json.dumps(gs,separators=(',',':')))
cs=json.loads((bak/'city-colliders.json').read_text());n=0
for c in cs:
 v=c['vertices'];keep=[]
 for k in range(0,len(c['indices']),3):
  f=c['indices'][k:k+3];ts=replacements.get(key([v[i*3:i*3+3]for i in f]))
  if ts is None:keep.extend(f);continue
  n+=1
  for t in ts:
   ix=len(v)//3;v.extend(c for q in t for c in q);keep.extend([ix,ix+1,ix+2])
 c['indices']=keep
(out/'city-colliders.json').write_text(json.dumps(cs,separators=(',',':')))
r=dict(changedTriangles=len(replacements),changedCollision=n,scope='Only5m shell543422869 west ofx68;east fragments retained')
Path('build/city-exteriors/cvs-horseshoe-ownership.json').write_text(json.dumps(r,indent=2));print(r)
