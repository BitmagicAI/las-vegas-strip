"""Remove the obsolete stretched garden pergola and east gazebo intersecting mapped kiosks/colonnade.
No interior primitive or collision is modified. Dry run unless --apply is passed.
"""
import sys,json,struct,hashlib
from pathlib import Path
sys.path.insert(0,'build/south-strip/python')
import numpy as np
p=Path('build/geographic-strip/detailed.glb');raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);buf=bytearray(raw[28+n:]);changes=[]
def read(ai):
 a=j['accessors'][ai];v=j['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];sz={'SCALAR':1,'VEC3':3}[a['type']];return np.ndarray((a['count'],sz),dtype=dt,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dt).itemsize*sz),np.dtype(dt).itemsize)).copy()
for nd in j['nodes']:
 if nd.get('extras',{}).get('geographicOwner')!='caesars' or nd.get('extras',{}).get('visibilityKind')!='outside' or 'mesh' not in nd:continue
 if not any(m in nd['name'] for m in ['c_stone__caesars','c_red__caesars','c_shadow__caesars']):continue
 for pr in j['meshes'][nd['mesh']]['primitives']:
  v=read(pr['attributes']['POSITION']);ix=read(pr['indices']).ravel().reshape(-1,3);parent=list(range(len(ix)));seen={}
  def root(a):
   while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
   return a
  for k,tri in enumerate(ix):
   for vi in tri:
    key=tuple(np.round(v[vi],4));old=seen.get(key)
    if old is not None:parent[root(k)]=root(old)
    else:seen[key]=k
  groups={}
  for k in range(len(ix)):groups.setdefault(root(k),[]).append(k)
  remove=set()
  for ids in groups.values():
   pts=v[ix[ids]];lo=pts.min((0,1));hi=pts.max((0,1))
   if lo[0]>=-124 and hi[0]<=-91 and lo[2]>=12 and hi[2]<=112 and lo[1]>=-.05 and hi[1]<=9:
    changes.append(dict(node=nd['name'],triangles=len(ids),bounds=[*lo.tolist(),*hi.tolist()]));remove.update(ids)
  if not remove:continue
  keep=np.array([tri for k,tri in enumerate(ix) if k not in remove],dtype='<u4').ravel();buf.extend(b'\0'*(-len(buf)%4));off=len(buf);buf.extend(keep.tobytes());vi=len(j['bufferViews']);j['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=keep.nbytes));ai=len(j['accessors']);j['accessors'].append(dict(bufferView=vi,componentType=5125,count=len(keep),type='SCALAR'));pr['indices']=ai
if '--apply' in sys.argv and changes:
 backup=Path('.bitmagic/city-exterior-backups/caesars-garden-2026-10-13/detailed.glb')
 backup.parent.mkdir(parents=True,exist_ok=True)
 if not backup.exists():backup.write_bytes(raw)
 j['buffers'][0]['byteLength']=len(buf);buf.extend(b'\0'*(-len(buf)%4));data=json.dumps(j,separators=(',',':')).encode();data+=b' '*(-len(data)%4);p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(data)+len(buf))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(buf),0x004e4942)+buf)
 rev=hashlib.sha256(p.read_bytes()).hexdigest()[:16]
 for f in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(f).write_text(json.dumps({'revision':rev}))
 Path('build/city-exteriors/caesars-old-garden-pergola-removal.json').write_text(json.dumps(changes,indent=2))
print(json.dumps(changes,indent=2))
