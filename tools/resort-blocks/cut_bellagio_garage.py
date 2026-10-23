"""Replace only the mapped parking block and its side access road, including collision."""
import json,math,shutil
from pathlib import Path
import numpy as np
OUT=Path('build/geographic-strip');backup=Path('build/resort-blocks/bellagio/garage-before');backup.mkdir(exist_ok=True)
BOXES=[(-374.6,-191.9,488.9,563.8),(-377,-210,563.8,581)]
def cut(tri,bounds):
 x0,x1,z0,z1=bounds;a=np.array(tri,float)
 if a[:,0].max()<x0 or a[:,0].min()>x1 or a[:,2].max()<z0 or a[:,2].min()>z1 or a[:,1].min()>12.6 or a[:,1].max()<-.05:return [tri]
 remaining=list(a);result=[]
 for nx,ny,nz,c in [(-1,0,0,x0),(1,0,0,-x1),(0,0,-1,z0),(0,0,1,-z1),(0,1,0,-12.6),(0,-1,0,-.05)]:
  inside=[];outside=[]
  for p,q in zip(remaining,remaining[1:]+remaining[:1]):
   dp=nx*p[0]+ny*p[1]+nz*p[2]+c;dq=nx*q[0]+ny*q[1]+nz*q[2]+c
   (inside if dp<=1e-7 else outside).append(p)
   if dp*dq<0:v=p+(q-p)*(dp/(dp-dq));inside.append(v);outside.append(v)
  if len(outside)>=3:
   for i in range(1,len(outside)-1):
    t=[outside[0],outside[i],outside[i+1]]
    if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>1e-8:result.append([p.tolist() for p in t])
  remaining=inside
  if len(remaining)<3:return result
 return result
def pieces(tri):
 result=[tri]
 for bounds in BOXES:result=[p for t in result for p in cut(t,bounds)]
 return result
for name in ['city-meshes.json','city-colliders.json']:
 p=OUT/name
 if not (backup/name).exists():shutil.copy2(p,backup/name)
 groups=json.loads(p.read_text());count=0
 for g in groups:
  flat='indices' in g;v=g['vertices'];faces=[g['indices'][i:i+3] for i in range(0,len(g['indices']),3)] if flat else g['faces'];new=[]
  for f in faces:
   tri=[v[i*3:i*3+3] if flat else v[i] for i in f]
   if max(t[0] for t in tri)<-377 or min(t[0] for t in tri)>-191.9 or max(t[2] for t in tri)<488.9 or min(t[2] for t in tri)>581 or min(t[1] for t in tri)>12.6:
    new.append(f);continue
   ps=pieces(tri)
   if ps==[tri]:new.append(f);continue
   count+=1
   for t in ps:
    n=len(v)//3 if flat else len(v);v.extend([k for p in t for k in p] if flat else t);new.append([n,n+1,n+2])
  if flat:g['indices']=[i for f in new for i in f]
  else:g['faces']=new
 p.write_text(json.dumps(groups,separators=(',',':')));print(name,count,flush=True)
