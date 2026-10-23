"""Remove obsolete city road/curb/bridge ribbons inside the authored arrival.
Clip in 3D (including vertical guard walls), keep unrelated buildings and lake.
Repeated execution is geometrically idempotent; run before city GLB export.
"""
import sys,json,math,shutil
from pathlib import Path
import numpy as np
OUT=Path('build/geographic-strip');backup=Path('build/resort-blocks/bellagio/south-arrival-before');backup.mkdir(exist_ok=True)
# Only the south-entry roads. The Strip main carriageways lie east of x=-22.
planes=[(-1,0,0,-222),(1,0,0,22),(0,0,-1,398),(0,0,1,-595),(0,1,0,-9),(0,-1,0,-.2)]
def cut(tri):
 a=np.array(tri,float)
 if a[:,0].max()<=-222 or a[:,0].min()>=-22 or a[:,2].max()<=398 or a[:,2].min()>=595 or a[:,1].min()>9:return None
 remaining=list(a);result=[]
 for nx,ny,nz,c in planes:
  inside=[];outside=[]
  for p,q in zip(remaining,remaining[1:]+remaining[:1]):
   dp=nx*p[0]+ny*p[1]+nz*p[2]+c;dq=nx*q[0]+ny*q[1]+nz*q[2]+c
   (inside if dp<=1e-7 else outside).append(p)
   if dp*dq<0:
    v=p+(q-p)*(dp/(dp-dq));inside.append(v);outside.append(v)
  if len(outside)>=3:
   for i in range(1,len(outside)-1):
    t=[outside[0],outside[i],outside[i+1]]
    if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>1e-8:result.append([p.tolist() for p in t])
  remaining=inside
  if len(remaining)<3:break
 if not remaining:return None
 return result
p=OUT/'city-meshes.json'
if not (backup/p.name).exists():shutil.copyfile(p,backup/p.name)
groups=json.loads(p.read_text());visual=0
for g in groups:
 mat=g['material'];building=mat.startswith(('building','tag/')) or mat=='utility'
 v=g['vertices'];faces=[]
 for f in g['faces']:
  tri=[v[i] for i in f]
  # Preserve taller building blocks and the existing arrival canopy. Only low
  # mapped covered-walkway placeholders in the southern strip are replaced.
  if building and (max(p[1] for p in tri)>6 or min(p[2] for p in tri)<521):faces.append(f);continue
  pieces=cut(tri)
  if pieces is None:faces.append(f);continue
  visual+=1
  for t in pieces:n=len(v);v.extend(t);faces.append([n,n+1,n+2])
 g['faces']=faces
p.write_text(json.dumps(groups,separators=(',',':')))
p=OUT/'city-colliders.json'
if not (backup/p.name).exists():shutil.copyfile(p,backup/p.name)
cells=json.loads(p.read_text());physics=0
for cell in cells:
 x,z=cell['center']
 if x+80<-222 or x-80>-22 or z+80<398 or z-80>595:continue
 v=cell['vertices'];idx=[]
 for i in range(0,len(cell['indices']),3):
  f=cell['indices'][i:i+3];tri=[v[j*3:j*3+3] for j in f]
  # Other structures are above this replacement's ceiling. Low terrain/roads
  # and the old five-metre walkway boxes in this zone are fully replaced.
  pieces=cut(tri)
  if pieces is None:idx.extend(f);continue
  physics+=1
  for t in pieces:n=len(v)//3;v.extend(x for p in t for x in p);idx.extend([n,n+1,n+2])
 cell['indices']=idx
p.write_text(json.dumps(cells,separators=(',',':')))
report=Path('build/resort-blocks/bellagio/south-arrival-cut.json')
if visual or physics or not report.exists():report.write_text(json.dumps(dict(visualFacesCut=visual,collisionFacesCut=physics,region=[-222,398,-22,595],verticalRange=[-.2,9]),indent=2))
print('Bellagio arrival cut',visual,physics)
