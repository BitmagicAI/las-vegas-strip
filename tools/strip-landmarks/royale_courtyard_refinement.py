"""Original furniture study from the operator pool photo and Google aerial.
Keeps the installed pool, hotel and all existing collision. Dimensions/counts inferred.
"""
from common import *
from rio_amenities import AmenityMeshes
RECORD=Path('docs/project-records/royale-carnaval-refinement')
Y=.32

def plan():
 occupied=unary_union([footprint('way/181282568'),footprint('way/209373381')])
 court=box(134,-508,177,-488).difference(footprint('way/181282568').buffer(.05))
 pool=Point(149,-497).buffer(4.5,resolution=24).union(Point(153,-493).buffer(3.4,resolution=24)).difference(Point(154,-499).buffer(2.7,resolution=20))
 pool=pool.intersection(court.buffer(-1.2))
 return occupied,court,pool

def build(B):
 B.property='royaleCourtyardRefinement-exterior';B.source='royale-courtyard-refinement';B.detail=0
 occupied,court,pool=plan()
 # Only recolour the existing courtyard surface, leaving water/coping untouched.
 deck=court.difference(pool.buffer(.43)).difference(occupied.buffer(.1))
 B.planar('rcr-terracotta',deck,.287)
 available=deck.buffer(-.4).difference(pool.buffer(1.65)).difference(occupied.buffer(.4))
 used=[];chairs=[];parasols=[]
 ring=pool.buffer(2.8).exterior
 for t in np.arange(0,ring.length,2.1):
  q=ring.interpolate(t);near=pool.exterior.interpolate(pool.exterior.project(q));yaw=math.atan2(near.x-q.x,near.y-q.y)+math.pi
  F=Frame(B,q.x,q.y,yaw,y=Y);p=F.poly([(-.43,-1.03),(.43,-1.03),(.43,1.03),(-.43,1.03)])
  if not available.covers(p) or any(p.intersects(v) for v in used):continue
  used.append(p.buffer(.18));chairs.append([q.x,q.y,yaw])
  F.box('rcr-frame',(0,.34,.2),(.78,.08,1.45),True)
  for x in [-.38,.38]:
   F.box('rcr-frame',(x,.34,0),(.045,.07,1.95))
   for z in [-.68,.68]:F.box('rcr-frame',(x,.17,z),(.05,.34,.05))
  for i in range(8):
   x=-.36+i*.09;mat=['rcr-sand','rcr-rust','rcr-blue','rcr-sand'][i%4]
   F.box(mat,(x+.045,.39,.25),(.09,.025,1.35))
   B.face(mat,[F.p(x,.405,-.425),F.p(x+.09,.405,-.425),F.p(x+.09,.88,-.95),F.p(x,.88,-.95)])
  # A rolled white towel visible on the official furniture photo.
  F.tube('rcr-towel',(-.28,.83,-.81),(.28,.83,-.81),.075,8)
 # Two table/parasol groups with conservative clearance from the pool circuit.
 for x,z in [(139,-504),(163,-493),(169,-502)]:
  patch=Point(x,z).buffer(1.45)
  if not available.covers(patch) or any(patch.intersects(v) for v in used):continue
  used.append(patch);parasols.append([x,z])
  B.box('rcr-frame',(x,Y+.38,z),(.12,.76,.12),True)
  B.box('rcr-sand',(x,Y+.78,z),(1.05,.08,1.05),True)
  B.tube('rcr-frame',(x,Y,z),(x,Y+2.65,z),.035,8)
  for j in range(12):
   a=j*math.tau/12;b=(j+1)*math.tau/12
   A=(x+1.3*math.cos(a),Y+2.18,z+1.3*math.sin(a));C=(x+1.3*math.cos(b),Y+2.18,z+1.3*math.sin(b))
   B.face('rcr-parasol',[(x,Y+2.65,z),A,C]);B.tube('rcr-frame',(x,Y+2.63,z),A,.012,4)
 route=pool.buffer(.95).exterior
 assert court.buffer(.01).covers(LineString(route).buffer(.22))
 assert not any(LineString(route).buffer(.4).intersects(v) for v in used)
 assert chairs, 'Furniture placement unexpectedly empty'
 (RECORD/'royale-routes.json').write_text(json.dumps([{'name':'royale-pool-circuit','points':[[x,Y,z] for x,z in route.coords]}],indent=2)+'\n')
 audit={'loungers':len(chairs),'parasolTables':len(parasols),'chairPlacements':chairs,'parasolPlacements':parasols,'deckAreaM2':deck.area,'limitations':['Furniture count, dimensions and orientation inferred, not surveyed.','Existing pool basin retained; no depth/swimming claim.','Palm planting remains deferred; available broadleaf source trees are not substituted.','No geometry installed yet.']}
 (RECORD/'royale-geometry.json').write_text(json.dumps(audit,indent=2)+'\n');return audit
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
