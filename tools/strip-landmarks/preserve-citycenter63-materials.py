"""Retain installed material definitions when exporting the bounded shade candidate.

The current shared exporter changed legacy ph-glass/ph-paving since this asset
was authored. Copy texture-free material definitions by name; never copy indices
into different texture tables. This operates on a candidate, not live assets.
"""
import argparse,json,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('candidate',type=Path);a=p.parse_args()
def read(path):
 data=path.read_bytes();length,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
 return json.loads(data[20:20+length]),data[20+length:]
old,_=read(a.original);new,tail=read(a.candidate)
assert not old.get('textures') and not new.get('textures')
materials={m['name']:m for m in old['materials']};changed=[]
for i,m in enumerate(new['materials']):
 if m['name'] in materials:
  if m!=materials[m['name']]:changed.append(m['name'])
  new['materials'][i]=materials[m['name']]
raw=json.dumps(new,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4)
a.candidate.write_bytes(struct.pack('<III',0x46546c67,2,20+len(raw)+len(tail))+struct.pack('<II',len(raw),0x4e4f534a)+raw+tail)
print(json.dumps({'restoredMaterialDefinitions':changed,'retainedMaterialNames':len(materials),'candidateOnly':True}))
