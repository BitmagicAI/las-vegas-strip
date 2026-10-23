"""Remove only superseded Crystals roof faces/ribs and roof colliders.
All source attribute buffers and all unrelated primitives are retained. An extras
marker makes a second run a no-op; never restore a stale whole-city backup.
"""
import json,struct,hashlib,sys
from pathlib import Path
sys.path.insert(0,'build/south-strip/python')
import numpy as np
backup=Path('.bitmagic/city-exterior-backups/crystals-roof-2026-10-13');backup.mkdir(parents=True,exist_ok=True)
p=Path('build/geographic-strip/detailed.glb');raw=p.read_bytes()
if not (backup/'detailed.glb').exists():(backup/'detailed.glb').write_bytes(raw)
n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);buf=bytearray(raw[28+n:]);removed=0;changed=[]
def read(ai):
 a=j['accessors'][ai];v=j['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];size={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];stride=v.get('byteStride',np.dtype(dt).itemsize*size)
 return np.ndarray((a['count'],size),dtype=dt,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,np.dtype(dt).itemsize)).copy()
for nd in j['nodes']:
 e=nd.get('extras',{})
 if e.get('geographicOwner')!='crystals' or 'mesh' not in nd or e.get('crystalsRoofRevision',0)>=2:continue
 if e.get('visibilityZone') not in ['zone23','zone28','outside']:continue
 for prim in j['meshes'][nd['mesh']]['primitives']:
  pos=read(prim['attributes']['POSITION']);idx=read(prim['indices']).ravel().reshape(-1,3);pts=pos[idx];lo=pts.min(1);hi=pts.max(1)
  # Source folded roof has y18 edge and y27/31/35 crests; structural ribs y17.6.
  # Main footprint only; leave projecting shop fronts and the Veer arrivals alone.
  mask=(lo[:,1]>=17.35)&(hi[:,1]<=35.1)&(lo[:,0]>=-180.7)&(hi[:,0]<=-40.7)&(lo[:,2]>=823.9)&(hi[:,2]<=1001.5)
  if not mask.any():continue
  kept=idx[~mask].astype('<u4').ravel();removed+=int(mask.sum());changed.append(nd['name'])
  if not len(kept):prim['indices']=prim['indices'];prim['_remove']=True;continue
  buf.extend(b'\0'*(-len(buf)%4));off=len(buf);buf.extend(kept.tobytes());vi=len(j['bufferViews']);j['bufferViews'].append(dict(buffer=0,byteOffset=off,byteLength=kept.nbytes));ai=len(j['accessors']);j['accessors'].append(dict(bufferView=vi,componentType=5125,count=len(kept),type='SCALAR'));prim['indices']=ai
 mesh=j['meshes'][nd['mesh']];mesh['primitives']=[pr for pr in mesh['primitives'] if not pr.pop('_remove',False)]
 if not mesh['primitives']:nd.pop('mesh')
 e['crystalsRoofReplaced']=True; e['crystalsRoofRevision']=2
if removed:
 j['buffers'][0]['byteLength']=len(buf);buf.extend(b'\0'*(-len(buf)%4));data=json.dumps(j,separators=(',',':')).encode();data+=b' '*(-len(data)%4)
 p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(data)+len(buf))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(buf),0x004e4942)+buf)
 rev=hashlib.sha256(p.read_bytes()).hexdigest()[:16]
 for f in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(f).write_text(json.dumps({'revision':rev}))
colliders={}
for file in ['src/work/geographic/level.json','build/geographic-strip/detailed.mesh-level.json']:
 p=Path(file);b=backup/file.replace('/','_')
 if not b.exists():b.write_bytes(p.read_bytes())
 d=json.loads(p.read_text());old=len(d['colliders']);d['colliders']=[c for c in d['colliders'] if 'Crystals folded roof' not in c.get('name','')];colliders[file]=old-len(d['colliders']);p.write_text(json.dumps(d,separators=(',',':')))
report=dict(removedTriangles=removed,changedNodes=changed,removedRoofColliders=colliders,backup=str(backup));Path('build/city-exteriors/crystals-roof-install.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
