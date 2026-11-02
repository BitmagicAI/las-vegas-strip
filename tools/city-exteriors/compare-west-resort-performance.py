"""Controlled local current/original comparison, restoring installed assets even on failure."""
from pathlib import Path
import subprocess,shutil,json,hashlib
base=Path('build/strip-landmarks');old=Path('.bitmagic/city-exterior-backups/west-resort-amenities');saved=old/'installed-comparison';saved.mkdir(exist_ok=True)
files=[k+'-exterior.glb' for k in ['goldCoastExterior','wyndhamDesertBlue']];hashes={}
for f in files:
 hashes[f]=hashlib.sha256((base/f).read_bytes()).hexdigest();shutil.copyfile(base/f,saved/f)
try:
 for variant in ['installed','original']:
  if variant=='original':
   for f in files:shutil.copyfile(old/f,base/f)
  subprocess.run(['node','tools/probe-eval.mjs','tools/city-exteriors/probe-west-resort-performance.js','--out','build/city-exteriors/west-resort-paired-'+variant],check=True)
finally:
 for f in files:
  shutil.copyfile(saved/f,base/f)
  assert hashlib.sha256((base/f).read_bytes()).hexdigest()==hashes[f]
 print('Installed GLBs restored and hashes verified.',flush=True)
