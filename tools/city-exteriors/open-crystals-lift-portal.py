"""Open only the mapped upper Crystals lift approach in retained geometry.
Keeps current GLB buffers/material attributes and unrelated interiors intact.
"""
import sys,json,struct,hashlib,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
p=Path('build/geographic-strip/detailed.glb');level=Path('src/work/geographic/level.json')
bak=Path('.bitmagic/city-exterior-backups/crystals-lift-portal-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
for f in [p,level]:
 if not(bak/f.name).exists():shutil.copy2(f,bak/f.name)
raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);buf=bytearray(raw[28+n:]);report=[]
# Aperture along mapped way1436769028. Bottom retains the gallery floor6.15m.
limits=[(0,-48.1,1),(0,-40.4,-1),(2,844.6,1),(2,848.7,-1),(1,6.02,1),(1,8.65,-1)]
def clipped(weights,vs,axis,value,sign):
 out=[]
 for a,b in zip(weights,weights[1:]+weights[:1]):
  da=((a@vs)[axis]-value)*sign;db=((b@vs)[axis]-value)*sign
  if da>=-1e-9:out.append(a)
  if da*db<0:out.append(a+(b-a)*da/(da-db))
 return out

def outside(vs):
 if np.ptp(vs[:,1])<.002 and 5.5<vs[:,1].mean()<6.16:return None
 # Fast reject avoids changing any triangle not touching the doorway volume.
 for axis,value,sign in limits:
  if max((q[axis]-value)*sign for q in vs)<-1e-8:return None
 pending=list(np.eye(3));out=[]
 for axis,value,sign in limits:
  if not pending:break
  part=clipped(pending,vs,axis,value,-sign)
  for i in range(1,len(part)-1):
   w=np.array([part[0],part[i],part[i+1]]);v=w@vs
   if np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))>1e-9:out.append(w)
  pending=clipped(pending,vs,axis,value,sign)
 if len(pending)<3:return None
 v=np.array(pending)@vs
 if sum(np.linalg.norm(np.cross(v[i]-v[0],v[i+1]-v[0]))for i in range(1,len(v)-1))<1e-9:return None
 return out
dtypes={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1',5122:'<i2',5120:'i1'}
sizes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def read(ai):
 a=j['accessors'][ai];v=j['bufferViews'][a['bufferView']];dt=np.dtype(dtypes[a['componentType']]);s=sizes[a['type']]
 return np.ndarray((a['count'],s),dtype=dt,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dt.itemsize*s),dt.itemsize)).copy()
def write(arr,template):
 arr=np.ascontiguousarray(arr);buf.extend(b'\0'*(-len(buf)%4));off=len(buf);buf.extend(arr.tobytes());vi=len(j['bufferViews']);j['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=arr.nbytes));a={k:v for k,v in template.items() if k not in ['bufferView','byteOffset','min','max','count','sparse']};a.update(bufferView=vi,count=len(arr));a['min']=arr.min(0).tolist();a['max']=arr.max(0).tolist();ai=len(j['accessors']);j['accessors'].append(a);return ai
for nd in j['nodes']:
 e=nd.get('extras',{})
 if e.get('geographicOwner')!='crystals' or 'mesh' not in nd:continue
 for prim in j['meshes'][nd['mesh']]['primitives']:
  attrs={k:read(v)for k,v in prim['attributes'].items()};pos=attrs['POSITION'];idx=read(prim['indices']).ravel().reshape(-1,3);keep=[];extra={k:[]for k in attrs};changed=0
  for face in idx:
   vs=pos[face].astype(float);pieces=outside(vs)
   if pieces is None:keep.append(face.tolist());continue
   changed+=1
   for weights in pieces:
    indices=[]
    for w in weights:
     indices.append(len(pos)+len(extra['POSITION']))
     for k,arr in attrs.items():
      v=w@arr[face]
      if k=='NORMAL':v/=max(np.linalg.norm(v),1e-12)
      if arr.dtype.kind in 'iu':v=np.rint(v)
      extra[k].append(v)
    keep.append(indices)
  if not changed:continue
  report.append(dict(node=nd['name'],changedTriangles=changed,before=len(idx),after=len(keep)))
  if not keep:prim['_remove']=True;continue
  for k,arr in attrs.items():
   if extra[k]:prim['attributes'][k]=write(np.vstack([arr,np.array(extra[k],dtype=arr.dtype)]),j['accessors'][prim['attributes'][k]])
  prim['indices']=write(np.array(keep,dtype='<u4').reshape(-1,1),dict(componentType=5125,type='SCALAR'))
 mesh=j['meshes'][nd['mesh']];mesh['primitives']=[x for x in mesh['primitives']if not x.pop('_remove',False)]
 if not mesh['primitives']:nd.pop('mesh')
if report:
 j['buffers'][0]['byteLength']=len(buf);buf.extend(b'\0'*(-len(buf)%4));data=json.dumps(j,separators=(',',':')).encode();data+=b' '*(-len(data)%4);p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(data)+len(buf))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(buf),0x004e4942)+buf)
 rev=hashlib.sha256(p.read_bytes()).hexdigest()[:16]
 for f in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(f).write_text(json.dumps({'revision':rev}))
d=json.loads(level.read_text());collision=[]
for c in d['colliders']:
 if 'Crystals'not in c.get('name','') or not c.get('vertices'):continue
 v=c['vertices'];keep=[];changed=0
 for i in range(0,len(c['indices']),3):
  face=c['indices'][i:i+3];vs=np.array([v[k*3:k*3+3]for k in face]);pieces=outside(vs)
  if pieces is None:keep.extend(face);continue
  changed+=1
  for w in pieces:
   n=len(v)//3;v.extend((w@vs).ravel().tolist());keep.extend([n,n+1,n+2])
 c['indices']=keep
 if changed:collision.append(dict(name=c['name'],changedTriangles=changed))
level.write_text(json.dumps(d,separators=(',',':')))
r=dict(visual=report,collision=collision,scope='Crystals mapped upper lift doorway and short approach only; retained gallery floor, unrelated interior geometry and finishes untouched')
Path('build/city-exteriors/crystals-lift-portal-cut.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
