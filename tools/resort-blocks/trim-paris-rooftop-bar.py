"""Remove whole displaced furniture; cut rails at real pavilion boundaries.
Existing floors, facades and interiors are retained. Idempotent on current data.
"""
from pathlib import Path
import json,shutil,sys,ast
sys.path.insert(0,'tools/strip-landmarks');from common import *
root=Path('build/resort-blocks/paris');backup=Path('.bitmagic/city-exterior-backups/paris-rooftop-bar-2026-10-21');backup.mkdir(parents=True,exist_ok=True)
paths=[root/'parisBlock-exterior.json',root/'parisBlock-exterior-collision.json']
for p in paths:
 if not (backup/p.name).exists():shutil.copy2(p,backup/p.name)
def key(q):return tuple(sorted(tuple(round(v,5)for v in p)for p in q))
# Reproduce only displaced original furniture to identify all triangles of each object.
b=Meshes();G=.24;D=6.64;F=lambda x,z,y=G,yaw=0:Frame(b,x,z,yaw,y)
tree=ast.parse(Path('tools/resort-blocks/build_paris.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='table');exec(compile(ast.Module(body=[fn],type_ignores=[]),'table-definition','exec'))
for x in [41,48]:
 for z in [422,427]:table(x,z,D,'paris-red' if x==41 else None,True)
for z in [421,428]:
 for x in [37,64]:b.tube('paris-iron',(x,D,z),(x,D+4,z),.05)
 b.path('paris-iron',[(37+i*27/12,D+4-.6*math.sin(i*math.pi/12),z) for i in range(13)],.016)
 for i in range(1,12):b.sphere('warm',(37+i*27/12,D+3.96-.6*math.sin(i*math.pi/12),z),.07,6,4)
remove={key([g['vertices'][i]for i in f])for g in b.groups.values()for f in g['faces']}
# Polygon clipping preserves full rails outside the small wall intersection.
planes=[(0,41.1,1),(0,47.7,-1),(1,6.63,1),(1,8.2,-1),(2,415.5,1),(2,418,-1)]
def clip(poly,axis,value,sign):
 out=[]
 for a,c in zip(poly,poly[1:]+poly[:1]):
  da=(a[axis]-value)*sign;dc=(c[axis]-value)*sign
  if da>=-1e-9:out.append(a)
  if (da>0 and dc<0)or(da<0 and dc>0):
   t=da/(da-dc);out.append([a[j]+(c[j]-a[j])*t for j in range(3)])
 return out
def outside(q):
 pending=q;out=[]
 for axis,value,sign in planes:
  if not pending:break
  part=clip(pending,axis,value,-sign)
  if len(part)>=3:
   for j in range(1,len(part)-1):
    t=[part[0],part[j],part[j+1]]
    if np.linalg.norm(np.cross(np.subtract(t[1],t[0]),np.subtract(t[2],t[0])))>1e-9:out.append(t)
  pending=clip(pending,axis,value,sign)
 return out

d=json.loads(paths[0].read_text());counts={}
for g in d['meshes']:
 source=g['source'].split('@')[0]
 if source not in ('upper-patio-detail','podium-south-pavilion'):continue
 vs=[];fs=[]
 for f in g['faces']:
  q=[g['vertices'][i]for i in f];pieces=[q]
  if source=='upper-patio-detail' and key(q)in remove:pieces=[];counts['wholeFurniture']=counts.get('wholeFurniture',0)+1
  elif source=='podium-south-pavilion' and g['material']in('paris-iron','brass'):
   if max(p[0]for p in q)>41.1 and min(p[0]for p in q)<47.7 and max(p[2]for p in q)>415.5 and min(p[2]for p in q)<418 and max(p[1]for p in q)>6.65 and min(p[1]for p in q)<8.2:pieces=outside(q);counts['railFacesCut']=counts.get('railFacesCut',0)+1
  for t in pieces:n=len(vs);vs.extend(t);fs.append([n,n+1,n+2])
 g['vertices']=vs;g['faces']=fs
paths[0].write_text(json.dumps(d,separators=(',',':')))
c=json.loads(paths[1].read_text());v=c['vertices'];vs=[];idx=[];n=0
for j in range(0,len(c['indices']),3):
 q=[v[i*3:i*3+3]for i in c['indices'][j:j+3]];pieces=[q]
 if max(p[0]for p in q)>41.1 and min(p[0]for p in q)<47.7 and max(p[2]for p in q)>415.5 and min(p[2]for p in q)<418 and min(p[1]for p in q)>6.63 and max(p[1]for p in q)>6.65 and max(p[1]for p in q)<8.2:pieces=outside(q);n+=1
 for t in pieces:
  k=len(vs)//3;vs.extend(a for p in t for a in p);idx.extend([k,k+1,k+2])
c['vertices']=vs;c['indices']=idx;paths[1].write_text(json.dumps(c,separators=(',',':')))
report=dict(groups=counts,collisionFacesCut=n,scope='Four whole picnic sets and two whole string-light runs removed; rails clipped at pavilion walls; all floors and ground facades retained.')
Path('build/city-exteriors/paris-rooftop-parent-trim.json').write_text(json.dumps(report,indent=2));print(report)
