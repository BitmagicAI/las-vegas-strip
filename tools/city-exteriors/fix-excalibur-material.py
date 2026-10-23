"""Lossless GLB JSON material edit; preserve every geometry/buffer byte."""
from pathlib import Path
import struct,json,hashlib,shutil
p=Path('build/highrises/exteriors.glb');backup=Path('build/city-exteriors/before/excalibur/exteriors.glb');backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():shutil.copy2(p,backup)
b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);changed=0
for m in d['materials']:
 if m.get('name') in ['South Strip / castlebrick','South Strip / castle-limestone']:
  m['name']='South Strip / castle-limestone';rgb=[int('dbd8cd'[i:i+2],16)/255 for i in (0,2,4)];rgb=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb];m['pbrMetallicRoughness']['baseColorFactor']=[*rgb,1];m['pbrMetallicRoughness']['roughnessFactor']=.78;changed+=1
# Dedicated paint material avoids applying corrugated roofing to smooth cones.
import copy
navy=next(i for i,m in enumerate(d['materials']) if m.get('name')=='South Strip / navy')
blue=copy.deepcopy(d['materials'][navy]);blue['name']='South Strip / excalibur-blue-paint'
rgb=[int('239bc3'[i:i+2],16)/255 for i in (0,2,4)]
blue['pbrMetallicRoughness']['baseColorFactor']=[*((v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4) for v in rgb),1]
blue['pbrMetallicRoughness']['roughnessFactor']=.62
blueid=next((i for i,m in enumerate(d['materials']) if m.get('name')==blue['name']),len(d['materials']))
if blueid==len(d['materials']):d['materials'].append(blue)
red=next(i for i,m in enumerate(d['materials']) if m.get('name')=='South Strip / redroof')
for node in d['nodes']:
 if node.get('extras',{}).get('property')!='excalibur' or 'mesh' not in node:continue
 for primitive in d['meshes'][node['mesh']]['primitives']:
  if primitive.get('material')==navy:
   primitive['material']=blueid if node.get('extras',{}).get('source')=='castle-turrets' else red
   changed+=1
assert changed
j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);tail=b[20+n:];out=struct.pack('<III',0x46546c67,2,20+len(j)+len(tail))+struct.pack('<II',len(j),0x4e4f534a)+j+tail;p.write_bytes(out)
Path('build/highrises/version.json').write_text(json.dumps({'revision':hashlib.sha256(out).hexdigest()[:16]}));print('Updated',changed,'materials; binary chunk unchanged',tail==out[20+len(j):])
