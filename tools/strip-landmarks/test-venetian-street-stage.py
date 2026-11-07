"""Validate the source delta against independent spatial and preservation bounds."""
import json, math, sys
from pathlib import Path
from collections import Counter
from common import footprint
from patch_venetian_street_stage import delta, rows, key
from shapely.geometry import Point, LineString

old=json.loads(Path(sys.argv[1]).read_text())
new=json.loads(Path(sys.argv[2]).read_text())
assert new['labels']==old['labels']
assert len(new['meshes'])>=len(old['meshes'])
for a,b in zip(old['meshes'],new['meshes']):
    if a['source']!='palazzo-front': assert a==b
    else: assert a['vertices']==b['vertices']
a=Counter(k for k,_,_ in rows(old['meshes']))
b=Counter(k for k,_,_ in rows(new['meshes']))
removed,added=a-b,b-a
want_remove,want_add,_=delta()
assert removed==want_remove and added==want_add
poly=footprint('way/33996627')
edges=[]
coords=list(poly.exterior.coords)
for p,q in zip(coords,coords[1:]):
    length=math.dist(p,q);ux,uz=(q[0]-p[0])/length,(q[1]-p[1])/length;nx,nz=-uz,ux
    if poly.contains(Point((p[0]+q[0])/2+nx*.1,(p[1]+q[1])/2+nz*.1)):nx,nz=-nx,-nz
    if nx<-.3 or nz<-.3:edges.append(LineString([p,q]))
for _,_,pts in [k for k in removed]+[k for k in added]:
    for x,y,z in pts:
        assert 4.5<y<12.8, ('Outside upper facade',x,y,z)
        assert min(e.distance(Point(x,z)) for e in edges)<.9, ('Outside selected street edges',x,y,z)
report={'passed':True,'removed':sum(removed.values()),'added':sum(added.values()),
        'untouchedSourceGroups':sum(m['source']!='palazzo-front' for m in old['meshes']),
        'labelsPreserved':True,'groundGeometryPreserved':True,'otherBuildingsAndServiceFacesPreserved':True,
        'allDifferencesInsideSelectedUpperFacade':True}
Path('docs/project-records/venetian-frontage-refinement/preservation-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
