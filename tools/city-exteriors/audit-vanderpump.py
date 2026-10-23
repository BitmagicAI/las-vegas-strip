import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,'build/south-strip/python')
import numpy as np
b=Path('.bitmagic/city-exterior-backups/vanderpump-2026-10-14');o=Path('build/strip-landmarks')
for f in ['vanderpump-interior.json','vanderpump-interior-collision.json','venues.json']:
 assert (b/f).read_bytes()==(o/f).read_bytes(),f
j=json.loads((o/'vanderpump-exterior.json').read_text());bad=[];n=0
for g in j['meshes']:
 v=np.array(g['vertices']);ix=np.array(g['faces']);assert np.isfinite(v).all();t=v[ix];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1);n+=len(ix)
 if (area<1e-9).any():bad.append([g['source'],g['material'],int((area<1e-9).sum())])
c=json.loads((o/'vanderpump-exterior-collision.json').read_text());assert max(c['indices'])<len(c['vertices'])//3
r=dict(triangles=n,batches=len(j['meshes']),degenerate=bad,interiorsAndVenueMetadataByteIdentical=True,collisionTriangles=len(c['indices'])//3)
Path('build/city-exteriors/vanderpump-audit.json').write_text(json.dumps(r,indent=2));print(r);assert not bad
