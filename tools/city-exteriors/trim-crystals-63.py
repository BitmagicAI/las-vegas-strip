"""Trim only exterior Crystals triangles intruding into the mapped 63 footprint.
Interior nodes and every unrelated buffer remain byte-for-byte referenced as before.
"""
import sys,json,struct,hashlib
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
cut=unary_union([footprint('way/1421481100'),footprint('way/1422113647')]).buffer(.02)
p=Path('build/geographic-strip/detailed.glb');raw=p.read_bytes();backup=Path('.bitmagic/city-exterior-backups/citycenter63-2026-10-19/detailed.glb')
if not backup.exists():backup.write_bytes(raw)
n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);buf=bytearray(raw[28+n:]);report=[]
dtypes={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1',5122:'<i2',5120:'i1'}
sizes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def read(ai):
 a=j['accessors'][ai];v=j['bufferViews'][a['bufferView']];dt=np.dtype(dtypes[a['componentType']]);s=sizes[a['type']]
 return np.ndarray((a['count'],s),dtype=dt,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dt.itemsize*s),dt.itemsize)).copy()
def write(arr,template):
 arr=np.ascontiguousarray(arr);buf.extend(b'\0'*(-len(buf)%4));off=len(buf);buf.extend(arr.tobytes());vi=len(j['bufferViews']);j['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=arr.nbytes));a={k:v for k,v in template.items() if k not in ['bufferView','byteOffset','min','max','count','sparse']};a.update(bufferView=vi,count=len(arr));a['min']=arr.min(0).tolist();a['max']=arr.max(0).tolist();ai=len(j['accessors']);j['accessors'].append(a);return ai
for nd in j['nodes']:
 e=nd.get('extras',{})
 if e.get('geographicOwner')!='crystals' or e.get('visibilityKind')=='interior' or 'mesh' not in nd or e.get('citycenter63Trim'):continue
 for prim in j['meshes'][nd['mesh']]['primitives']:
  attrs={k:read(v) for k,v in prim['attributes'].items()};pos=attrs['POSITION'];idx=read(prim['indices']).ravel().reshape(-1,3);keep=[];extra={k:[] for k in attrs};changed=0
  for face in idx:
   vs=pos[face].astype(float);lo=vs.min(0);hi=vs.max(0)
   if hi[0]<cut.bounds[0] or lo[0]>cut.bounds[2] or hi[2]<cut.bounds[1] or lo[2]>cut.bounds[3]:keep.append(face.tolist());continue
   projected=Polygon(vs[:,[0,2]])
   if projected.area>1e-7:
    coords=vs[:,[0,2]];region=projected;mask=cut
   else:
    delta=vs[:,[0,2]].max(0)-vs[:,[0,2]].min(0);axis=0 if delta[0]>delta[1] else 2
    if hi[axis]-lo[axis]<1e-5:keep.append(face.tolist());continue
    ia=int(np.argmin(vs[:,axis]));ib=int(np.argmax(vs[:,axis]));line=LineString([vs[ia,[0,2]],vs[ib,[0,2]]]);section=line.intersection(cut);segments=list(section.geoms) if hasattr(section,'geoms') else [section];ranges=[]
    for seg in segments:
     if seg.geom_type!='LineString' or seg.is_empty:continue
     vals=[q[0 if axis==0 else 1] for q in seg.coords];ranges.append(box(min(vals),-100,max(vals),500))
    mask=unary_union(ranges);coords=vs[:,[axis,1]];region=Polygon(coords)
   if region.area<1e-8 or not region.intersects(mask):keep.append(face.tolist());continue
   remainder=region.difference(mask)
   if abs(remainder.area-region.area)<1e-7:keep.append(face.tolist());continue
   changed+=1;matrix=np.vstack([coords.T,np.ones(3)])
   for poly in parts(remainder):
    for tri in triangles(poly):
     indices=[];weights=[]
     for q in list(tri.exterior.coords)[:-1]:weights.append(np.linalg.solve(matrix,np.array([q[0],q[1],1.])))
     verts=np.array(weights)@vs
     if np.dot(np.cross(verts[1]-verts[0],verts[2]-verts[0]),np.cross(vs[1]-vs[0],vs[2]-vs[0]))<0:weights.reverse()
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
 mesh=j['meshes'][nd['mesh']];mesh['primitives']=[x for x in mesh['primitives'] if not x.pop('_remove',False)]
 if not mesh['primitives']:nd.pop('mesh')
 e['citycenter63Trim']=True
if report:
 j['buffers'][0]['byteLength']=len(buf);buf.extend(b'\0'*(-len(buf)%4));data=json.dumps(j,separators=(',',':')).encode();data+=b' '*(-len(data)%4);p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(data)+len(buf))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(buf),0x004e4942)+buf)
 rev=hashlib.sha256(p.read_bytes()).hexdigest()[:16]
 for f in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(f).write_text(json.dumps({'revision':rev}))
Path('build/city-exteriors/citycenter63-crystals-trim.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
