"""Subtract surveyed outdoor-garden footprint from retained Flamingo casino only.
Current-data, attribute-preserving and idempotent. Backups never used as input.
"""
import sys,struct,hashlib,shutil
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
from flamingo_garden import garden_mask,ROTUNDA_IDS
from shapely.prepared import prep
mask=garden_mask();stairWell=box(192.3,8.8,198.3,23.03);prepared=prep(mask);bounds=mask.bounds
# Also remove the parent podium's surfaces within the three replacement rotundas.
rotundas=unary_union([footprint(i).buffer(.025)for i in ROTUNDA_IDS])
def subtract(vs,area=mask):
 xz=vs[:,[0,2]]
 if xz[:,0].max()<area.bounds[0]or xz[:,0].min()>area.bounds[2]or xz[:,1].max()<area.bounds[1]or xz[:,1].min()>area.bounds[3]:return None
 shape=Polygon(xz)
 if shape.area>1e-8:
  if not shape.intersects(area):return None
  remain=shape.difference(area)
  if abs(remain.area-shape.area)<1e-9:return None
  mat=np.vstack([xz.T,np.ones(3)]);inv=np.linalg.inv(mat);out=[]
  for poly in parts(remain):
   for tri in triangles(poly):
    w=np.array([inv@np.array([x,z,1])for x,z in list(tri.exterior.coords)[:-1]])
    out.append(oriented(w,vs))
  return out
 # Vertical faces project to a line: perform subtraction in their(u,y) plane.
 pairs=[(i,k,np.linalg.norm(xz[k]-xz[i]))for i in range(3)for k in range(i+1,3)];i,k,L=max(pairs,key=lambda q:q[2])
 if L<1e-9:return None
 origin=xz[i];axis=(xz[k]-origin)/L;u=(xz-origin)@axis;line=LineString([origin,origin+axis*L]);cut=line.intersection(area)
 intervals=[]
 def lines(g):
  if g.is_empty:return []
  if g.geom_type=='LineString':return [g]
  return [v for q in getattr(g,'geoms',[])for v in lines(q)]
 for seg in lines(cut):
  us=[np.dot(np.array(p)-origin,axis)for p in seg.coords];intervals.append(box(min(us),-100,max(us),200))
 if not intervals:return None
 uv=np.column_stack([u,vs[:,1]]);poly=Polygon(uv);remain=poly.difference(unary_union(intervals))
 if abs(remain.area-poly.area)<1e-9:return None
 inv=np.linalg.inv(np.vstack([uv.T,np.ones(3)]));out=[]
 for p in parts(remain):
  for tri in triangles(p):out.append(oriented(np.array([inv@np.array([u,y,1])for u,y in list(tri.exterior.coords)[:-1]]),vs))
 return out

def oriented(w,vs):
 q=w@vs
 if np.dot(np.cross(q[1]-q[0],q[2]-q[0]),np.cross(vs[1]-vs[0],vs[2]-vs[0]))<0:w=w[[0,2,1]]
 return w

if __name__=='__main__':
 p=Path('build/geographic-strip/detailed.glb');level=Path('src/work/geographic/level.json');parent=Path('build/strip-landmarks/flamingoExterior-exterior.json');pc=Path('build/strip-landmarks/flamingoExterior-exterior-collision.json')
 bak=Path('.bitmagic/city-exterior-backups/flamingo-garden-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
 for f in [p,level,parent,pc]:
  if not(bak/f.name).exists():shutil.copy2(f,bak/f.name)
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);buf=bytearray(raw[28+n:]);report=[]
 dtypes={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1',5122:'<i2',5120:'i1'};sizes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
 def read(ai):
  a=j['accessors'][ai];v=j['bufferViews'][a['bufferView']];dt=np.dtype(dtypes[a['componentType']]);s=sizes[a['type']]
  return np.ndarray((a['count'],s),dtype=dt,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dt.itemsize*s),dt.itemsize)).copy()
 def write(arr,template):
  arr=np.ascontiguousarray(arr);buf.extend(b'\0'*(-len(buf)%4));off=len(buf);buf.extend(arr.tobytes());vi=len(j['bufferViews']);j['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=arr.nbytes));a={k:v for k,v in template.items()if k not in ['bufferView','byteOffset','min','max','count','sparse']};a.update(bufferView=vi,count=len(arr));a['min']=arr.min(0).tolist();a['max']=arr.max(0).tolist();ai=len(j['accessors']);j['accessors'].append(a);return ai
 for nd in j['nodes']:
  e=nd.get('extras',{})
  if e.get('geographicOwner')!='flamingo'or e.get('visibilityZone')!='zone16'or'mesh'not in nd:continue
  assert not any(k in nd for k in ['matrix','translation','rotation','scale']),nd['name']
  for prim in j['meshes'][nd['mesh']]['primitives']:
   attrs={k:read(v)for k,v in prim['attributes'].items()};pos=attrs['POSITION'];idx=read(prim['indices']).ravel().reshape(-1,3);keep=[];extra={k:[]for k in attrs};changed=0
   # Interior furnishing islands are removed whole rather than sliced through seats.
   whole=set()
   if '_interior_'in nd.get('name',''):
    parents=list(range(len(idx)));bypos={}
    def root(i):
     while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
     return i
    for i,face in enumerate(idx):
     for vertex in face:
      key=tuple(np.round(pos[vertex],4));old=bypos.get(key)
      if old is not None:parents[root(i)]=root(old)
      else:bypos[key]=i
    components={}
    for i in range(len(idx)):components.setdefault(root(i),[]).append(i)
    for faces in components.values():
     points=pos[idx[faces].ravel()];lo=points.min(0);hi=points.max(0)
     if max(hi[0]-lo[0],hi[2]-lo[2])<12 and mask.intersects(box(lo[0]-.001,lo[2]-.001,hi[0]+.001,hi[2]+.001)):whole.update(faces)
   for fi,face in enumerate(idx):
    vs=pos[face].astype(float);effective=mask
    if 'ri_marble'in nd['name'] and 5.8<vs[:,1].min() and vs[:,1].max()<6.6:effective=mask.union(stairWell)
    centre=vs.mean(0);oldStep=.075+(centre[2]+47)*6/70
    obsoleteEscalator=('ri_dark'in nd['name']or'ri_gold'in nd['name'])and 192.3<centre[0]<198.3 and -47.1<centre[2]<23.05 and oldStep-.1<centre[1]<oldStep+1.2
    pieces=[]if fi in whole or obsoleteEscalator else subtract(vs,effective)
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
   report.append(dict(node=nd['name'],changedTriangles=changed,wholeFurnishingTriangles=len(whole),before=len(idx),after=len(keep)))
   if not keep:prim['_remove']=True;continue
   for k,arr in attrs.items():
    if extra[k]:prim['attributes'][k]=write(np.vstack([arr,np.array(extra[k],dtype=arr.dtype)]),j['accessors'][prim['attributes'][k]])
   prim['indices']=write(np.array(keep,dtype='<u4').reshape(-1,1),dict(componentType=5125,type='SCALAR'))
  mesh=j['meshes'][nd['mesh']];mesh['primitives']=[q for q in mesh['primitives']if not q.pop('_remove',False)]
  if not mesh['primitives']:nd.pop('mesh')
 if report:
  j['buffers'][0]['byteLength']=len(buf);buf.extend(b'\0'*(-len(buf)%4));data=json.dumps(j,separators=(',',':')).encode();data+=b' '*(-len(data)%4);p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(data)+len(buf))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(buf),0x004e4942)+buf)
  rev=hashlib.sha256(p.read_bytes()).hexdigest()[:16]
  for f in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(f).write_text(json.dumps({'revision':rev}))
 def collision_cut(c,area):
  v=c['vertices'];keep=[];changed=0
  for i in range(0,len(c['indices']),3):
   face=c['indices'][i:i+3];vs=np.array([v[k*3:k*3+3]for k in face]);pieces=subtract(vs,area)
   if pieces is None:keep.extend(face);continue
   changed+=1
   for w in pieces:
    n=len(v)//3;v.extend((w@vs).ravel().tolist());keep.extend([n,n+1,n+2])
  c['indices']=keep;return changed
 d=json.loads(level.read_text());cr=[];colliders=[]
 from shapely.geometry import MultiPoint
 for c in d['colliders']:
  if 'flamingo'not in c.get('name','').lower()or not c.get('vertices'):
   colliders.append(c);continue
  if 'Flamingo escalator' in c['name']:
   cr.append(dict(name=c['name'],removed='Replaced with metre-scale14m flight inside mapped casino, preserving upper gallery access'));continue
  effective=mask.union(stairWell)if 'Flamingo upper lounge'in c['name']else mask
  if 'indices'in c:
   n=collision_cut(c,effective);colliders.append(c)
   if n:cr.append(dict(name=c['name'],triangles=n))
   continue
  vs=np.array(c['vertices']).reshape(-1,3);plan=MultiPoint(vs[:,[0,2]]).convex_hull
  if not plan.intersects(effective):colliders.append(c);continue
  remaining=plan.difference(effective)
  if abs(remaining.area-plan.area)<1e-8:colliders.append(c);continue
  levels=np.unique(np.round(vs[:,1],5))
  assert len(levels)<=2,(c['name'],'non-prismatic convex hull needs explicit treatment')
  count=0
  for poly in parts(remaining):
   for t in triangles(poly):
    cc=dict(c,name=c['name']+' / garden retained '+str(count));cc['vertices']=[v for y in [float(vs[:,1].min()),float(vs[:,1].max())]for x,z in list(t.exterior.coords)[:-1]for v in [x,y,z]];colliders.append(cc);count+=1
  cr.append(dict(name=c['name'],retainedPrisms=count))
 d['colliders']=colliders;level.write_text(json.dumps(d,separators=(',',':')))
 d=json.loads(parent.read_text());pr=[]
 for g in d['meshes']:
  if g.get('source')!='flamingo-podium':continue
  v=g['vertices'];keep=[];n=0
  for face in g['faces']:
   vs=np.array([v[i]for i in face]);pieces=subtract(vs,rotundas)
   if pieces is None:keep.append(face);continue
   n+=1
   for w in pieces:
    start=len(v);v.extend((w@vs).tolist());keep.append([start,start+1,start+2])
  g['faces']=keep
  if n:pr.append(dict(material=g['material'],triangles=n))
 parent.write_text(json.dumps(d,separators=(',',':')))
 d=json.loads(pc.read_text());cn=collision_cut(d,rotundas);pc.write_text(json.dumps(d,separators=(',',':')))
 result=dict(legacyVisual=report,legacyCollision=cr,parentVisual=pr,parentCollisionTriangles=cn,maskArea=mask.area,scope='Mapped garden void and three replacement rotundas only. Other casino footprint/interiors retained; furnishing components crossing the boundary removed whole.')
 Path('build/city-exteriors/flamingo-garden-cut.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
