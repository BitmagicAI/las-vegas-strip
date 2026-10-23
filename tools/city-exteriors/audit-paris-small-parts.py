"""Read-only source ownership check for remaining Paris mapped components."""
import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks');from common import *
ids=['way/114697072','way/114697073','way/1424222076'];ps={i:footprint(i).buffer(.005)for i in ids};out={i:[]for i in ids}
for g in json.loads(Path('build/geographic-strip/city-meshes.json').read_text()):
 if not(g['material']in('building-tagged','building-estimated','utility')or g['material'].startswith('tag/')):continue
 for f in g['faces']:
  vs=[g['vertices'][k]for k in f]
  for i,p in ps.items():
   if all(p.covers(Point(v[0],v[2]))for v in vs):out[i].append(dict(material=g['material'],vertices=vs))
Path('build/city-exteriors/paris-small-parts-owner-audit.json').write_text(json.dumps(out,indent=2));print({i:len(a)for i,a in out.items()})
