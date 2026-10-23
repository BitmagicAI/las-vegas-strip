"""Move the prototype safe zone out of the mapped lake to its south forecourt.
Uses named ownership, preserving every unrelated authored/editor transform.
"""
import sys,json,struct,hashlib
from pathlib import Path
sys.path.insert(0,'tools/geographic-strip');import mapping
out=Path('build/geographic-strip');target=mapping.point([-42,0,0],'sanctuary')
old=json.loads((out/'anchors.json').read_text())['sanctuary'];dx,dz=target[0]-old[0],target[2]-old[2]
if abs(dx)+abs(dz)<.001:print('Sanctuary already on the south forecourt');sys.exit(0)
source=json.loads((mapping.BASE/'build/hotels/staged-vegas.mesh-level.json').read_text())
names={c['name'] for c in source['colliders'] if mapping.owner(c['name'],mapping.center(c))=='sanctuary'}
for path in [out/'detailed.mesh-level.json',Path('src/work/geographic/level.json')]:
    data=json.loads(path.read_text())
    for c in data['colliders']:
        if c['name'] not in names:continue
        if 'position' in c:c['position'][0]+=dx;c['position'][2]+=dz
        else:
            for i in range(0,len(c['vertices']),3):c['vertices'][i]+=dx;c['vertices'][i+2]+=dz
    for p in data.get('landmarks',[]):
        if p['name'] in ['spawn','haven'] or 'sanctuary' in p['name'].lower():p['position'][0]+=dx;p['position'][2]+=dz
    path.write_text(json.dumps(data,indent=2)+'\n')
path=out/'detailed.glb';raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];data=json.loads(raw[20:20+n]);moved=0
for node in data.get('nodes',[]):
    if node.get('extras',{}).get('geographicOwner')!='sanctuary':continue
    p=node.setdefault('translation',[0,0,0]);p[0]+=dx;p[2]+=dz;moved+=1
payload=json.dumps(data,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);tail=raw[20+n:]
path.write_bytes(struct.pack('<III',0x46546c67,2,20+len(payload)+len(tail))+struct.pack('<II',len(payload),0x4e4f534a)+payload+tail)
for path in [out/'anchors.json',Path('src/work/geographic/anchors.json')]:
    data=json.loads(path.read_text())
    for k in ['sanctuary','companion','jeep','charger']:data[k][0]+=dx;data[k][2]+=dz
    data['transforms']['sanctuary']=mapping.TRANSFORMS['sanctuary'];path.write_text(json.dumps(data,indent=2)+'\n')
# Read shared live configuration at mutation time.
path=Path('src/work/world.json');data=json.loads(path.read_text());spawn=data['worldProfileData']['playerSpawnPosition']
if abs(spawn['x']-old[0])<20 and abs(spawn['z']-old[2])<20:spawn['x']+=dx;spawn['z']+=dz
path.write_text(json.dumps(data,indent=2)+'\n')
revision=hashlib.sha256((out/'detailed.glb').read_bytes()).hexdigest()[:16]
for path in [out/'detailed-version.json',Path('src/work/geographic/version.json')]:path.write_text(json.dumps(dict(revision=revision)))
Path('build/resort-blocks/bellagio/sanctuary-relocation.json').write_text(json.dumps(dict(fromPosition=old,toPosition=target,delta=[dx,0,dz],meshBatches=moved,reason='Original center was inside the newly restored mapped lake; new center clears road/sidewalk/building polygons by 26 m.'),indent=2))
print('Sanctuary moved',old,'->',target,'batches',moved)
