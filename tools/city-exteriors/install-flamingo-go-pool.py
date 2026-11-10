"""Append only the pool venue; preserve every other venue and asset byte-for-byte."""
import json,hashlib
from pathlib import Path
base=Path('build/strip-landmarks');key='flamingoGoPool';meta=json.loads((base/(key+'-venue.pending.json')).read_text());p=base/'venues.json';venues=json.loads(p.read_text());others=[v for v in venues if v['key']!=key];p.write_text(json.dumps(others+[meta],separators=(',',':')))
assert [v for v in json.loads(p.read_text()) if v['key']!=key]==others
(base/'version.json').write_text(json.dumps({'revision':hashlib.sha256((base/(key+'-exterior.glb')).read_bytes()+p.read_bytes()).hexdigest()[:16]}))
print('Installed only',key,'preserved',len(others),'other venues')
