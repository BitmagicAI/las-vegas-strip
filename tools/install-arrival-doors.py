"""Register local authored leaves without any upload. Retain engine door physics."""
from pathlib import Path
import json,hashlib,shutil
root=Path('build/arrival-reconstruction')
p=Path('src/work/world.json');world=json.loads(p.read_text())
# Re-read on every invocation: the live editor owns other transforms in this file.
for style in ['bronze','silver','black','sage']:
 asset='arrival-door-'+style;f=root/('door-'+style+'.glb');rev=hashlib.sha256(f.read_bytes()).hexdigest()[:12]
 record={'id':asset,'name':asset,'type':'glb','url':'/build/arrival-reconstruction/'+f.name+'?v='+rev,'size':f.stat().st_size,'targetHeight':4.2}
 world['assets']=[a for a in world['assets'] if a['id']!=asset]+[record]
extra=json.loads((root/'extra-doors.json').read_text());doors=world['worldProfileData']['doors'];ids={d['id'] for d in doors}
for d in extra:
 if d['id'] not in ids:doors.append(d)
changes=[]
overrides=json.loads((root/'door-overrides.json').read_text())
for d in doors:
 if d['id'] in overrides:d.update(overrides[d['id']])
 name=d['id'].lower()
 if any(k in name for k in ['service','staff','stores','medical','security','stock']):continue
 # Only public exterior/mall doors; streamed private doors remain set-specific.
 if not any(k in name for k in ['entrance','exit','caesars_main','caesars_garden','citycenter','interiors /','arrival / veer']):continue
 style='sage' if 'paris' in name else 'bronze' if any(k in name for k in ['bellagio','caesars','flamingo','waldorf']) else 'black' if any(k in name for k in ['crystals','cosmopolitan','hollywood']) else 'silver'
 d['assetId']='arrival-door-'+style;d['thickness']=.22;changes.append(d['id'])
p.write_text(json.dumps(world,indent=2)+'\n')
(root/'door-installation.json').write_text(json.dumps({'doors':changes,'assetsLocal':True},indent=2))
print('Local glass door leaves registered:',len(changes))
