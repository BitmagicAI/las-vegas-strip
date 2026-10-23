"""Current-data replacement of legacy decorative south facade only.
Preserves room/interior meshes and ALL collision; backup is never an input.
"""
import sys,struct,json,hashlib,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import np
P=Path('build/geographic-strip/detailed.glb')
limits=[(0,85.27,1),(0,206.58,-1),(1,.12,1),(1,12.5,-1),(2,301.95,1),(2,303.0,-1)]
def clip(ws,vs,axis,value,sign):
 out=[]
 for a,b in zip(ws,ws[1:]+ws[:1]):
  da=((a@vs)[axis]-value)*sign;db=((b@vs)[axis]-value)*sign
  if da>=-1e-9:out.append(a)
  if da*db<0:out.append(a+(b-a)*da/(da-db))
 return out

def outside(vs):
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

raw=P.read_bytes();backup=Path('.bitmagic/city-exterior-backups/versailles-south-2026-10-22');backup.mkdir(parents=True,exist_ok=True)
if not(backup/P.name).exists():shutil.copy2(P,backup/P.name)
n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);buf=bytearray(raw[28+n:]);report=[]
dtypes={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1',5122:'<i2',5120:'i1'};sizes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def read(ai):
 a=j['accessors'][ai];v=j['bufferViews'][a['bufferView']];dt=np.dtype(dtypes[a['componentType']]);s=sizes[a['type']]
 return np.ndarray((a['count'],s),dtype=dt,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dt.itemsize*s),dt.itemsize)).copy()
def write(arr,template):
 arr=np.ascontiguousarray(arr);buf.extend(b'\0'*(-len(buf)%4));off=len(buf);buf.extend(arr.tobytes());vi=len(j['bufferViews']);j['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=arr.nbytes));a={k:v for k,v in template.items()if k not in ['bufferView','byteOffset','min','max','count','sparse']};a.update(bufferView=vi,count=len(arr));a['min']=arr.min(0).tolist();a['max']=arr.max(0).tolist();ai=len(j['accessors']);j['accessors'].append(a);return ai
for nd in j['nodes']:
 e=nd.get('extras',{});name=nd.get('name','')
 if e.get('geographicOwner')!='horseshoe'or e.get('visibilityKind')not in ['shell','outside']or'mesh'not in nd:continue
 if not any(k in name for k in ['rx_gold','rx_limestone','rx_blueglass']):continue
 assert not any(k in nd for k in ['matrix','translation','rotation','scale'])
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
  report.append(dict(node=name,changedTriangles=changed,before=len(idx),after=len(keep)))
  if not keep:prim['_remove']=True;continue
  for k,arr in attrs.items():
   if extra[k]:prim['attributes'][k]=write(np.vstack([arr,np.array(extra[k],dtype=arr.dtype)]),j['accessors'][prim['attributes'][k]])
  prim['indices']=write(np.array(keep,dtype='<u4').reshape(-1,1),dict(componentType=5125,type='SCALAR'))
 mesh=j['meshes'][nd['mesh']];mesh['primitives']=[q for q in mesh['primitives']if not q.pop('_remove',False)]
 if not mesh['primitives']:nd.pop('mesh')
if report:
 j['buffers'][0]['byteLength']=len(buf);buf.extend(b'\0'*(-len(buf)%4));data=json.dumps(j,separators=(',',':')).encode();data+=b' '*(-len(data)%4);P.write_bytes(struct.pack('<III',0x46546c67,2,28+len(data)+len(buf))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(buf),0x004e4942)+buf)
 rev=hashlib.sha256(P.read_bytes()).hexdigest()[:16]
 for f in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(f).write_text(json.dumps({'revision':rev}))
Path('build/city-exteriors/versailles-south-cut.json').write_text(json.dumps({'changed':report,'collision':'unchanged','bounds':[85.27,.12,301.95,206.58,12.5,303]},indent=2));print(report)
