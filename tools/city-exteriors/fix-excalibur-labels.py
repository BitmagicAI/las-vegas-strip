"""Correct two approach labels only; preserve all highrise geometry/binary data."""
import json,struct,math,hashlib
from pathlib import Path
p=Path('build/highrises/exteriors.glb');raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);changed=[]
for node in doc['nodes']:
 if node.get('extras',{}).get('property')!='excalibur' or node.get('name') not in ['EXCALIBUR','EXCALIBUR.001']:continue
 if node.get('extras',{}).get('approachLabelCorrected'):continue
 # Absolute target also makes this safe after a fresh export from corrected source.
 node['rotation']=[-.27059805,-.65328148,.65328148,-.27059805]
 node['extras']['approachLabelCorrected']=True;changed.append(node['name'])
if changed:
 backup=Path('.bitmagic/city-exterior-backups/excalibur-labels-2026-10-14/exteriors.glb');backup.parent.mkdir(parents=True,exist_ok=True)
 if not backup.exists():backup.write_bytes(raw)
 data=json.dumps(doc,separators=(',',':')).encode();data+=b' '*(-len(data)%4);tail=raw[20+n:]
 p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
 Path('build/highrises/version.json').write_text(json.dumps({'revision':hashlib.sha256(p.read_bytes()).hexdigest()[:16]}))
print({'changed':changed,'binaryPreserved':p.read_bytes()[-len(raw[20+n:]):]==raw[20+n:]})
