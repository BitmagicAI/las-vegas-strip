"""Move one sanctuary projector out of the mapped entrance lane, locally.
Preserve the sanctuary field, vehicles, objectives and all unrelated vertices.
"""
import json,struct,hashlib,shutil
from pathlib import Path
p=Path('build/geographic-strip/detailed.glb');raw=p.read_bytes();ln=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+ln]);buf=bytearray(raw[28+ln:]);changed=0
if not j.get('extras',{}).get('bellagioProjectorClear'):
 backup=Path('build/resort-blocks/bellagio/south-arrival-before/detailed.glb')
 if not backup.exists():shutil.copyfile(p,backup)
 visited=set()
 for n in j['nodes']:
  if n.get('extras',{}).get('geographicOwner')!='sanctuary' or 'mesh' not in n:continue
  t=n.get('translation',[0,0,0])
  for prim in j['meshes'][n['mesh']]['primitives']:
   aid=prim['attributes']['POSITION']
   if aid in visited:continue
   visited.add(aid);a=j['accessors'][aid];v=j['bufferViews'][a['bufferView']];assert a['componentType']==5126
   start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12)
   for i in range(a['count']):
    off=start+i*stride;x,y,z=struct.unpack_from('<fff',buf,off);wx,wy,wz=x+t[0],y+t[1],z+t[2]
    if -66.65<wx<-65.6 and -.05<=wy<1.8 and 524.65<wz<525.8:
     struct.pack_into('<fff',buf,off,x,y,z+11);changed+=1
 j.setdefault('extras',{})['bellagioProjectorClear']=True;s=json.dumps(j,separators=(',',':')).encode();s+=b' '*((-len(s))%4)
 p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(s)+len(buf))+struct.pack('<II',len(s),0x4e4f534a)+s+struct.pack('<II',len(buf),0x004e4942)+buf)
for path in ['src/work/geographic/level.json','build/geographic-strip/detailed.mesh-level.json']:
 q=Path(path);data=json.loads(q.read_text())
 for c in data['colliders']:
  if c['name']=='Sanctuary / field projector 5' and min(c['vertices'][2::3])<530:
   for i in range(2,len(c['vertices']),3):c['vertices'][i]+=11
 q.write_text(json.dumps(data,indent=2)+'\n')
revision=hashlib.sha256(p.read_bytes()).hexdigest()[:16]
for q in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(q).write_text(json.dumps(dict(revision=revision)))
print('Projector vertices moved',changed)
