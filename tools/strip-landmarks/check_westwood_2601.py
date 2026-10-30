"""Source-only clearance regression; installed walks remain a separate gate."""
import json,sys
sys.path.insert(0,'build/south-strip/python')
import numpy as np
from pathlib import Path
root=Path('build/strip-landmarks');c=json.loads((root/'westwood-2601-exterior-collision.json').read_text());v=np.array(c['vertices']).reshape(-1,3);tri=v[np.array(c['indices']).reshape(-1,3)]
meta=json.loads((root/'westwood-2601-metadata.json').read_text());a,b=np.array(meta['routes'][0]['points'])
def ray(o,d):
 e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.sum(e1*h,axis=1);safe=np.abs(det)>1e-9;inv=np.zeros(len(det));inv[safe]=1/det[safe];s=o-tri[:,0];u=inv*np.sum(s*h,axis=1);q=np.cross(s,e1);vv=inv*np.sum(d*q,axis=1);t=inv*np.sum(e2*q,axis=1)
 return t[safe&(u>=-1e-7)&(vv>=-1e-7)&(u+vv<=1+1e-7)&(t>=0)]
missing=[];heights=[]
for i,t in enumerate(np.linspace(0,1,45)):
 p=a+(b-a)*t;o=p+np.array([0,2,0]);hits=ray(o,np.array([0,-1,0]));hits=hits[hits<=3]
 if not len(hits):missing.append(i)
 else:heights.append(float(o[1]-min(hits)))
d=b-a;dist=np.linalg.norm(d);hits=ray(a+[0,1.6,0],d/dist);blocked=bool(np.any(hits<dist))
report=dict(finite=bool(np.all(np.isfinite(v))),triangles=len(tri),rampSamples=45,missingFloor=missing,bodyHeightObstruction=blocked,rampHeightRange=[min(heights),max(heights)],maxSampleStep=max(abs(np.diff(heights))))
# Walk along the pool deck immediately adjacent to the hotel wall. A centre-line
# ramp check alone misses this half-metre gap at the back of the courtyard.
forward=(b-a)[[0,2]];forward/=np.linalg.norm(forward)
local_z=-forward;local_x=np.array([local_z[1],-local_z[0]])
centre=np.array(meta['center'])[[0,2]]
deck_missing=[]
for i,x in enumerate(np.linspace(-33,-9,49)):
 xz=centre+local_x*x+local_z*(41*.3048/2+.20)
 hits=ray(np.array([xz[0],2,xz[1]]),np.array([0,-1,0]))
 if not np.any((hits>=1.7)&(hits<=2)):deck_missing.append(i)
report['hotelDeckSamples']=49;report['hotelDeckMissingFloor']=deck_missing
Path('.bitmagic/w26-source-route-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));assert report['finite'] and not missing and not blocked and report['maxSampleStep']<.02 and not deck_missing
