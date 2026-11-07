"""Scoped TI authoring; permit only the documented guest entry column cut."""
from common import *
from collections import Counter
import subprocess
import ti_parking
key=ti_parking.KEY
baseline={}
exec(subprocess.check_output(['git','show','b8cb05f17efb1ac0d9a05db1889668a4a8d5e083:tools/strip-landmarks/ti_parking.py'],text=True),baseline)
original=Meshes();baseline['exterior'](original)
def faces(data):
 v=np.asarray(data['vertices']).reshape(-1,3)
 return Counter(tuple(tuple(float(x) for x in v[i]) for i in data['indices'][j:j+3]) for j in range(0,len(data['indices']),3))
B=Meshes();ti_parking.exterior(B)
old=faces(original.solids[key+'-exterior']);new=faces(B.solids[key+'-exterior'])
removed=list((old-new).elements());added=list((new-old).elements())
assert removed and added,'Expected documented entry-column correction'
for tri in removed+added:
 for x,y,z in tri:
  assert -41<x<-32 and -965.3<z<-946.7 and -.01<=y<=17.95,(x,y,z)
for tri in added:
 assert min(p[1] for p in tri)>=3.44-1e-6,tri
for label in B.labels:label['detail']=0
B.save_all()
report={'removedTriangles':len(removed),'addedTriangles':len(added),'scope':'Guest facade and first interior column in entry aperture only; all other collision triangles identical','triangles':sum(len(g['faces']) for g in B.groups.values())}
Path('docs/project-records/ti-parking-refinement/source-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
