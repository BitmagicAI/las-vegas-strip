import json
from pathlib import Path
old=Path('.bitmagic/city-exterior-backups/atomic-golf-2026-10-19');new=Path('build/geographic-strip')
a=json.loads((old/'city-meshes.json').read_text());b=json.loads((new/'city-meshes.json').read_text())
def building(g):return g['material'] in ('building-estimated','building-tagged','utility') or g['material'].startswith('tag/')
def keys(gs,pred):
 out=set()
 for g in gs:
  if not pred(g):continue
  vs=g['vertices']
  for f in g['faces']:out.add((g['material'],tuple(sorted(tuple(round(c,4) for c in vs[i]) for i in f))))
 return out
ka,kb=keys(a,building),keys(b,building);removed=ka-kb;added=kb-ka
outside=[(m,vs) for m,vs in removed|added if any(not(1601<v[0]<1649 and -3766<v[2]<-3652) for v in vs)]
report=dict(unrelatedMeshesExactlyIdentical=[g for g in a if not building(g)]==[g for g in b if not building(g)],removedBuildingTriangles=len(removed),addedBuildingTriangles=len(added),changesOutsideScope=len(outside))
Path('build/city-exteriors/atomic-ownership-audit.json').write_text(json.dumps(report,indent=2));print(report);assert report['unrelatedMeshesExactlyIdentical'] and not outside and all(m=='utility' and max(v[1] for v in vs)<=3.5 for m,vs in added)
