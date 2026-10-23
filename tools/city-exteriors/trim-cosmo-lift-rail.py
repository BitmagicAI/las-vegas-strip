"""Remove the retained cosmetic railing across the mapped Cosmopolitan lift door."""
import sys,json,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks');from common import np
root=Path('build/resort-blocks/cosmo');bak=Path('.bitmagic/city-exterior-backups/cosmo-lift-rail-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
for n in ['cosmo-exterior.json','cosmo-exterior-collision.json']:
 if not(bak/n).exists():shutil.copy2(root/n,bak/n)
planes=[(np.array([1,0,0]),-51.7),(np.array([-1,0,0]),50.85),(np.array([0,0,1]),741.10),(np.array([0,0,-1]),-743.0),(np.array([0,1,0]),6.10),(np.array([0,-1,0]),-7.5)]
def clip(poly,n,d):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=float(np.dot(a,n)-d);db=float(np.dot(b,n)-d)
  if da>=-1e-8:out.append(a)
  if da*db<0:out.append([a[j]+(b[j]-a[j])*da/(da-db)for j in range(3)])
 return out
def outside(q):
 pending=q;out=[]
 for n,d in planes:
  if not pending:break
  part=clip(pending,-n,-d)
  for j in range(1,len(part)-1):
   tri=[part[0],part[j],part[j+1]]
   if np.linalg.norm(np.cross(np.subtract(tri[1],tri[0]),np.subtract(tri[2],tri[0])))>1e-8:out.append(tri)
  pending=clip(pending,n,d)
 return out
def near(q):return min(v[0]for v in q)<-50.85 and max(v[0]for v in q)>-51.7 and min(v[2]for v in q)<743 and max(v[2]for v in q)>741.1 and min(v[1]for v in q)>6.1 and max(v[1]for v in q)<7.5
def key(q):return tuple(sorted(tuple(round(v,5)for v in p)for p in q))
f=root/'cosmo-exterior.json';d=json.loads(f.read_text());n=0
for g in d['meshes']:
 if g['source']!='bridge-landings' or g['material']!='steel':continue
 v=g['vertices'];faces=[]
 for face in g['faces']:
  q=[v[i]for i in face]
  if not near(q):faces.append(face);continue
  pieces=outside(q)
  if len(pieces)==1 and key(pieces[0])==key(q):faces.append(face);continue
  n+=1
  for tri in pieces:i=len(v);v.extend(tri);faces.append([i,i+1,i+2])
 g['faces']=faces
f.write_text(json.dumps(d,separators=(',',':')))
Path('build/city-exteriors/cosmo-lift-rail-cut.json').write_text(json.dumps({'railTrianglesClipped':n,'collisionChanged':False,'scope':'Cosmopolitan bridge-landings steel only, 1.9m clear doorway slot; old rail had no collision'},indent=2));print('RAIL CUT',n)
