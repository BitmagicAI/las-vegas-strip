"""Remove replaced legacy exterior nodes only; retain all public interior bytes.
Idempotent, and separate from tower/core installer. Source backup stays immutable.
"""
import json,struct,hashlib
from pathlib import Path
p=Path('build/geographic-strip/detailed.glb');raw=p.read_bytes();backup=Path('.bitmagic/city-exterior-backups/flamingo-podium-2026-10-14');backup.mkdir(parents=True,exist_ok=True)
if not (backup/'before-canopy-correction.glb').exists():(backup/'before-canopy-correction.glb').write_bytes(raw)
if not (backup/'detailed.glb').exists():(backup/'detailed.glb').write_bytes(raw)
n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);body=raw[20+n:];removed=[]
for nd in j['nodes']:
 e=nd.get('extras',{})
 if e.get('geographicOwner')=='flamingo' and (e.get('visibilityKind')=='outside' or nd.get('name') in ['VIS_zone35_shell_arrival_pink__flamingo','VIS_zone35_shell_arrival_gold__flamingo']) and 'mesh' in nd:
  removed.append(nd['name']);nd.pop('mesh');e['flamingoPodiumReplaced']=True
if removed:
 data=json.dumps(j,separators=(',',':')).encode();data+=b' '*(-len(data)%4);p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(data)+len(body))+struct.pack('<II',len(data),0x4e4f534a)+data+body)
 rev=hashlib.sha256(p.read_bytes()).hexdigest()[:16]
 for f in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(f).write_text(json.dumps({'revision':rev}))
for name in ['src/work/geographic/level.json','build/geographic-strip/detailed.mesh-level.json']:
 p=Path(name);bp=backup/name.replace('/','_')
 if not bp.exists():bp.write_bytes(p.read_bytes())
 j=json.loads(p.read_text());old=j['colliders'];j['colliders']=[c for c in old if not c.get('name','').startswith(('Exterior / Flamingo /','Public design / flamingo / canopy pier /'))];p.write_text(json.dumps(j,separators=(',',':')))
 print(name,'exterior-only colliders removed',len(old)-len(j['colliders']))
print('Removed legacy exterior nodes',len(removed));(backup/'replacement-report.json').write_text(json.dumps(removed,indent=2))
