"""Remove only obsolete elevated walkway kits inside the authored Mandalay private pool court court."""
import sys,json,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
root=Path('build/geographic-strip');backup=Path('.bitmagic/city-exterior-backups/mandalay-pool-paths-2026-10-14');backup.mkdir(exist_ok=True)
from mandalay_pool_detail import plans
mask=unary_union([p for r,p in plans() if r['id'] not in ['way/128158102','way/116660352','way/399554380']]).convex_hull.buffer(45,join_style=2);ps=list(mask.exterior.coords);center=mask.centroid;planes=[]
for a,b in zip(ps,ps[1:]):
 nx,nz=b[1]-a[1],a[0]-b[0];c=-nx*a[0]-nz*a[1]
 if nx*center.x+nz*center.y+c>0:nx,nz,c=-nx,-nz,-c
 planes.append((nx,nz,c))
def key(t):return tuple(sorted(tuple(round(float(c),4) for c in v) for v in t))
def cut(t):
 if max(v[0] for v in t)<mask.bounds[0] or min(v[0] for v in t)>mask.bounds[2] or max(v[2] for v in t)<mask.bounds[1] or min(v[2] for v in t)>mask.bounds[3]:return None
 remaining=[np.array(v,float) for v in t];result=[]
 for nx,nz,c in planes:
  inside=[];outside=[]
  for p,q in zip(remaining,remaining[1:]+remaining[:1]):
   dp=nx*p[0]+nz*p[2]+c;dq=nx*q[0]+nz*q[2]+c
   (inside if dp<=1e-8 else outside).append(p)
   if dp*dq<0:
    v=p+(q-p)*dp/(dp-dq);inside.append(v);outside.append(v)
  for i in range(1,len(outside)-1):
   tri=[outside[0],outside[i],outside[i+1]]
   if np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))>1e-8:result.append([v.tolist() for v in tri])
  remaining=inside
  if len(remaining)<3:return None
 return result
for name in ['city-meshes.json','city-colliders.json']:
 if not (backup/name).exists():shutil.copy2(root/name,backup/name)
groups=json.loads((root/'city-meshes.json').read_text());replaced={};count=0
for g in groups:
 if not g['material'].startswith('bridge-'):continue
 v=g['vertices'];faces=[]
 for f in g['faces']:
  t=[v[i] for i in f];pieces=cut(t)
  if pieces is None:faces.append(f);continue
  replaced[key(t)]=pieces;count+=1
  for p in pieces:n=len(v);v.extend(p);faces.append([n,n+1,n+2])
 g['faces']=faces
(root/'city-meshes.json').write_text(json.dumps(groups,separators=(',',':')))
cells=json.loads((root/'city-colliders.json').read_text());collision=0
for cell in cells:
 v=cell['vertices'];idx=[]
 for i in range(0,len(cell['indices']),3):
  f=cell['indices'][i:i+3];t=[v[j*3:j*3+3] for j in f];pieces=replaced.get(key(t))
  if pieces is None:idx.extend(f);continue
  collision+=1
  for p in pieces:n=len(v)//3;v.extend(x for q in p for x in q);idx.extend([n,n+1,n+2])
 cell['indices']=idx
(root/'city-colliders.json').write_text(json.dumps(cells,separators=(',',':')))
r={'visualFacesClipped':count,'collisionFacesClipped':collision,'scope':'Only bridge-* material triangles inside Mandalay private pool court convex envelope; other surfaces untouched.','bounds':mask.bounds};Path('build/city-exteriors/mandalay-pool-path-cut.json').write_text(json.dumps(r,indent=2));print(r)
