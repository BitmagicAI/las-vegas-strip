"""Replace only three lift control entries; static shaft collision stays in GLBs."""
from pathlib import Path
import json,shutil
root=Path('build/geographic-strip/access');bak=Path('.bitmagic/city-exterior-backups/pedestrian-lifts-access-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
p=root/'manifest.json'
if not(bak/p.name).exists():shutil.copy2(p,bak/p.name)
entries=json.loads(p.read_text())
for key in ['cosmoPedestrianLift','crystalsPedestrianLift','parkPedestrianLift']:
 d=json.loads(Path('build/city-exteriors/'+key+'-access.pending.json').read_text());f=root/(d['id']+'.json')
 if f.exists()and not(bak/f.name).exists():shutil.copy2(f,bak/f.name)
 f.write_text(json.dumps(d,separators=(',',':')));entries=[e for e in entries if e['id']!=d['id']];entries.append({k:d[k]for k in ['id','name','bounds','height','portals']})
p.write_text(json.dumps(entries,indent=2)+'\n');print('Installed 3 pedestrian lift access entries')
