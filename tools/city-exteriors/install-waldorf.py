"""Replace only legacy Waldorf tower skin/collision; retain public lobby/interiors."""
import json,struct,hashlib
from pathlib import Path
backup=Path('build/city-exteriors/before');backup.mkdir(exist_ok=True,parents=True)
p=Path('build/geographic-strip/detailed.glb');raw=p.read_bytes();b=backup/'before-waldorf-detailed.glb'
if not b.exists():b.write_bytes(raw)
n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);removed=[]
for node in j['nodes']:
 e=node.get('extras',{})
 if e.get('geographicOwner')=='waldorf' and e.get('visibilityKind')=='outside' and e.get('visibilityTower')=='waldorf' and 'mesh' in node:removed.append(node['name']);node.pop('mesh')
if removed:
 data=json.dumps(j,separators=(',',':')).encode();data+=b' '*(-len(data)%4);tail=raw[20+n:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(tail))+struct.pack('<II',len(data),0x4e4f534a)+data+tail)
 rev=hashlib.sha256(p.read_bytes()).hexdigest()[:16]
 for f in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(f).write_text(json.dumps({'revision':rev}))
for filename in ['src/work/geographic/level.json','build/geographic-strip/detailed.mesh-level.json']:
 p=Path(filename);b=backup/('waldorf-'+p.name)
 if not b.exists():b.write_bytes(p.read_bytes())
 d=json.loads(p.read_text());old=len(d['colliders']);d['colliders']=[c for c in d['colliders'] if 'Waldorf folded mass' not in c.get('name','')];p.write_text(json.dumps(d,separators=(',',':')));print(filename,'removed',old-len(d['colliders']),'obsolete tower colliders')
fit=json.loads(Path('tools/highrises/waldorf-core-fit.json').read_text())
for filename in ['src/work/hotels/towers.json','build/geographic-strip/towers.json']:
 p=Path(filename);b=backup/('waldorf-'+filename.replace('/','_'))
 if not b.exists():b.write_bytes(p.read_bytes())
 d=json.loads(p.read_text())
 for t in d:
  if t['id']=='waldorf-residences':t.update(fit)
 p.write_text(json.dumps(d,indent=2))
print('Removed obsolete tower render nodes',len(removed))
