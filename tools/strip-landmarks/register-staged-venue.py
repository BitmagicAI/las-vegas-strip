"""Register new local architecture only after its export is present and valid."""
import json,sys,struct
from pathlib import Path
key=sys.argv[1];root=Path('build/strip-landmarks');p=root/(key+'-exterior.glb')
raw=p.read_bytes();assert len(raw)>20 and struct.unpack_from('<I',raw)[0]==0x46546c67,p
assert (root/(key+'-exterior-collision.json')).is_file()
entry=json.loads((root/(key+'-venue.pending.json')).read_text());assert entry['key']==key
p=root/'venues.json';entries=json.loads(p.read_text());entries=[e for e in entries if e['key']!=key];entries.append(entry);p.write_text(json.dumps(entries,separators=(',',':')))
print('Registered',key)
