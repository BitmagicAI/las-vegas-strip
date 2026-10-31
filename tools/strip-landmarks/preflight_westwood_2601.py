"""Read-only source placement audit; never installs or modifies shared city data."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Polygon, Point, unary_union, footprint, SURVEY, Meshes
import westwood_2601

root=Path('build/strip-landmarks')
record=json.loads(Path('tools/resort-blocks/westwood-2601.json').read_text())
owned=set(record['mappedIds'])
collision=json.loads((root/'westwood-2601-exterior-collision.json').read_text())
raw=collision['vertices'];verts=list(zip(raw[::3],raw[1::3],raw[2::3]))
indices=collision['indices'];projected=[]
for i in range(0,len(indices),3):
    points=[verts[j] for j in indices[i:i+3]]
    if max(p[1] for p in points)<.2:continue
    p=Polygon([(v[0],v[2]) for v in points])
    if p.area>1e-8:projected.append(p)
# Horizontal projection is conservative: overlapping footprints may be at different heights.
class ShellAudit(Meshes):
    def __init__(self):super().__init__();self.footprints=[]
    def shell(self,p,lo,hi,mat,*args,**kwargs):
        if hi>.2:self.footprints.append(p)
        return super().shell(p,lo,hi,mat,*args,**kwargs)
audit=ShellAudit();westwood_2601.build(audit)
coverage=unary_union(projected+audit.footprints)
neighbours=[];camera_hits=[]
for building in SURVEY:
    p=footprint(building['id'])
    if building['id'] not in owned and coverage.intersects(p):
        area=coverage.intersection(p).area
        if area>.05:neighbours.append(dict(id=building['id'],areaM2=round(area,4)))
    low=building.get('base') or 0;high=building.get('height') or 0
    for view in record['views']:
        x,y,z=view['eye']
        if low<=y<=high and p.covers(Point(x,z)):
            camera_hits.append(dict(view=view['id'],mappedId=building['id']))
report=dict(scope='Source shell footprints, collision projections and mapped building camera volumes only; roads, actual runtime mesh occlusion and installed alignment still require inspection.',mappedBuildingCount=len(SURVEY),claimedIds=sorted(owned),collisionTriangles=len(indices)//3,neighbourOverlaps=neighbours,cameraCount=len(record['views']),camerasInsideMappedBuildings=camera_hits)
out=Path('.bitmagic/w26-placement-report.json');out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report));assert not neighbours and not camera_hits
