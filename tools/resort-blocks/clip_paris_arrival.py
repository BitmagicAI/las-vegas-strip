"""Subtract the new motor court from retained Paris geometry, UVs and collision.
Only Paris nodes are edited; all other mesh/image buffer payloads are preserved.
The convex half-space clip also interpolates texture coordinates and normals.
"""
import json,struct,sys,math,copy
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from paris_arrival import arrival_void,CX,CZ,R
OUT=Path('build/resort-blocks/paris');base=OUT/'arrival-before';base.mkdir(exist_ok=True)
files=['build/geographic-strip/detailed.glb','src/work/geographic/level.json']
for path in files:
 p=Path(path);dest=base/p.name
 if not dest.exists():dest.write_bytes(p.read_bytes())
# Repeated installs use the current file; a version marker prevents buffer growth.
p=Path(files[0]);raw=p.read_bytes();ln=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+ln]);buf=bytearray(raw[28+ln:]);version='paris-arrival-2026-10-05-v2'
cut=arrival_void();entry=box(CX-4.3,CZ-R-11.2,CX+4.3,CZ-R+.3)
regions=[(cut,.10,27),(entry,.10,8.5)]
def planes(poly,lo,hi):
 pts=list(poly.exterior.coords)[:-1]
 if not poly.exterior.is_ccw:pts=pts[::-1]
 q=[(0,-1,0,lo),(0,1,0,-hi)]
 for a,b in zip(pts,pts[1:]+pts[:1]):
  dx,dz=b[0]-a[0],b[1]-a[1];q.append((dz,0,-dx,dx*a[1]-dz*a[0]))
 return q
cuts=[(poly,lo,hi,planes(poly,lo,hi)) for poly,lo,hi in regions]
def split(poly,plane):
 out=[];inside=[];nx,ny,nz,c=plane
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=nx*a[0]+ny*a[1]+nz*a[2]+c;db=nx*b[0]+ny*b[1]+nz*b[2]+c
  (inside if da<=1e-7 else out).append(a)
  if da*db<0:
   t=da/(da-db);v=a+(b-a)*t;inside.append(v);out.append(v)
 return inside,out

def clip(poly):
 result=[poly]
 for region,lo,hi,planes0 in cuts:
  nextparts=[]
  for poly in result:
   pp=np.array(poly);xz=Polygon(pp[:,[0,2]]) if abs(np.cross(pp[1,:3]-pp[0,:3],pp[2,:3]-pp[0,:3])[1])>1e-8 else LineString(pp[:,[0,2]])
   if pp[:,1].max()<lo or pp[:,1].min()>hi or not region.intersects(xz):nextparts.append(poly);continue
   remain=poly
   for plane in planes0:
    if len(remain)<3:break
    remain,outside=split(remain,plane)
    if len(outside)>=3:nextparts.append(outside)
  result=nextparts
 return result

dtypes={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32};ncomp={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def read(aid):
 a=j['accessors'][aid];v=j['bufferViews'][a['bufferView']];dt=np.dtype(dtypes[a['componentType']]);c=ncomp[a['type']];stride=v.get('byteStride',dt.itemsize*c);off=v.get('byteOffset',0)+a.get('byteOffset',0)
 return np.ndarray((a['count'],c),dtype=dt,buffer=buf,offset=off,strides=(stride,dt.itemsize)).copy()
def write(arr,template,target):
 arr=np.ascontiguousarray(arr);buf.extend(b'\0'*((-len(buf))%4));off=len(buf);buf.extend(arr.tobytes());v=len(j['bufferViews']);j['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=arr.nbytes,target=target));a=copy.deepcopy(template);a.update(bufferView=v,byteOffset=0,count=len(arr));a.pop('sparse',None)
 if 'min' in a:a['min']=arr.min(axis=0).tolist();a['max']=arr.max(axis=0).tolist()
 aid=len(j['accessors']);j['accessors'].append(a);return aid
changed=0;removed=0
if j.get('extras',{}).get('parisArrivalClip')!=version:
 for node in j['nodes']:
  if node.get('extras',{}).get('geographicOwner')!='paris' or 'mesh' not in node:continue
  assert not any(k in node for k in ['matrix','translation','rotation','scale']),node['name']
  mesh=copy.deepcopy(j['meshes'][node['mesh']]);newprims=[]
  for prim in mesh['primitives']:
   attrs=prim['attributes'];keys=['POSITION']+[k for k in attrs if k!='POSITION'];arrays=[read(attrs[k]) for k in keys];widths=[a.shape[1] for a in arrays];rows=np.concatenate(arrays,axis=1).astype(float);ix=read(prim['indices']).reshape(-1,3);verts=[];touched=0
   for ids in ix:
    tri=list(rows[ids]);pieces=clip(tri)
    if len(pieces)!=1 or len(pieces[0])!=3 or not np.array_equal(np.array(pieces[0]),np.array(tri)):touched+=1
    for frag in pieces:
     for i in range(1,len(frag)-1):
      a,b,c=frag[0],frag[i],frag[i+1]
      if np.linalg.norm(np.cross(b[:3]-a[:3],c[:3]-a[:3]))>1e-7:verts.extend([a,b,c])
   if not touched:newprims.append(prim);continue
   changed+=1;removed+=touched
   if not verts:continue
   out=np.array(verts);at=0
   for key,width,arr in zip(keys,widths,arrays):
    part=out[:,at:at+width];at+=width
    if key=='NORMAL':part=part/np.maximum(np.linalg.norm(part,axis=1,keepdims=True),1e-10)
    prim['attributes'][key]=write(part.astype(arr.dtype),j['accessors'][attrs[key]],34962)
   prim['indices']=write(np.arange(len(out),dtype=np.uint32).reshape(-1,1),dict(componentType=5125,type='SCALAR'),34963);newprims.append(prim)
  mesh['primitives']=newprims
  if newprims:node['mesh']=len(j['meshes']);j['meshes'].append(mesh)
  else:node.pop('mesh',None)
 j.setdefault('extras',{})['parisArrivalClip']=version;j['buffers'][0]['byteLength']=len(buf);buf.extend(b'\0'*((-len(buf))%4));s=json.dumps(j,separators=(',',':')).encode();s+=b' '*((-len(s))%4)
 p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(s)+len(buf))+struct.pack('<II',len(s),0x4e4f534a)+s+struct.pack('<II',len(buf),0x004e4942)+buf)
# Existing colliders are metre-space convex prisms. Subtract the same plan void;
# triangulated fragments are a bounded number of rigid static pieces, not props.
data=json.load(open(files[1]));cols=[];count=0
for col in data['colliders']:
 if 'paris' not in col['name'].lower() or '/ court clipped' in col['name']:cols.append(col);continue
 v=np.array(col.get('vertices',[])).reshape(-1,3)
 if not len(v):cols.append(col);continue
 if col['shape']=='trimesh':
  vs=[]
  for ids in np.array(col['indices']).reshape(-1,3):
   for frag in clip(list(v[ids])):
    for k in range(1,len(frag)-1):vs.extend([frag[0],frag[k],frag[k+1]])
  if vs:cols.append(dict(col,vertices=np.array(vs).flatten().tolist(),indices=list(range(len(vs))),name=col['name']+' / court clipped'))
  continue
 lo,hi=v[:,1].min(),v[:,1].max();poly=Polygon(v[:,[0,2]]).convex_hull
 if hi<.1 or lo>27 or not any(poly.intersects(q[0]) for q in regions):cols.append(col);continue
 # All intersecting existing solid boxes are vertical prisms. Preserve their
 # heights; existing stair/guest geometry does not enter this arrival volume.
 remaining=poly
 for region,low,high in regions:
  if lo<high and hi>low:remaining=remaining.difference(region)
 if remaining.equals(poly):cols.append(col);continue
 count+=1
 for piece in parts(remaining):
  for tri in triangles(piece):
   coords=list(tri.exterior.coords)[:-1];vv=[a for y in [lo,hi] for x,z in coords for a in [x,y,z]]
   cols.append(dict(col,vertices=vv,name=col['name']+' / court clipped'))
seen={}
for col in cols:
 name=col['name'];seen[name]=seen.get(name,0)+1
 if seen[name]>1:col['name']=name+' '+str(seen[name])
data['colliders']=cols;data['lights']=[l for l in data['lights'] if not ('paris' in l['name'].lower() and cut.contains(Point(l['position'][0],l['position'][2])))]
for path in [files[1],'build/geographic-strip/detailed.mesh-level.json']:Path(path).write_text(json.dumps(data,indent=2)+'\n')
# The motor court must not inherit the old rectangular indoor culling volume.
p=Path('src/work/vegas-visibility.json');m=json.loads(p.read_text());m['exteriorVoids']=[v for v in m.get('exteriorVoids',[]) if v['id']!='paris-arrival'];m['exteriorVoids'].append(dict(id='paris-arrival',building='paris',center=[CX,CZ],radius=R+.05,minY=.1,maxY=27))
# The glazed vestibule must retain the outdoor view even while its doors close.
center=[CX,3.65,CZ-R-5.5];size=[8.4,7.3,11.4]
m['zones']=[v for v in m['zones'] if v['id']!='paris-arrival-vestibule']
m['zones'].insert(0,dict(id='paris-arrival-vestibule',name='Paris main entrance vestibule',building='paris',center=center,size=size,yaw=0,windowed=True,arrival=True,room=False,corridor=False,sourceCenter=center,sourceSize=size,sourceYaw=0,geoTransform=dict(key='paris-arrival',source=[0,0,1,1],target=[0,0,1,1],osm=[],linear=[1,0,0,1],translation=[0,0],heightScale=1)))
p.write_text(json.dumps(m,indent=2)+'\n')
report=dict(version=version,affectedPrimitives=changed,affectedTriangles=removed,affectedColliders=count,voidCenter=[CX,CZ],radius=R+.05)
if changed or count or not (OUT/'arrival-cut-report.json').exists():(OUT/'arrival-cut-report.json').write_text(json.dumps(report,indent=2))
print(report)
