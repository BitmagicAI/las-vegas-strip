import sys,subprocess,json
from collections import Counter
sys.path.insert(0,'tools/strip-landmarks')
from common import *
import wynn_encore
old={};exec(subprocess.check_output(['git','show','c80070da:tools/strip-landmarks/wynn_encore.py']),old)
a,b=Meshes(),Meshes();old['exterior'](a);wynn_encore.exterior(b)
def tris(m):
 c=m.solids['wynnEncoreExterior-exterior'];v=c['vertices'];ind=c['indices'];return Counter(tuple(tuple(v[j*3:j*3+3]) for j in ind[i:i+3]) for i in range(0,len(ind),3))
x,y=tris(a),tris(b)
other=lambda m:sorted(json.dumps(g,sort_keys=True) for g in m.groups.values() if g['source']!='podium/way/156626862')
assert other(a)==other(b)
assert not x-y
report={'oldTriangles':sum(x.values()),'newTriangles':sum(y.values()),'removed':sum((x-y).values()),'added':sum((y-x).values()),'otherSourceGroupsIdentical':True,'sourceTriangles':sum(len(g['faces']) for g in b.groups.values()),'sourceBatches':len(b.groups)}
Path('docs/project-records/wynn-encore-courts-refinement/source-collision-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
