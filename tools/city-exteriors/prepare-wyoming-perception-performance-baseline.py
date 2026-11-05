"""Copy the exact pre-PR512 assets from local Git LFS storage for browser-only A/B."""
import hashlib,json,subprocess,shutil
from pathlib import Path
base='55d96d49'
gitdir=Path(subprocess.check_output(['git','rev-parse','--git-common-dir'],text=True).strip()).resolve()
out=Path('build/city-exteriors/wyoming-perception-performance-baseline');out.mkdir(exist_ok=True)
rows=[]
for rel in ['baked/cells/cell-1_-4.bin','baked/cells/cell-2_-6.bin','strip-landmarks/wyoming17Frontage-exterior.glb','strip-landmarks/perceptionMuseum-exterior.glb']:
 pointer=subprocess.check_output(['git','show',base+':runtime-assets/'+rel],text=True)
 oid=pointer.split('oid sha256:')[1].splitlines()[0]
 source=gitdir/'lfs/objects'/oid[:2]/oid[2:4]/oid
 assert source.exists(),f'Missing local LFS object: {oid}'
 assert hashlib.sha256(source.read_bytes()).hexdigest()==oid
 target=out/Path(rel).name;shutil.copyfile(source,target)
 rows.append({'path':rel,'oid':oid,'file':str(target)})
(out/'manifest.json').write_text(json.dumps({'base':base,'files':rows},indent=2)+'\n')
