from common import *
from flamingo_exterior import exterior,KEY,IDS
B=Meshes();meta=exterior(B);B.save_all();p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
p=OUT/'replacement-ids.json';ids=set(json.loads(p.read_text()));ids.update(IDS);from flamingo_podium_detail import IDS as PODIUM_IDS
ids.update(PODIUM_IDS);p.write_text(json.dumps(sorted(ids)))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')

# Preserve the replacement garden rotunda boundaries when rebuilding the parent.
if (OUT/"flamingoGarden-exterior.glb").exists():
 import subprocess
 subprocess.run([sys.executable,"tools/city-exteriors/cut-flamingo-garden.py"],check=True)

if (OUT/"flamingoGarden-exterior.glb").exists():
 subprocess.run([sys.executable,"tools/city-exteriors/open-flamingo-gallery-door.py"],check=True)
