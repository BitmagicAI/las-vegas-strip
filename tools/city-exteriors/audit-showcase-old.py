"""Check newly authored rotunda faces, including duplicates and water orientation."""
import json,math
from pathlib import Path
p=json.loads(Path('build/strip-landmarks/showcase-exterior.json').read_text());seen=set();bad=[];count=0
for g in p['meshes']:

 for f in g['faces']:
  count+=1;pts=[g['vertices'][i] for i in f]
  if not all(math.isfinite(x) for pt in pts for x in pt):bad.append(('nonfinite',count));continue
  a,b,c=pts;u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  if sum(x*x for x in n)<1e-16:bad.append(('degenerate',count))
  key=tuple(sorted(tuple(round(x,6) for x in pt) for pt in pts))
  if key in seen:bad.append(('duplicate',count))
  seen.add(key)
  if g['material']=='cp_pool' and n[1]<=0:bad.append(('water-backface',count))
r={'triangles':count,'errors':bad,'scope':'All Showcase finite, nonzero, nonduplicate triangle geometry and upward water faces; not a comprehensive intersection audit.'};Path('build/city-exteriors/showcase-old-geometry-audit.json').write_text(json.dumps(r,indent=2));print(r);assert not bad
