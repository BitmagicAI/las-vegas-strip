import json
from pathlib import Path
old=Path('.bitmagic/city-exterior-backups/citycenter63-2026-10-19');new=Path('build/geographic-strip')
a=json.loads((old/'city-meshes.json').read_text());b=json.loads((new/'city-meshes.json').read_text())
def building(g):return g['material'] in ('building-estimated','building-tagged','utility') or g['material'].startswith('tag/')
def bridge(g):return g['cell'] in ['-1,4','-1,5'] and g['material'] in ['bridge-metal','bridge-concrete','bridge-glass','bridge-light']
def keys(gs,pred):
 out=set()
 for g in gs:
  if not pred(g):continue
  vs=g['vertices']
  for f in g['faces']:out.add((g['material'],tuple(sorted(tuple(round(c,4) for c in vs[i]) for i in f))))
 return out
ka,kb=keys(a,building),keys(b,building);removed=ka-kb;added=kb-ka
ra,rb=keys(a,bridge),keys(b,bridge)
outside=[(mat,vs) for mat,vs in removed|added if any(not(-168<v[0]<-48 and 778<v[2]<856) for v in vs)]
railOutside=[(mat,vs) for mat,vs in ra-rb if any(not(-111<v[0]<-36 and 771<v[2]<862 and 6.07<v[1]<7.41) for v in vs)]
report=dict(unrelatedMeshesExactlyIdentical=[g for g in a if not building(g) and not bridge(g)]==[g for g in b if not building(g) and not bridge(g)],removedBuildingTriangles=len(removed),addedBuildingTriangles=len(added),buildingChangesOutsideScope=len(outside),removedBridgeGuardTriangles=len(ra-rb),addedBridgeGuardTriangles=len(rb-ra),guardChangesOutsideScope=len(railOutside),examples=outside[:3])
Path('build/city-exteriors/citycenter63-ownership-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['unrelatedMeshesExactlyIdentical'] and not outside and not added and not railOutside and not(rb-ra)
