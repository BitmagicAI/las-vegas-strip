"""Install local assets/metadata; never registers or uploads assets."""
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/geographic-strip';WORK=ROOT/'src/work'
for src,dest in {'towers.json':'hotels/towers.json','review.json':'public-resorts/review.json','visibility.json':'vegas-visibility.json','detailed.mesh-level.json':'geographic/level.json','detailed-version.json':'geographic/version.json','anchors.json':'geographic/anchors.json'}.items():shutil.copyfile(OUT/src,WORK/dest)
# The Paris lift's positions (ParisLift.ts) come from the remapped mission data; the rest of that file belongs to the
# zombie game built on the city (vegas-afterlight-game), not to the city.
missions=json.loads((OUT/'vegas-missions.json').read_text())
lift=json.loads((WORK/'paris-lift.json').read_text());lift['paris']={k:missions['paris'][k] for k in lift['paris']}
(WORK/'paris-lift.json').write_text(json.dumps(lift,indent=2)+'\n')
# Read the live world at mutation time so unrelated editor changes survive.
p=WORK/'world.json';w=json.loads(p.read_text());profile=w['worldProfileData'];updates={d['id']:d for d in json.loads((OUT/'doors.json').read_text())}
profile['doors']=[updates.get(d['id'],d) for d in profile['doors']]
spawn=next(v for v in json.loads((OUT/'detailed.mesh-level.json').read_text())['landmarks'] if v['name']=='spawn')['position'];profile['playerSpawnPosition']=dict(zip(('x','y','z'),spawn));profile['groundWorldSizeX']=4900;profile['groundWorldSizeZ']=8700
p.write_text(json.dumps(w,indent=2)+'\n')
print('Local geographic assets installed. No asset uploads.')

# Replacement blocks own their geometry/cores after a geographic rebuild.
if (ROOT/'build/resort-blocks/cosmo/version.json').exists():
 import subprocess,sys
 subprocess.run([sys.executable,str(ROOT/'tools/resort-blocks/install_cosmopolitan.py')],cwd=ROOT,check=True)

if (ROOT/'build/resort-blocks/bellagio/version.json').exists():
 import subprocess,sys
 subprocess.run([sys.executable,str(ROOT/'tools/resort-blocks/install_bellagio.py')],cwd=ROOT,check=True)

if (ROOT/'build/resort-blocks/paris/version.json').exists():
 import subprocess,sys
 subprocess.run([sys.executable,str(ROOT/'tools/resort-blocks/install_paris.py')],cwd=ROOT,check=True)

# Preserve the authored Waldorf exterior owner after legacy regeneration.
if Path("build/strip-landmarks/waldorfExterior-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/install-waldorf.py")

# Preserve mapped Caesars tower ownership and its existing guest-core fit.
if Path("build/strip-landmarks/caesarsExterior-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/install-caesars.py")

# Retain the mapped Flamingo wings, marquee and fitted existing guest core.
if Path("build/strip-landmarks/flamingoExterior-exterior.glb").exists():
 import runpy
 runpy.run_path("tools/city-exteriors/install-flamingo.py")
 if Path("tools/city-exteriors/install-flamingo-podium.py").exists():runpy.run_path("tools/city-exteriors/install-flamingo-podium.py")
 runpy.run_path("tools/city-exteriors/install-horseshoe.py")
