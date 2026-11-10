"""Original courtyard study from Marriott photographs and aerial tracing.
Source study only: ground registration/access still need installed review.
"""
from common import *
from rio_amenities import AmenityMeshes
from hughes_site import roads
RECORD=Path('docs/project-records/hughes-center-amenities')
Y=.16

def plan():
 r=json.loads((RECORD/'research.json').read_text())['references'][0]['coordinateFit']
 lon,lat=r['centreLonLat'];cx=6378137*math.radians(lon+115.173)*math.cos(math.radians(36.116));cz=-6378137*math.radians(lat-36.116)
 def xy(v):return cx+(v[0]-676)*.1206,cz+(v[1]-360)*.1206
 # Rounded corners follow the aerial silhouette, not a copied mesh.
 pool=Polygon([xy(v) for v in r['poolApproxPixels']]).buffer(.7).buffer(-.7).simplify(.07)
 spa=Point(xy(r['spaCentrePixels'])).buffer(1.35,resolution=20)
 occupied=footprint('way/205497576').buffer(.3)
 water=pool.union(spa)
 deck=water.buffer(5,join_style=2).difference(occupied).difference(roads())
 assert not water.buffer(1.8).intersects(roads())
 assert not water.buffer(1.8).intersects(occupied)
 return deck,pool,spa

def build(B):
 B.property='residenceHughesAmenities-exterior';B.source='residence-hughes-amenities';B.detail=0
 deck,pool,spa=plan();water=pool.union(spa)
 B.planar('rha-paving',deck.difference(water),Y,True)
 B.planar('rha_pool',water,Y+.01)
 B.planar('rha-coping',water.buffer(.25).difference(water),Y+.035,True)
 B.shell(water,Y-.2,Y-.01,'rha-tile',roof=False,solid=False)
 route=pool.buffer(1.2).exterior
 assert deck.covers(LineString(route).buffer(.4))
 used=[];free=deck.buffer(-.4).difference(water.buffer(2.1));count=0
 for t in np.arange(0,pool.buffer(3.5).exterior.length,2.2):
  q=pool.buffer(3.5).exterior.interpolate(t);n=pool.exterior.interpolate(pool.exterior.project(q));yaw=math.atan2(n.x-q.x,n.y-q.y)+math.pi
  F=Frame(B,q.x,q.y,yaw,y=Y);p=F.poly([(-.43,-1),(.43,-1),(.43,1),(-.43,1)])
  if not free.covers(p) or any(p.intersects(u) for u in used):continue
  used.append(p.buffer(.12));count+=1
  F.box('rha-fabric',(0,.39,.25),(.72,.09,1.35),True)
  for x in [-.36,.36]:
   F.box('rha-metal',(x,.32,0),(.05,.07,1.9))
   for z in [-.65,.65]:F.box('rha-metal',(x,.17,z),(.055,.34,.055))
  B.face('rha-fabric',[F.p(-.36,.44,-.4),F.p(.36,.44,-.4),F.p(.36,.88,-.91),F.p(-.36,.88,-.91)])
  for i in range(6):F.box('rha-cream' if i%2 else 'rha-yellow',(-.3+i*.12,.83,-.87),(.12,.13,.13))
 # Gray pickets follow the deck boundary, with a dry south opening.
 ring=LineString(deck.exterior.coords);gate=ring.interpolate(ring.project(Point(pool.centroid.x,pool.bounds[3]+5)))
 for t in np.arange(0,ring.length,.19):
  q=ring.interpolate(t)
  if q.distance(gate)<1.15:continue
  B.box('rha-metal',(q.x,Y+.62,q.y),(.025,1.24,.025))
 for t in np.arange(0,ring.length,2.1):
  q=ring.interpolate(t)
  if q.distance(gate)<1.15:continue
  B.box('rha-metal',(q.x,Y+.66,q.y),(.07,1.32,.07),True)
 for a,b in zip(list(ring.coords),list(ring.coords)[1:]):
  line=LineString([a,b]);segments=line.difference(gate.buffer(1.15))
  for s in ([segments] if segments.geom_type=='LineString' else segments.geoms):
   if s.length>.02:
    a,b=s.coords[0],s.coords[-1]
    B.tube('rha-metal',(a[0],Y+1.24,a[1]),(b[0],Y+1.24,b[1]),.035,6)
    # Separate simple collision panel behind the open pickets; preserve the gate.
    c=B.solids[B.property];n=len(c['vertices'])//3
    for x,y,z in [(a[0],Y,a[1]),(b[0],Y,b[1]),(b[0],Y+1.24,b[1]),(a[0],Y+1.24,a[1])]:c['vertices'].extend([x,y,z])
    c['indices'].extend([n,n+1,n+2,n,n+2,n+3])
 routes=[{'name':'residence-pool-circuit','points':[[x,Y,z] for x,z in route.coords]}]
 (RECORD/'residence-routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 audit={'loungers':count,'poolAreaM2':pool.area,'spaAreaM2':spa.area,'deckAreaM2':deck.area,'poolBounds':list(pool.bounds),'limitations':['Approximate aerial registration; not surveyed.','Original court, landscaping and lobby connection not yet built.','Fence south gap is provisional, not verified public access.','Visual water above retained ground; no swimming-depth claim.','Source not installed or accepted.']}
 (RECORD/'residence-geometry.json').write_text(json.dumps(audit,indent=2)+'\n');return audit
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
