import sys,types,subprocess,json,hashlib
sys.path.insert(0,'tools/strip-landmarks')
import planet_hollywood as new
from common import Meshes
old=types.ModuleType('old_ph');exec(subprocess.check_output(['git','show','f65a541aa9220beb4202840a15ca76483bd9da2f:tools/strip-landmarks/planet_hollywood.py'],text=True),old.__dict__)
def build(m):
 b=Meshes()
 for f in [m.exterior,m.towers,m.harmon_corner,m.pool_furniture]:f(b)
 return b
a,b=build(old),build(new)
def digest(g):return hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest()
changed=[str(k) for k in a.groups.keys()|b.groups.keys() if digest(a.groups.get(k))!=digest(b.groups.get(k))]
unrelated=[k for k in changed if 'harmon-corner' not in k]
la=[x for x in a.labels if x.get('source')!='harmon-corner'];lb=[x for x in b.labels if x.get('source')!='harmon-corner']
r={'changedGroups':changed,'unrelatedChanged':unrelated,'unrelatedLabelsIdentical':la==lb,'collisionIdentical':a.solids==b.solids,'beforeTriangles':sum(len(g['faces']) for g in a.groups.values()),'afterTriangles':sum(len(g['faces']) for g in b.groups.values())}
open('docs/project-records/harmon-refinement/source-preservation.json','w').write(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));assert not unrelated and la==lb and a.solids==b.solids
