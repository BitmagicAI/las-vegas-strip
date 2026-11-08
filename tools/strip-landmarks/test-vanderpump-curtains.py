"""Assert the bounded fabric patch preserves all other geometry and metadata."""
import argparse,json
from pathlib import Path
from common import np
from patch_vanderpump_curtains import patch
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('candidate',type=Path);a=p.parse_args()
s=json.loads(a.source.read_text());c=json.loads(a.candidate.read_text());expected,audit=patch(s);assert c==expected
old=[m for m in s['meshes'] if m['material'] not in ['vp-fabric','vp-cushion']];assert c['meshes'][:len(old)]==old
original=next(m for m in s['meshes'] if m['material']=='vp-cushion');new=c['meshes'][len(old)];assert original['vertices']==new['vertices'] and original['faces']==new['faces']
assert s['labels']==c['labels'] and not audit['collisionAdded']
for m in c['meshes'][len(old)+1:]:
 v=np.asarray(m['vertices']);assert np.isfinite(v).all()
 for f in m['faces']:
  tri=v[f];assert np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))>1e-9
print(json.dumps({'passed':True,**audit}))
