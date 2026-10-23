"""Install validated local lift/corridor access without rebuilding other entries."""
from pathlib import Path
import json,shutil
root=Path('build/geographic-strip/access');bak=Path('.bitmagic/city-exterior-backups/harmon-access-2026-10-21');bak.mkdir(parents=True,exist_ok=True)
for p in [root/'manifest.json',root/'way-1421481101.json',root/'harmon-bridge-atrium.json']:
 if p.exists()and not(bak/p.name).exists():shutil.copy2(p,bak/p.name)
manifest=json.loads((root/'manifest.json').read_text())
for path in ['build/city-exteriors/harmon-east-lift-access.pending.json','build/city-exteriors/harmon-bridge-passage.pending.json']:
 data=json.loads(Path(path).read_text());(root/(data['id']+'.json')).write_text(json.dumps(data,separators=(',',':')))
 manifest=[e for e in manifest if e['id']!=data['id']];manifest.append({k:data[k]for k in ['id','name','bounds','height','portals']})
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Installed Harmon lift and bridge-floor access')
