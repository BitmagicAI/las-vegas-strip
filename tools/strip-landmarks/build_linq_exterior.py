"""Rebuild LINQ exterior only. Preserve the entire High Roller, interiors and collision."""
from pathlib import Path
import sys,json
sys.path.insert(0,'tools/strip-landmarks')
s=Path('tools/strip-landmarks/build.py').read_text();stop=s.index("enter('linq','interior');")
ns={};exec(compile(s[:stop],'<LINQ exterior only>','exec'),ns);B=ns['B']
p=Path('build/strip-landmarks/linq-exterior.json');old=json.loads(p.read_text())
old['meshes']=[g for g in old['meshes'] if g['source'].startswith('wheel-')]+list(B.groups.values())
old['labels']=[g for g in old['labels'] if g['source'].startswith('wheel-')]+B.labels
p.write_text(json.dumps(old,separators=(',',':')))
p=Path('build/strip-landmarks/venues.json');vs=json.loads(p.read_text());v=next(v for v in vs if v['key']=='linq');v['views'].update(ns['spec']['views']);p.write_text(json.dumps(vs,separators=(',',':')))
print('LINQ',len(old['meshes']),'groups',sum(len(g['faces']) for g in old['meshes']),'triangles; all wheel/interior/collider files preserved')
