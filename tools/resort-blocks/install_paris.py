"""Install a selective Paris exterior replacement, preserving playable interiors."""
import json,struct,hashlib,sys
from pathlib import Path
sys.path.insert(0,'tools/geographic-strip');import mapping
OUT=Path('build/resort-blocks/paris');backup=OUT/'before';backup.mkdir(exist_ok=True)
def backup_file(p):
 dest=backup/p.name
 if not dest.exists():dest.write_bytes(p.read_bytes())
def old_inside(p):return 79.8<=p[0]<=177.7 and 385.5<=p[2]<=478.5 and p[1]<11
p=Path('build/geographic-strip/detailed.glb');backup_file(p);__import__('runpy').run_path('tools/resort-blocks/remove_paris_arc.py');raw=p.read_bytes();length=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+length]);removed=[]
for n in j.get('nodes',[]):
 e=n.get('extras',{})
 if e.get('geographicOwner')=='eiffel' or (e.get('geographicOwner')=='paris' and e.get('visibilityKind')=='outside'):
  removed.append(n.get('name'));n.pop('mesh',None);n.pop('children',None)
s=json.dumps(j,separators=(',',':')).encode();s+=b' '*((-len(s))%4);tail=raw[20+length:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(s)+len(tail))+struct.pack('<II',len(s),0x4e4f534a)+s+tail)
# Classify original names before their geographic transform. Keep the whole
# functioning casino/service suite and its doors; only obsolete exterior collision goes.
old=json.load(open(mapping.BASE/'build/hotels/staged-vegas.mesh-level.json'));names={v['name'] for v in old['colliders'] if mapping.owner(v['name'],mapping.center(v))=='paris'}
eiffel_names={v['name'] for v in old['colliders'] if mapping.owner(v['name'],mapping.center(v))=='eiffel'}
p=Path('src/work/geographic/level.json');backup_file(p);data=json.loads(p.read_text());gone=[]
for c in data['colliders']:
 if c['name'] in eiffel_names or c['name'].split(' / court clipped')[0] in eiffel_names or (c['name'] in names and (not old_inside(mapping.center(c)) or 'Arc de Triomphe' in c['name'])):gone.append(c['name'])
data['colliders']=[c for c in data['colliders'] if c['name'] not in gone]
for p in [Path('src/work/geographic/level.json'),Path('build/geographic-strip/detailed.mesh-level.json')]:p.write_text(json.dumps(data,indent=2)+'\n')
__import__('runpy').run_path('tools/resort-blocks/clip_paris_arrival.py')
# The old custom interior visibility volumes remain the authority for guest access.
revision=hashlib.sha256(Path('build/geographic-strip/detailed.glb').read_bytes()).hexdigest()[:16]
for p in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(p).write_text(json.dumps(dict(revision=revision)))
previous=json.loads((OUT/'ownership-report.json').read_text()) if (OUT/'ownership-report.json').exists() else {}
gone=list(dict.fromkeys(previous.get('removedColliders',[])+gone))
(OUT/'ownership-report.json').write_text(json.dumps(dict(removedLegacyExteriorBatches=len(removed),legacyBatchNames=removed,removedColliders=gone,preserved='All Paris interior and shell zones, doors, objectives, custom guest stair/hall/room assets; Eiffel lift interaction and unchanged landing coordinates; Horseshoe/Versailles owners',replacementIds=json.loads((OUT/'replacement-ids.json').read_text())),indent=2))
print('Paris exterior installed;',len(removed),'legacy exterior batches and',len(gone),'obsolete exterior colliders removed.')
