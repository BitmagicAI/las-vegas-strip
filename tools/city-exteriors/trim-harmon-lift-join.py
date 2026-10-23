"""Open only the old bridge railing across the restored mapped Harmon span.
No deck, ground, road or building geometry is changed.
"""
import sys,json,shutil,math
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks');from common import np
root=Path('build/geographic-strip');bak=Path('.bitmagic/city-exterior-backups/harmon-lift-join-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
for n in ['city-meshes.json','city-colliders.json']:
 if not(bak/n).exists():shutil.copy2(root/n,bak/n)
# Along the mapped centerline, extended just beyond the join at both ends.
a=np.array([73.37,846.98]);t=np.array([1.59,-11.85]);t/=np.linalg.norm(t);n=np.array([-t[1],t[0]])
planes=[(np.array([n[0],0,n[1]]),float(a@n-1.9)),(-np.array([n[0],0,n[1]]),float(-a@n-1.9)),(np.array([t[0],0,t[1]]),float(a@t-5)),(-np.array([t[0],0,t[1]]),float(-a@t-14)),(np.array([0,1,0]),6.1), (np.array([0,-1,0]),-7.4)]
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
def near(q):return min(v[0]for v in q)<79 and max(v[0]for v in q)>70 and min(v[2]for v in q)<853 and max(v[2]for v in q)>832 and min(v[1]for v in q)>6.1 and max(v[1]for v in q)<7.4
def key(q):return tuple(sorted(tuple(round(v,4)for v in p)for p in q))
gs=json.loads((bak/'city-meshes.json').read_text());replaced={};counts={}
for g in gs:
 if g['material']not in ['bridge-metal','bridge-glass']:continue
 old=g['vertices'];keep=[]
 for f in g['faces']:
  q=[old[i]for i in f]
  if not near(q):keep.append(f);continue
  pieces=outside(q)
  if len(pieces)==1 and key(pieces[0])==key(q):keep.append(f);continue
  replaced[key(q)]=pieces;counts[g['material']]=counts.get(g['material'],0)+1
  for tri in pieces:k=len(old);old.extend(tri);keep.append([k,k+1,k+2])
 g['faces']=keep
(root/'city-meshes.json').write_text(json.dumps(gs,separators=(',',':')))
cs=json.loads((bak/'city-colliders.json').read_text());count=0
for c in cs:
 v=c['vertices'];keep=[]
 for i in range(0,len(c['indices']),3):
  idx=c['indices'][i:i+3];q=[v[j*3:j*3+3]for j in idx];pieces=replaced.get(key(q))
  if pieces is None:keep.extend(idx);continue
  count+=1
  for tri in pieces:k=len(v)//3;v.extend(c for p in tri for c in p);keep.extend([k,k+1,k+2])
 c['indices']=keep
(root/'city-colliders.json').write_text(json.dumps(cs,separators=(',',':')))
report=dict(railFacesClipped=counts,collisionFacesClipped=count,scope='Existing bridge rails only within restored Harmon span clear width at north join.')
Path('build/city-exteriors/harmon-east-lift-join-trim.json').write_text(json.dumps(report,indent=2));print(report)
