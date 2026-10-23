"""Audit every pavement triangle, including road edges missed by route rays."""
import json
from pathlib import Path
import numpy as np
root=Path('build/resort-blocks/bellagio')
results=[]
for mesh in json.loads((root/'bellagioBlock-exterior.json').read_text())['meshes']:
 if mesh['source'] not in ['south-arrival-upper-pavement','south-arrival-lower-pavement']:continue
 p=np.array(mesh['vertices'])[mesh['faces']]
 n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);area=abs(n[:,1])
 valid=area>1e-8
 grades=np.linalg.norm(n[valid][:,[0,2]],axis=1)/area[valid]
 # At most 30% in this fitted ramp network; metre-high jagged edges fail.
 assert grades.max()<.30,(mesh['source'],float(grades.max()),p[valid][grades.argmax()].tolist())
 heights={}
 for x,y,z in p.reshape(-1,3):
  key=(round(x,5),round(z,5));old=heights.setdefault(key,y)
  assert abs(y-old)<1e-4,('surface crack',key,old,y)
 results.append(dict(source=mesh['source'],triangles=len(p),maxGrade=float(grades.max()),p95Grade=float(np.percentile(grades,95)),sharedVerticesContinuous=True))
assert len(results)==2
(root/'arrival-surface-audit.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
