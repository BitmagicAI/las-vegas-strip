"""Building-only runs must preserve every prior road/landscape mesh verbatim."""
import json,hashlib,gc
from pathlib import Path

def hashes(path):
 data=json.load(open(path));out={}
 for g in data:
  m=g['material']
  if m in ('building-estimated','building-tagged','utility') or m.startswith('tag/'):continue
  out[g['cell']+'|'+m]=hashlib.sha256(json.dumps(g,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 del data;gc.collect();return out
old=hashes('build/city-exteriors/before/mgm/city-meshes.json');new=hashes('build/geographic-strip/city-meshes.json')
report=dict(oldGroups=len(old),newGroups=len(new),changed=[k for k in old if old[k]!=new.get(k)],added=[k for k in new if k not in old])
Path('build/city-exteriors/mgm-preservation.json').write_text(json.dumps(report,indent=2));print(report)
assert not report['changed'] and not report['added']
