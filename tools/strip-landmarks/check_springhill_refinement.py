"""Source route clearance; installed collision and walks remain separate gates."""
import json,sys
from pathlib import Path
sys.path.insert(0,'build/south-strip/python')
import numpy as np
root=Path('build/strip-landmarks')
def ray(o,d):
 e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.sum(e1*h,axis=1);safe=np.abs(det)>1e-9;inv=np.zeros(len(det));inv[safe]=1/det[safe];s=o-tri[:,0];u=inv*np.sum(s*h,axis=1);q=np.cross(s,e1);vv=inv*np.sum(d*q,axis=1);t=inv*np.sum(e2*q,axis=1)
 return t[safe&(u>=-1e-7)&(vv>=-1e-7)&(u+vv<=1+1e-7)&(t>=0)]

reports=[]
for key in ['springhillExterior']:
 chunks=[]
 for suffix in ['exterior','interior']:
  f=root/(key+'-'+suffix+'-collision.json')
  if not f.exists():continue
  c=json.loads(f.read_text());v=np.array(c['vertices']).reshape(-1,3);chunks.append(v[np.array(c['indices']).reshape(-1,3)])
 tri=np.concatenate(chunks);missing=[];blocked=[];samples=0
 meta=json.loads((root/(key+'-metadata.json')).read_text())
 for route in meta['routes']:
  for seg,(a,b) in enumerate(zip(route['points'],route['points'][1:])):
   a,b=np.array(a),np.array(b);d=b-a;length=np.linalg.norm(d);direction=d/length;across=np.array([direction[2],0,-direction[0]])
   for lane in [-.3,0,.3]:
    start=a+lane*across
    for i,t in enumerate(np.linspace(0,1,max(8,int(length/.2)))):
     if not route['name'].startswith('Roof'):continue
     p=start+d*t;hits=ray(p+[0,2,0],np.array([0,-1,0]));samples+=1
     if route['name'].startswith('Roof') and not np.any(abs(hits-2)<.06):missing.append([route['name'],seg,lane,i])
    for height in [.35,1,1.7]:
     hits=ray(start+[0,height,0],direction)
     if np.any(hits<length-1e-5):blocked.append([route['name'],seg,lane,height,float(min(hits))])
 reports.append(dict(key=key,triangles=len(tri),finite=bool(np.all(np.isfinite(tri))),floorSamples=samples,missingFloor=missing,obstructions=blocked))
Path('.bitmagic/springhill-source-route-report.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports));assert all(r['finite'] and not r['missingFloor'] and not r['obstructions'] for r in reports)
