"""Verify a candidate changes only canopy geometry, with no collision or label edits."""
import argparse, json
from pathlib import Path
from common import np
from patch_citycenter63_shades import patch
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('candidate',type=Path);a=p.parse_args()
source=json.loads(a.source.read_text());candidate=json.loads(a.candidate.read_text())
expected,audit=patch(source)
assert candidate==expected
old=[g for g in source['meshes'] if not(g['source']=='ocean-prime-terrace' and g['material']=='blue')]
assert candidate['meshes'][:len(old)]==old
assert candidate['labels']==source['labels']
assert audit['shadeCount']==12 and not audit['collisionAdded']
added=candidate['meshes'][len(old):]
for g in added:
 v=np.asarray(g['vertices']);assert np.isfinite(v).all()
 assert v[:,1].min()>20.98 and v[:,1].max()<=21.281
 for f in g['faces']:
  tri=v[f];assert np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))>1e-9
print(json.dumps({'passed':True,'retainedGroups':len(old),'shadeCount':12,'labelsUnchanged':True,'collisionAdded':False}))
