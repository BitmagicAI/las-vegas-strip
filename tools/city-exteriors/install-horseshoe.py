"""Replace Horseshoe tower skins, preserve public interiors, fit existing guest core.
Idempotent GLB edit: append only changed roof primitives, retain every other byte
of attribute data. Roof opening is bounded to the new stair, Y12.1..12.4 only.
"""
import sys,json,struct,hashlib
from pathlib import Path
sys.path.insert(0,'build/south-strip/python');sys.path.insert(0,'tools/geographic-strip')
import numpy as np
from shapely.geometry import Polygon,box
from surface_geometry import triangles
from building_surfaces import parts
backup=Path('build/city-exteriors/before');backup.mkdir(exist_ok=True,parents=True)
p=Path('build/geographic-strip/detailed.glb');raw=p.read_bytes();b=backup/'before-horseshoe-detailed.glb'
if not b.exists():b.write_bytes(raw)
n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);buf=bytearray(raw[28+n:]);removed=[];changed=0
mask=box(114.75,282.2,125.25,289.8)
def read(ai):
 a=j['accessors'][ai];v=j['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];size={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];stride=v.get('byteStride',np.dtype(dt).itemsize*size)
 return np.ndarray((a['count'],size),dtype=dt,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,np.dtype(dt).itemsize)).copy()
def add(a,typ='VEC3',integer=False):
 a=np.asarray(a,dtype='<u4' if integer else '<f4');buf.extend(b'\0'*(-len(buf)%4));off=len(buf);buf.extend(a.tobytes());vi=len(j['bufferViews']);j['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=a.nbytes));ai=len(j['accessors']);acc=dict(bufferView=vi,componentType=5125 if integer else 5126,count=len(a),type=typ)
 if typ=='VEC3':acc.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
 j['accessors'].append(acc);return ai
for node in j['nodes']:
 e=node.get('extras',{})
 if e.get('geographicOwner')!='horseshoe' or 'mesh' not in node:continue
 if e.get('visibilityKind')=='outside' and e.get('visibilityTower')=='horseshoe':
  if e.get('horseshoeTowerFiltered'):continue
  # Retain low canopy components sharing the old tower batch.
  kept=[]
  for prim in j['meshes'][node['mesh']]['primitives']:
   pp=read(prim['attributes']['POSITION']);ii=read(prim['indices']).ravel().reshape(-1,3)
   keep=ii[(pp[ii,1].max(axis=1)<12.5)]
   if len(keep):
    prim['indices']=add(keep.ravel(),'SCALAR',True);kept.append(prim)
  if kept:j['meshes'][node['mesh']]['primitives']=kept
  else:removed.append(node['name']);node.pop('mesh')
  e['horseshoeTowerFiltered']=True;changed+=1;continue
 if e.get('horseshoeStairCut'):continue
 mesh=j['meshes'][node['mesh']]
 for prim in mesh['primitives']:
  attrs={k:read(v) for k,v in prim['attributes'].items()};pos=attrs['POSITION'];idx=read(prim['indices']).ravel().reshape(-1,3);out={k:[] for k in attrs};touch=False
  for ids in idx:
   pts=pos[ids];flat=np.ptp(pts[:,1])<.001 and 12.09<=pts[0,1]<=12.41
   poly=Polygon(pts[:,[0,2]]) if flat else None
   if not flat or poly.area<1e-8 or not poly.intersects(mask):
    for k,a in attrs.items():out[k].extend(a[ids])
    continue
   touch=True;basis=np.vstack([pts[:,0],pts[:,2],np.ones(3)])
   for part in parts(poly.difference(mask)):
    for tri in triangles(part):
     coords=np.array(list(tri.exterior.coords)[:-1]);weights=np.linalg.solve(basis,np.vstack([coords[:,0],coords[:,1],np.ones(3)]))
     pp=weights.T@pts
     if np.dot(np.cross(pp[1]-pp[0],pp[2]-pp[0]),np.cross(pts[1]-pts[0],pts[2]-pts[0]))<0:weights=weights[:,::-1]
     for k,a in attrs.items():out[k].extend(weights.T@a[ids])
  if touch:
   changed+=1
   for k,values in out.items():prim['attributes'][k]=add(values,'VEC'+str(attrs[k].shape[1]))
   prim['indices']=add(np.arange(len(out['POSITION'])),'SCALAR',True)
 e['horseshoeStairCut']=True
if removed or changed:
 j['buffers'][0]['byteLength']=len(buf);buf.extend(b'\0'*(-len(buf)%4));data=json.dumps(j,separators=(',',':')).encode();data+=b' '*(-len(data)%4)
 p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(data)+len(buf))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(buf),0x004e4942)+buf)
 rev=hashlib.sha256(p.read_bytes()).hexdigest()[:16]
 for f in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(f).write_text(json.dumps({'revision':rev}))
for filename in ['src/work/geographic/level.json','build/geographic-strip/detailed.mesh-level.json']:
 p=Path(filename);b=backup/('horseshoe-'+p.name)
 if not b.exists():b.write_bytes(p.read_bytes())
 d=json.loads(p.read_text());out=[];cuts=0
 for c in d['colliders']:
  if c.get('name','').startswith('Exterior / Horseshoe /'):cuts+=1;continue
  if c.get('name','').startswith('Interiors / 00426 Horseshoe ceiling') and 'Horseshoe stair cut' not in c['name']:
   v=np.array(c['vertices']).reshape(-1,3);lo=v.min(0);hi=v.max(0);poly=Polygon(v[:,[0,2]]).convex_hull
   if poly.intersects(mask):
    for i,q in enumerate(parts(poly.difference(mask))):
     # Triangular prisms retain the roof's full thickness without filling the hole.
     for ti,t in enumerate(triangles(q)):
      cc=dict(c,name=c['name']+f' / Horseshoe stair cut {i}-{ti}');cc['vertices']=[n for y in [lo[1],hi[1]] for x,z in list(t.exterior.coords)[:-1] for n in [x,y,z]];cc['shape']='convexHull';cc.pop('indices',None);out.append(cc)
    continue
  out.append(c)
 d['colliders']=out;p.write_text(json.dumps(d,separators=(',',':')));print(filename,'obsolete tower colliders removed',cuts)
fit=dict(origin=[120,.075,286],linear=[0,1,-1,0],yaw=1.5707963267948966)
for filename in ['src/work/hotels/towers.json','build/geographic-strip/towers.json']:
 p=Path(filename);b=backup/('horseshoe-'+filename.replace('/','_'))
 if not b.exists():b.write_bytes(p.read_bytes())
 d=json.loads(p.read_text())
 for t in d:
  if t['id']=='horseshoe-resort':t.update(fit);t['name']='Versailles · Preserved guest wing'
 p.write_text(json.dumps(d,indent=2))
print('Removed tower nodes',len(removed),'roof primitives cut',changed)
