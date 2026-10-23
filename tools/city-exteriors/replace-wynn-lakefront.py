"""Scoped lake restoration: remove three falsely enclosed terraces/basin and cut dry ground only inside new water."""
import sys,json,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks');from common import *
from wynn_lakefront import lake_shape
out=Path('build/geographic-strip');bak=Path('.bitmagic/city-exterior-backups/wynn-lakefront-2026-10-20');bak.mkdir(parents=True,exist_ok=True)
for name in ['city-meshes.json','city-colliders.json','building-index.json']:
 if not (bak/name).exists():shutil.copy2(out/name,bak/name)
p=unary_union([footprint(i)for i in ['way/142899192','way/142899188','way/142899193']]).buffer(.005)
water=lake_shape().union(footprint('way/142899193').buffer(-.45));wb=water.bounds
from shapely.prepared import prep
wp=prep(water)
def key(vs):return tuple(sorted(tuple(round(c,4)for c in v)for v in vs))
gs=json.loads((bak/'city-meshes.json').read_text());removed=set();clipped={};addCount=0
for g in gs:
 building=g['material'] in ('building-estimated','building-tagged','utility')or g['material'].startswith('tag/')
 ground=g['material'] in ('ground','woodland')
 if not building and not ground:continue
 keep=[];extra=[]
 for face in g['faces']:
  vs=[g['vertices'][i]for i in face]
  if building:
   if all(p.covers(Point(v[0],v[2]))for v in vs)and abs(max(v[1]for v in vs)-6)<.001 and all(abs(v[1])<.001 or abs(v[1]-6)<.001 for v in vs):removed.add(key(vs));continue
  elif max(v[1]for v in vs)<.65 and max(v[0]for v in vs)>=wb[0] and min(v[0]for v in vs)<=wb[2] and max(v[2]for v in vs)>=wb[1] and min(v[2]for v in vs)<=wb[3]:
   t=Polygon([(v[0],v[2])for v in vs])
   if t.area>.001 and wp.intersects(t):
    remain=t.difference(water);new=[]
    # Existing ground triangles are planar; preserve their exact elevation outside mask.
    A=np.array([[v[0],v[2],1]for v in vs]);coef=np.linalg.solve(A,np.array([v[1]for v in vs]))
    for q in parts(remain):
     for tri in triangles(q):
      vv=[[x,float(coef[0]*x+coef[1]*z+coef[2]),z]for x,z in list(tri.exterior.coords)[:-1]]
      if np.cross(np.array(vv[1])-vv[0],np.array(vv[2])-vv[0])[1]<0:vv.reverse()
      new.append(vv);extra.append(vv)
    clipped[key(vs)]=new;continue
  keep.append(face)
 for vv in extra:
  n=len(g['vertices']);g['vertices'].extend(vv);keep.append([n,n+1,n+2]);addCount+=1
 g['faces']=keep
assert 5<len(removed)<600,len(removed)
assert 0<len(clipped)<100,len(clipped)
(out/'city-meshes.json').write_text(json.dumps(gs,separators=(',',':')))
cs=json.loads((bak/'city-colliders.json').read_text());n=0;cut=0
for c in cs:
 v=c['vertices'];keep=[];extra=[]
 for k in range(0,len(c['indices']),3):
  tri=c['indices'][k:k+3];kk=key([v[i*3:i*3+3]for i in tri])
  if kk in removed:n+=1
  elif kk in clipped:cut+=1;extra.extend(clipped[kk])
  else:keep.extend(tri)
 for vv in extra:
  idx=len(v)//3;v.extend(a for pt in vv for a in pt);keep.extend([idx,idx+1,idx+2])
 c['indices']=keep
(out/'city-colliders.json').write_text(json.dumps(cs,separators=(',',':')))
report=dict(removed=len(removed),colliderTrianglesRemoved=n,groundClipped=len(clipped),groundColliderClipped=cut,groundReplacementTriangles=addCount,scope='Only three mapped6m shells and ground/woodland inside registered lake masks; roads and all other geometry retained.')
Path('build/city-exteriors/wynn-lakefront-ownership-audit.json').write_text(json.dumps(report,indent=2));print(report)
