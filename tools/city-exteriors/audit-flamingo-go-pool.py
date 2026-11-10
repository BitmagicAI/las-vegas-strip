"""Check original pool geometry and unchanged installed neighbors."""
import json,math,hashlib
from pathlib import Path
p=Path('docs/project-records/flamingo-go-pool');data=json.loads(Path('build/strip-landmarks/flamingoGoPool-exterior.json').read_text());count=0;errors=[]
for g in data['meshes']:
 for f in g['faces']:
  count+=1;a,b,c=[g['vertices'][i]for i in f];u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  if not all(math.isfinite(x)for q in [a,b,c]for x in q)or sum(x*x for x in cross)<1e-16:errors.append({'source':g['source'],'face':f})
unchanged={}
for key in ['flamingoExterior','flamingoGarden','hgvFlamingoExterior']:
 for suffix in ['-exterior.glb','-exterior-collision.bin']:
  name=key+suffix;runtime=Path('runtime-assets/strip-landmarks')/name;installed=Path('build/optimized/build/strip-landmarks' if suffix.endswith('.glb') else 'build/strip-landmarks')/name
  assert runtime.read_bytes()==installed.read_bytes(),name
  unchanged[name]=hashlib.sha256(installed.read_bytes()).hexdigest()
c=json.loads(Path('build/strip-landmarks/flamingoGoPool-exterior-collision.json').read_text());r={'authoredTriangles':count,'collisionTriangles':len(c['indices'])//3,'unchangedNeighbors':unchanged,'errors':errors};(p/'geometry.json').write_text(json.dumps(r,indent=2)+'\n');print(r);assert not errors
