"""Preserve every original triangle/label while splitting upper glass and adding details."""
import argparse,json
from pathlib import Path
from common import np,footprint,Point
from patch_atomic_terrace import patch
from atomic_terrace_fans import FAN_CENTERS
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('candidate',type=Path);a=p.parse_args()
s=json.loads(a.source.read_text());c=json.loads(a.candidate.read_text());expected,audit=patch(s);assert c==expected
for old,new in zip(s['meshes'],c['meshes']):
 if old['source']=='podium/south-terrace' and old['material']=='ag-glass':
  guard=c['meshes'][len(s['meshes'])];assert old['vertices']==new['vertices']==guard['vertices'];assert sorted(old['faces'])==sorted(new['faces']+guard['faces'])
 else:assert old==new
assert s['labels']==c['labels'] and not audit['collisionAdded']
for x,z in FAN_CENTERS:assert footprint('way/1553042969').contains(Point(x,z).buffer(1.7))
for m in c['meshes'][len(s['meshes'])+1:]:
 v=np.asarray(m['vertices']);assert np.isfinite(v).all()
 for f in m['faces']:
  t=v[f];assert np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>1e-9
print(json.dumps({'passed':True,**audit}))
