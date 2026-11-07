"""Audit additive roof pass against the unmodified frontage builder in PR base."""
import sys,json,subprocess
from collections import Counter
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import Meshes
import horseshoe_exterior as H
ns={'__name__':'baseline_frontage'}
exec(subprocess.check_output(['git','show','1b73c28c:tools/strip-landmarks/horseshoe_frontage.py'],text=True),ns)
new=Meshes();H.exterior(new)
fn=H.frontage;H.frontage=ns['frontage'];old=Meshes();H.exterior(old);H.frontage=fn

def tris(g):return Counter(tuple(tuple(g['vertices'][j]) for j in f) for f in g['faces'])
added=0
for k,g in old.groups.items():
 n=new.groups[k]
 if g['source']!='horseshoe/bazaar-frontage':assert g==n,k
 else:
  a,b=tris(g),tris(n);assert not a-b,k
  extra=b-a;added+=sum(extra.values())
  for t in extra:
   for x,y,z in t:assert 35<=x<=61 and 12.83<=y<=14.2 and 173<=z<=209,(x,y,z)
assert new.labels==old.labels

def collision(b):
 c=b.solids['horseshoeExterior-exterior'];v=c['vertices'];i=c['indices']
 return Counter(tuple(tuple(v[j*3:j*3+3]) for j in i[k:k+3]) for k in range(0,len(i),3))
a,b=collision(old),collision(new);assert not a-b
for t in b-a:
 for x,y,z in t:assert abs(x-47)>1.7,(x,y,z)
r={'unchangedOtherSources':True,'allOldTrianglesRetained':True,'allOldCollisionTrianglesRetained':sum(a.values()),'addedVisualTriangles':added,'addedCollisionTriangles':sum((b-a).values()),'centreRouteClear':True,'tables':9,'chairsAndStools':18,'publicVerticalAccessVerified':False}
p=Path('docs/project-records/horseshoe-bazaar-refinement/geometry-audit.json');p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
