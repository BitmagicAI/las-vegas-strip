"""Authoring regression: shore has one owner, hardware is submerged, repairs repeat safely."""
import sys,json,hashlib,argparse
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import Meshes
from bellagio_edge_ownership import reconcile,support_roadside_verge
parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path);args=parser.parse_args()
out=Path('build/resort-blocks/bellagio');doc=json.loads((out/'bellagioBlock-exterior.json').read_text());b=Meshes();b.groups={i:g for i,g in enumerate(doc['meshes'])}
b.solids['bellagioBlock-exterior']=json.loads((out/'bellagioBlock-exterior-collision.json').read_text())
report={'remainingCoplanarArea':reconcile(b)}
assert max(report['remainingCoplanarArea'].values())<1e-6,report
hardware=[v[1] for g in doc['meshes'] if g['source']=='lakefront-fountain-array' for v in g['vertices']]
report['hardwareTopY']=max(hardware);assert report['hardwareTopY']<=-1.6+1e-6
report['repeatedSupportTriangles']=support_roadside_verge(b,json.loads(Path('build/geographic-strip/city-meshes.json').read_text()));assert report['repeatedSupportTriangles']==0
if args.baseline:
 old=json.loads((args.baseline/'bellagioBlock-exterior.json').read_text())
 key=lambda g:(g['property'],g['source'],g['material'],g['detail'])
 current={key(g):g for g in doc['meshes']}
 allowed={'lakefront-lake','lakefront-fountain-array','lakefront-strip-promenade'};unchanged=0;changed=[]
 for g in old['meshes']:
  if g==current[key(g)]:unchanged+=1
  else:assert g['source'] in allowed;changed.append(key(g))
 report['unchangedExistingGroups']=unchanged;report['changedExistingGroups']=changed
 prior=json.loads((args.baseline/'bellagioBlock-exterior-collision.json').read_text());now=b.solids['bellagioBlock-exterior']
 assert now['vertices'][:len(prior['vertices'])]==prior['vertices'] and now['indices'][:len(prior['indices'])]==prior['indices']
 report['originalColliderPrefixPreserved']=True
 hashes=Path('build/probe/water-edge/protected-hashes.json')
 if hashes.exists():
  protected=json.loads(hashes.read_text())
  assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protected.items())
  report['protectedFilesUnchanged']=len(protected)
(out/'water-edge-geometry-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
