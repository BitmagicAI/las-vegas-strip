"""Original pool court from linked aerial and official photos; metre fit is estimated.
Existing mapped pavilions and garage are excluded, never replaced by this study.
"""
from common import *
from rio_amenities import AmenityMeshes
Y=.32
RECORD=Path('docs/project-records/palace-us-bank-amenities')
# North-up Google zoom20 reference, approximately .1206 m/pixel at latitude36.14.
# The map canvas excludes a72px navigation rail, hence centre676 rather than640.
CX=6378137*math.radians(-115.17552+115.173)*math.cos(math.radians(36.116))
CZ=-6378137*math.radians(36.14152-36.116)
def traced(points):return Polygon([(CX+(x-676)*.1206,CZ+(z-360)*.1206) for x,z in points])
def plan():
 occupied=unary_union([footprint(i) for i in ['way/146612127','way/802738223','way/802738225','way/802738226']])
 deck=traced([(856,100),(1015,220),(730,580),(515,450)]).difference(occupied.buffer(.4))
 pool=traced([(768,264),(822,292),(855,326),(850,367),(825,376),(801,410),(719,427),(690,405),(689,383),(707,337),(742,328),(758,277)])
 spa=traced([(747,435),(782,431),(795,438),(789,452),(758,456),(749,449)])
 assert deck.buffer(-.5).covers(pool.union(spa))
 return occupied,deck,[pool,spa]
def build(B):
 B.property='palaceStationAmenities-exterior';B.source='palace-station-amenities';B.detail=0
 occupied,deck,pools=plan();water=unary_union(pools)
 B.planar('psa-paving',deck.difference(water),Y,True)
 B.planar('psa_pool',water,Y-.12)
 B.planar('psa-tile',water,Y-.9,True);B.shell(water,Y-.9,Y,'psa-tile',roof=False,solid=True)
 B.planar('psa-coping',water.buffer(.25).difference(water),Y+.025,True)
 # The nearby spa and pool share one clear outer walking loop.
 routes=[]
 for n,p in enumerate(parts(water.buffer(1.15,join_style=2))):
  ring=list(p.exterior.coords);assert deck.covers(LineString(ring).buffer(.42))
  routes.append(dict(name='palace-circuit-'+str(n),points=[[x,Y,z] for x,z in ring]))
 corridor=unary_union([LineString([(p[0],p[2]) for p in r['points']]).buffer(.8) for r in routes])
 used=[];counts=dict(loungers=0,parasols=0,daybeds=0)
 def reserve(p):
  if not deck.buffer(-.45).covers(p) or water.buffer(2).intersects(p) or corridor.intersects(p) or any(p.intersects(q) for q in used):return False
  used.append(p.buffer(.2));return True
 # Independent parasol bases do not obstruct the circulation loop.
 for d in np.arange(2,pools[0].buffer(7).exterior.length,10):
  q=pools[0].buffer(7).exterior.interpolate(d)
  if not reserve(q.buffer(.45)):continue
  x,z=q.x,q.y;B.box('psa-dark',(x,Y+1.2,z),(.045,2.4,.045),True)
  for j in range(12):
   a=j*math.tau/12;b=(j+1)*math.tau/12
   tip=(x,Y+2.8,z);edge=(x+1.2*math.cos(a),Y+2.35,z+1.2*math.sin(a))
   B.face('psa-white',[tip,edge,(x+1.2*math.cos(b),Y+2.35,z+1.2*math.sin(b))])
   B.tube('psa-dark',tip,edge,.014,4)
  counts['parasols']+=1
 # Navy daybeds/yellow cushions; exact placement/count remains an inference.
 for px,pz in [(855,225),(900,275),(850,460)]:
  x,z=CX+(px-676)*.1206,CZ+(pz-360)*.1206;F=Frame(B,x,z,math.radians(38),y=Y)
  if not reserve(F.poly([(-1,-1.2),(1,-1.2),(1,1.2),(-1,1.2)])):continue
  F.box('psa-navy',(0,.3,0),(1.8,.6,2.1),True)
  F.box('psa-navy',(0,.7,-.85),(1.8,.6,.3))
  for dx in [-.5,.5]:F.box('psa-yellow',(dx,.75,-.55),(.55,.35,.3))
  counts['daybeds']+=1
 # Mesh lounges and dark ribs/white parasols are visible in official photos.
 for distance in [4.1,7]:
  ring=pools[0].buffer(distance).exterior
  for d in np.arange(0,ring.length,2.6):
   q=ring.interpolate(d);near=pools[0].exterior.interpolate(pools[0].exterior.project(q));yaw=math.atan2(near.x-q.x,near.y-q.y)+math.pi
   F=Frame(B,q.x,q.y,yaw,y=Y)
   if not reserve(F.poly([(-.5,-1.1),(.5,-1.1),(.5,1.1),(-.5,1.1)])):continue
   F.box('psa-white',(0,.3,0),(.72,.12,1.9),True)
   for x in [-.3,.3]:
    for z in [-.65,.65]:F.box('psa-white',(x,.15,z),(.04,.3,.04))
   B.face('psa-white',[F.p(-.36,.38,-.3),F.p(.36,.38,-.3),F.p(.36,.85,-.9),F.p(-.36,.85,-.9)])
   counts['loungers']+=1
 (RECORD/'palace-station-routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 (RECORD/'palace-station-geometry.json').write_text(json.dumps(dict(**counts,deckAreaM2=deck.area,basinAreasM2=[p.area for p in pools],coordinateFit=dict(centre=[CX,CZ],metresPerPixel=.1206,screenCentre=[676,360]),limitations=['Estimated map registration, deck extent, furniture count and ground elevation.','Existing mapped pavilions retained; raised bar/stair and planting still unresolved.','Source only; installation, collision, daylight and performance acceptance pending.']),indent=2)+'\n')
 return counts
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
