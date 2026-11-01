"""Audit authored triangles and perimeter route floor support before installation."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'tools/strip-landmarks')
from shapely.geometry import Point,Polygon
from shapely.ops import unary_union
REC=Path('docs/project-records/rio-palms-amenities')
for key in ['rio','palms']:
 data=json.loads(Path('build/strip-landmarks/'+key+'Amenities-exterior.json').read_text());total=0;bad=0
 for g in data['meshes']:
  v=np.array(g['vertices']).reshape(-1,3);f=np.array(g['faces']).reshape(-1,3);t=v[f];total+=len(f);bad+=int((np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)<1e-8).sum())
 assert bad==0,(key,bad)
 collision=json.loads(Path('build/strip-landmarks/'+key+'Amenities-exterior-collision.json').read_text());v=np.array(collision['vertices']).reshape(-1,3);t=v[np.array(collision['indices']).reshape(-1,3)]
 floors=unary_union([Polygon(a[:,[0,2]]) for a in t if np.max(abs(a[:,1]-.32))<.001 and Polygon(a[:,[0,2]]).area>1e-8])
 samples=0;unsupported=0
 for route in json.loads((REC/(key+'-routes.json')).read_text()):
  for a,b in zip(route['points'],route['points'][1:]):
   for u in np.linspace(0,1,max(2,int(np.linalg.norm(np.array(a)-np.array(b))/.3)+1)):
    p=np.array(a)*(1-u)+np.array(b)*u;samples+=1;unsupported+=not floors.buffer(.01).covers(Point(p[0],p[2]))
 assert unsupported==0,(key,unsupported)
 report=dict(triangles=total,degenerateTriangles=bad,collisionTriangles=len(t),routeSamples=samples,unsupportedSamples=unsupported,scope='Authored source only; installed preservation, visual and movement checks still required')
 (REC/(key+'-source-check.json')).write_text(json.dumps(report,indent=2)+'\n');print(key,report)
