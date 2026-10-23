"""Open the existing parent facade at the retained upper-gallery stair endpoint."""
import sys,json,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
limits=[(0,193.4,1),(0,197.2,-1),(2,21.9,1),(2,24.0,-1),(1,5.88,1),(1,8.8,-1)]
def clip(ws,vs,axis,value,sign):
 out=[]
 for a,b in zip(ws,ws[1:]+ws[:1]):
  da=((a@vs)[axis]-value)*sign;db=((b@vs)[axis]-value)*sign
  if da>=-1e-9:out.append(a)
  if da*db<0:out.append(a+(b-a)*da/(da-db))
 return out

def outside_one(vs,limits):
 if any(np.max((vs[:,a]-v)*s)<-1e-8 for a,v,s in limits):return None
 pending=list(np.eye(3));out=[]
 for a,v,s in limits:
  if not pending:break
  part=clip(pending,vs,a,v,-s)
  for i in range(1,len(part)-1):
   w=np.array([part[0],part[i],part[i+1]]);q=w@vs
   if np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))>1e-9:out.append(w)
  pending=clip(pending,vs,a,v,s)
 if len(pending)<3:return None
 q=np.array(pending)@vs
 if sum(np.linalg.norm(np.cross(q[i]-q[0],q[i+1]-q[0]))for i in range(1,len(q)-1))<1e-9:return None
 return out
def outside(vs):
 openings=[limits,[(0,193.4,1),(0,197.2,-1),(2,8.25,1),(2,9.15,-1),(1,.12,1),(1,3.4,-1)]]
 polys=[np.eye(3)];changed=False
 for opening in openings:
  nxt=[]
  for w in polys:
   pieces=outside_one(w@vs,opening)
   if pieces is None:nxt.append(w)
   else:changed=True;nxt.extend(q@w for q in pieces)
  polys=nxt
 return polys if changed else None
bak=Path('.bitmagic/city-exterior-backups/flamingo-gallery-door-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
p=Path('build/strip-landmarks/flamingoExterior-exterior.json');pc=p.with_name('flamingoExterior-exterior-collision.json')
for f in [p,pc]:
 if not(bak/f.name).exists():shutil.copy2(f,bak/f.name)
d=json.loads(p.read_text());report=[]
for g in d['meshes']:
 if g.get('source')!='flamingo-podium':continue
 keep=[];changed=0;v=g['vertices']
 for f in g['faces']:
  vs=np.array([v[i]for i in f]);pieces=outside(vs)
  if pieces is None:keep.append(f);continue
  changed+=1
  for w in pieces:n=len(v);v.extend((w@vs).tolist());keep.append([n,n+1,n+2])
 g['faces']=keep
 if changed:report.append(dict(material=g['material'],triangles=changed))
p.write_text(json.dumps(d,separators=(',',':')))
d=json.loads(pc.read_text());v=d['vertices'];keep=[];changed=0
for i in range(0,len(d['indices']),3):
 f=d['indices'][i:i+3];vs=np.array([v[k*3:k*3+3]for k in f]);pieces=outside(vs)
 if pieces is None:keep.extend(f);continue
 changed+=1
 for w in pieces:n=len(v)//3;v.extend((w@vs).ravel().tolist());keep.extend([n,n+1,n+2])
d['indices']=keep;pc.write_text(json.dumps(d,separators=(',',':')))
r=dict(visual=report,collisionTriangles=changed,openings=[[193.4,5.88,21.9,197.2,8.8,24.0],[193.4,.12,8.25,197.2,3.4,9.15]]);Path('build/city-exteriors/flamingo-gallery-door.json').write_text(json.dumps(r,indent=2));print(r)
