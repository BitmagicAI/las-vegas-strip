"""Selective PH tower replacement; leaves interiors, collision and other owners byte-identical."""
import json,struct,hashlib
from pathlib import Path
p=Path('build/geographic-strip/detailed.glb');dest=Path('build/city-exteriors/before/detailed.glb');dest.parent.mkdir(parents=True,exist_ok=True)
raw=p.read_bytes()
if not dest.exists():dest.write_bytes(raw)
n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);removed=[]
for node in j['nodes']:
 e=node.get('extras',{});name=node.get('name','')
 if e.get('geographicOwner')!='planet-hollywood' or e.get('visibilityKind')!='outside' or not e.get('visibilityTower'):continue
 if any(x in name for x in ['rx_leaf','rx_trunk']):continue
 if 'mesh' in node:removed.append(name);node.pop('mesh')
if removed:
 data=json.dumps(j,separators=(',',':')).encode();data+=b' '*(-len(data)%4);tail=raw[20+n:]
 p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
 rev=hashlib.sha256(p.read_bytes()).hexdigest()[:16]
 for f in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(f).write_text(json.dumps({'revision':rev}))
 out=Path('docs/project-records/city-exteriors-2026-10-12/planet-ownership.json');out.write_text(json.dumps({'removedRenderNodes':removed,'retained':'Every interior and shell node, collider, road and landscape. Existing tower collision and guest datum retained.','backup':str(dest)},indent=2))
print('Removed obsolete tower render batches:',len(removed))
