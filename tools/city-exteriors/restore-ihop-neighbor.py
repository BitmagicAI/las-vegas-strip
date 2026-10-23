"""Keep only intended motel-shell deletion; preserve every other city triangle."""
import json
from pathlib import Path
old=Path('.bitmagic/city-exterior-backups/ihop-2026-10-19');out=Path('build/geographic-strip')
a=json.loads((old/'city-meshes.json').read_text());b=json.loads((out/'city-meshes.json').read_text())
def key(vs):return tuple(sorted(tuple(round(c,4) for c in v) for v in vs))
def building(g):return g['material'] in ('building-estimated','building-tagged','utility') or g['material'].startswith('tag/')
def keys(gs):return {key([g['vertices'][i] for i in f]) for g in gs if building(g) for f in g['faces']}
removed=keys(a)-keys(b);target={vs for vs in removed if all(1771<v[0]<1810 and -3758<v[2]<-3723 for v in vs)}
assert len(target)==10,len(target)
for g in a:
 if building(g):g['faces']=[f for f in g['faces'] if key([g['vertices'][i] for i in f]) not in target]
(out/'city-meshes.json').write_text(json.dumps(a,separators=(',',':')))
c=json.loads((old/'city-colliders.json').read_text())
for cell in c:
 v=cell['vertices'];idx=cell['indices'];cell['indices']=[i for k in range(0,len(idx),3) if key([v[j*3:j*3+3] for j in idx[k:k+3]]) not in target for i in idx[k:k+3]]
(out/'city-colliders.json').write_text(json.dumps(c,separators=(',',':')))
print('Removed only',len(target),'obsolete motel triangles; other meshes/collision restored exactly.')
