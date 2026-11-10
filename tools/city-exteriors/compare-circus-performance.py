"""Compare optimized runtime assets, never invalidating source timestamps or loader manifest."""
from pathlib import Path
import subprocess,shutil,hashlib
base=Path('build/optimized/build/strip-landmarks');old=Path('.bitmagic/city-exterior-backups/circus-refinement/optimized-original');old.mkdir(exist_ok=True)
saved=old.parent/'optimized-installed-comparison';saved.mkdir(exist_ok=True)
files=[k+'-exterior.glb' for k in ['circusExterior']];hashes={}
for f in files:
 if not (old/f).exists():shutil.copy2(Path('runtime-assets/strip-landmarks')/f,old/f)
 hashes[f]=hashlib.sha256((base/f).read_bytes()).hexdigest();shutil.copy2(base/f,saved/f)
try:
 for variant in ['installed','original']:
  if variant=='original':
   for f in files:shutil.copy2(old/f,base/f)
  subprocess.run(['node','tools/probe-eval.mjs','tools/city-exteriors/probe-circus-refinement-pair.js','--out','build/city-exteriors/circus-optimized-paired-'+variant],check=True)
finally:
 for f in files:
  shutil.copy2(saved/f,base/f)
  assert hashlib.sha256((base/f).read_bytes()).hexdigest()==hashes[f]
 print('Optimized installed GLBs restored and hashes verified; source timestamps untouched.',flush=True)
