import json,hashlib
from pathlib import Path
old=Path('.bitmagic/city-exterior-backups/showcase-ownership-2026-10-19');new=Path('build/geographic-strip')
a=json.loads((old/'city-meshes.json').read_text());b=json.loads((new/'city-meshes.json').read_text())
def building(g):return g['material'] in ('building-estimated','building-tagged','utility') or g['material'].startswith('tag/')
def keys(gs):
 out=set()
 for g in gs:
  if not building(g):continue
  vs=g['vertices']
  for f in g['faces']:out.add((g['material'],tuple(sorted(tuple(round(c,4) for c in vs[i]) for i in f))))
 return out
ka,kb=keys(a),keys(b);removed=ka-kb;added=kb-ka
outside=[]
for kind,ts in [('removed',removed),('added',added)]:
 for mat,vs in ts:
  if any(not (30<=v[0]<=220 and 1250<=v[2]<=1550) for v in vs):outside.append((kind,mat,vs))
report={'nonBuildingMeshesExactlyIdentical':[g for g in a if not building(g)]==[g for g in b if not building(g)],'removedTriangles':len(removed),'addedTriangles':len(added),'changesOutsideShowcaseBounds':len(outside),'outsideExamples':outside[:5]}
oldindex={x['id']:x for x in json.loads((old/'building-index.json').read_text())};newindex={x['id']:x for x in json.loads((new/'building-index.json').read_text())};report['removedIDs']=sorted(oldindex.keys()-newindex.keys());report['changedOtherIndexRows']=[k for k in oldindex.keys()&newindex.keys() if oldindex[k]!=newindex[k]]
print(json.dumps(report,indent=2));Path('build/city-exteriors/showcase-ownership-audit.json').write_text(json.dumps(report,indent=2))
assert report['nonBuildingMeshesExactlyIdentical'];assert not outside;assert not report['changedOtherIndexRows']
