"""Original dry landscaped frontage, traced from aerial and Jan2026 Street View.
Dark rectangles are gravel beds, not asserted fountains: close Street View supersedes
ambiguous aerial appearance and old leasing copy. All fit/elevations are estimates.
"""
from common import *
from rio_amenities import AmenityMeshes
import us_bank as U
Y=.32
RECORD=Path('docs/project-records/palace-us-bank-amenities')
CX=6378137*math.radians(-115.1737+115.173)*math.cos(math.radians(36.116))
CZ=-6378137*math.radians(36.14475-36.116)
def point(x,z):return (CX+(x-676)*.1206,CZ+(z-360)*.1206)
def traced(points):return Polygon([point(x,z) for x,z in points])
def plan():
 occupied=unary_union([footprint(i) for i in U.IDS])
 plot=traced([(350,150),(920,70),(920,480),(875,555),(810,580),(400,580),(355,550)]).difference(occupied.buffer(.45))
 paths=[]
 # Pale diagonal cross-paths and their dark gravel squares follow the visible pattern.
 for a,b in [((850,230),(850,350)),((850,350),(740,470)),((740,470),(600,520)),((600,520),(510,475))]:
  a=np.array(a);b=np.array(b);v=b-a;length=np.linalg.norm(v);u=v/length;n=np.array([-u[1],u[0]])
  for d in np.arange(0,length,30):
   c=a+u*d
   for sign in [-1,1]:
    p0=c+n*sign*35-u*25;p1=c-n*sign*35+u*25
    paths.append(LineString([point(*p0),point(*p1)]).buffer(.45,cap_style=2))
 path=unary_union(paths).intersection(plot)
 beds=[traced(p).difference(occupied.buffer(.7)).difference(path.buffer(.15)) for p in [
  [(878,225),(902,240),(902,350),(880,365),(857,345),(865,300)],
  [(515,540),(555,520),(610,540),(660,520),(720,520),(710,545),(650,565),(570,565),(530,555)],
  [(780,285),(810,270),(835,300),(815,350),(785,405),(755,430),(755,375)],
  [(430,455),(455,433),(480,455),(475,485),(455,500),(433,480)]]]
 beds=[p.intersection(plot.buffer(-.3)) for p in beds]
 return occupied,plot,path,beds

def build(B):
 B.property='usBankAmenities-exterior';B.source='us-bank-amenities';B.detail=0
 occupied,plot,path,beds=plan();planting=unary_union(beds)
 B.planar('uba-gravel',plot,Y,True);B.planar('uba-path',path,Y+.02,True)
 # Larger west entrance court is paved in the aerial, unlike east gravel squares.
 court=traced([(355,180),(485,250),(500,380),(520,435),(470,425),(430,455),(355,410)]).intersection(plot)
 B.planar('uba-paving',court,Y+.025,True)
 for p in beds:
  B.planar('uba-soil',p,Y+.42,True)
  B.shell(p,Y,Y+.48,'uba-stone',roof=False,solid=True)
  B.planar('uba-stone',p.buffer(.12).difference(p),Y+.48,True)
 # Small original clipped hedge volumes at the planter perimeter; tree meshes imported separately.
 trees=[];shrubs=0
 for p in parts(planting):
  core=p.buffer(-.45)
  if core.is_empty:continue
  B.shell(core,Y+.42,Y+1.15,'uba-hedge',roof=False,solid=False)
  # Explicit matching top material.
  B.planar('uba-hedge',core,Y+1.151)
  for d in np.arange(1,p.exterior.length,4.2):
   q=p.exterior.interpolate(d);q=core.representative_point() if not core.covers(q) else q
   if any(math.hypot(q.x-t[0],q.y-t[1])<3 for t in trees):continue
   trees.append([q.x,q.y,3.8+(len(trees)%3)*.7]);shrubs+=1
 # Ground-level dry route along the street-facing side of the pattern, not through raised beds.
 routes=[dict(name='us-bank-street-frontage',points=[[x,Y,z] for x,z in [point(916,100),point(916,450),point(875,535),point(810,570),point(410,570)]])]
 for r in routes:
  line=LineString([(p[0],p[2]) for p in r['points']]);assert plot.buffer(.1).covers(line.buffer(.3));assert not planting.intersects(line.buffer(.4))
 (RECORD/'us-bank-routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 (RECORD/'us-bank-geometry.json').write_text(json.dumps(dict(treePlacements=trees,planterAreaM2=planting.area,dryLandscapeAreaM2=plot.area,coordinateFit=dict(centre=[CX,CZ],metresPerPixel=.1206,screenCentre=[676,360]),limitations=['Approximate registration, retained mapped shells, elevations and species.','Close Jan2026 Street View shows gravel and hedges; no new water asserted.','Sign, palm court, exact entrances and full garage access remain unresolved.','Source only; installed review and clearance pending.']),indent=2)+'\n')
 return dict(trees=len(trees),planters=len(beds))
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
