from common import *
from planet_hollywood import exterior,towers,harmon_corner,pool_furniture,KEY
B=Meshes();meta=exterior(B);towers(B);harmon_corner(B);pool_furniture(B);meta["building"]="planet-hollywood";B.save_all()
p=OUT/'venues.json';v=json.loads(p.read_text());v=[x for x in v if x['key']!=KEY];v.append(meta);p.write_text(json.dumps(v,separators=(',',':')))
print(KEY,len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles')

# Preserve the surveyed public bridge-floor apertures after future facade exports.
import subprocess
subprocess.run([sys.executable,'tools/city-exteriors/open-harmon-bridge-portals.py','--planet-only'],check=True)
