"""Remove prior owners, install guest cores, preserve unrelated local world edits."""
import json,struct,hashlib,sys,copy
from pathlib import Path
sys.path.insert(0,'tools/geographic-strip');import mapping
ROOT=Path('.');B=Path('build/resort-blocks');OUT=B/'cosmo'
# Remove nodes owned by the old block. Referenced buffers for other resorts are
# byte-for-byte preserved; orphaned meshes are not instantiated by GLTFLoader.
p=Path('build/geographic-strip/detailed.glb');raw=p.read_bytes();length,typ=struct.unpack_from('<II',raw,12);j=json.loads(raw[20:20+length]);removed=[]
for n in j.get('nodes',[]):
 if n.get('extras',{}).get('geographicOwner')=='cosmopolitan':
  removed.append(n.get('name'));n.pop('mesh',None);n.pop('children',None)
s=json.dumps(j,separators=(',',':')).encode();s+=b' '*((-len(s))%4);tail=raw[20+length:];p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(s)+len(tail))+struct.pack('<II',len(s),0x4e4f534a)+s+tail)
# Source ownership is evaluated before the original geographic transform.
old=json.load(open(mapping.BASE/'build/hotels/staged-vegas.mesh-level.json'))
names={k:{v['name'] for v in old[k] if mapping.owner(v['name'],mapping.center(v) if k=='colliders' else v['position'])=='cosmopolitan'} for k in ['colliders','lights','volumes','landmarks']}
data=json.load(open('src/work/geographic/level.json'));counts={}
for k,owned in names.items():
 before=len(data[k]);data[k]=[v for v in data[k] if v['name'] not in owned];counts[k]=before-len(data[k])
for p in [Path('src/work/geographic/level.json'),Path('build/geographic-strip/detailed.mesh-level.json')]:p.write_text(json.dumps(data,indent=2)+'\n')
manifest=json.load(open('src/work/vegas-visibility.json'));manifest['zones']=[z for z in manifest['zones'] if z.get('building')!='cosmopolitan'];manifest['portals']=[v for v in manifest['portals'] if 'cosmopolitan' not in v.get('buildings',[])]
Path('src/work/vegas-visibility.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Guest modules retain their custom set; no nonuniform scaling of furniture.
towers=json.load(open('src/work/hotels/towers.json'))
for t in towers:
 if t['id']=='cosmo-boulevard':t.update(origin=[-120,22.64,647],yaw=-1.5707963267948966,bays=6,floors=44,firstGuestFloor=2,source='guest-boulevard');t.pop('linear',None)
 if t['id']=='cosmo-chelsea':t.update(origin=[-322,22.64,668],yaw=-1.5707963267948966,bays=7,floors=44,firstGuestFloor=2,source='guest-chelsea');t.pop('linear',None)
Path('src/work/hotels/towers.json').write_text(json.dumps(towers,indent=2)+'\n')
# Door record names are scoped to the replaced block. New sliding doors are
# authored by the new block loader, and guest doors stay in HotelStreaming.
p=Path('src/work/world.json');w=json.loads(p.read_text());ds=w['worldProfileData']['doors'];gone=[d['id'] for d in ds if any(t in str(d).lower() for t in ['cosmo'])];w['worldProfileData']['doors']=[d for d in ds if d['id'] not in gone];p.write_text(json.dumps(w,indent=2)+'\n')
revision=hashlib.sha256(Path('build/geographic-strip/detailed.glb').read_bytes()).hexdigest()[:16]
for p in ['src/work/geographic/version.json','build/geographic-strip/detailed-version.json']:Path(p).write_text(json.dumps(dict(revision=revision)))
prior=json.loads((OUT/'ownership-report.json').read_text()) if (OUT/'ownership-report.json').exists() else {}
removed=list(set(removed+prior.get('legacyBatchNames',[])))
for k,v in prior.get('removedRecords',{}).items():counts[k]=max(counts.get(k,0),v)
gone=list(set(gone+prior.get('removedDoors',[])))
(OUT/'ownership-report.json').write_text(json.dumps(dict(removedLegacyBatches=max(len(removed),prior.get('removedLegacyBatches',0)),legacyBatchNames=removed,removedRecords=counts,removedDoors=gone,newOwner='build/resort-blocks/cosmo',preserved='All unrelated detailed GLB binary payloads; existing custom guest assets'),indent=2))
print('Installed replacement',len(removed),'legacy batches removed',counts)
