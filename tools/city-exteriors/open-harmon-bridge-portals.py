"""Pierce the two mapped bridge-floor entries only, retaining all other surfaces."""
import sys,json,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks');from common import *
bak=Path('.bitmagic/city-exterior-backups/harmon-bridge-portals-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
boxes=[(71.4,79,831.5,838.7),(38.5,46,778.1,785.5)]
def clip(poly,axis,value,sign):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a[axis]-value)*sign;db=(b[axis]-value)*sign
  if da>=-1e-9:out.append(a)
  if da*db<0:out.append([a[j]+(b[j]-a[j])*da/(da-db)for j in range(3)])
 return out
def cut_box(q,rect):
 x0,x1,z0,z1=rect;pending=q;out=[]
 for axis,value,sign in [(0,x0,1),(0,x1,-1),(2,z0,1),(2,z1,-1),(1,6.09,1),(1,9.55,-1)]:
  if not pending:break
  part=clip(pending,axis,value,-sign)
  for j in range(1,len(part)-1):
   t=[part[0],part[j],part[j+1]]
   if np.linalg.norm(np.cross(np.subtract(t[1],t[0]),np.subtract(t[2],t[0])))>1e-9:out.append(t)
  pending=clip(pending,axis,value,sign)
 return out
def cut(q):
 pieces=[q]
 for rect in boxes:
  x0,x1,z0,z1=rect
  if max(p[0]for p in q)<x0 or min(p[0]for p in q)>x1 or max(p[2]for p in q)<z0 or min(p[2]for p in q)>z1 or max(p[1]for p in q)<6.09 or min(p[1]for p in q)>9.55:continue
  pieces=[t for p in pieces for t in cut_box(p,rect)]
 return pieces
def key(q):return tuple(sorted(tuple(round(v,5)for v in p)for p in q))
report={}
for owner,mfile,cfile in [('city','build/geographic-strip/city-meshes.json','build/geographic-strip/city-colliders.json'),('planetHollywood','build/strip-landmarks/planetHollywood-exterior.json','build/strip-landmarks/planetHollywood-exterior-collision.json')]:
 if '--planet-only' in sys.argv and owner=='city':continue
 for file in [mfile,cfile]:
  f=Path(file);target=bak/f.name
  if not target.exists():shutil.copy2(f,target)
 d=json.loads(Path(mfile).read_text());groups=d if owner=='city'else d['meshes'];n=0
 for g in groups:
  if owner=='city'and g['material']not in ['building-estimated','building-tagged','bridge-metal','bridge-glass']:continue
  if owner!='city'and g['source'].split('@')[0]!='harmon-corner':continue
  vs=g['vertices'];faces=[]
  for f in g['faces']:
   q=[vs[i]for i in f];pieces=cut(q)
   if len(pieces)==1 and key(pieces[0])==key(q):faces.append(f);continue
   n+=1
   for t in pieces:k=len(vs);vs.extend(t);faces.append([k,k+1,k+2])
  g['faces']=faces
 Path(mfile).write_text(json.dumps(d,separators=(',',':')))
 c=json.loads(Path(cfile).read_text());cs=c if isinstance(c,list)else[c];nc=0
 for row in cs:
  v=row['vertices'];idx=[]
  for i in range(0,len(row['indices']),3):
   tri=row['indices'][i:i+3];q=[v[j*3:j*3+3]for j in tri];pieces=cut(q)
   if len(pieces)==1 and key(pieces[0])==key(q):idx.extend(tri);continue
   nc+=1
   for t in pieces:k=len(v)//3;v.extend(a for p in t for a in p);idx.extend([k,k+1,k+2])
  row['indices']=idx
 Path(cfile).write_text(json.dumps(c,separators=(',',':')));report[owner]={'visualFacesCut':n,'collisionFacesCut':nc}
Path('build/city-exteriors/harmon-bridge-portals-cut.json').write_text(json.dumps(report,indent=2));print(report)
