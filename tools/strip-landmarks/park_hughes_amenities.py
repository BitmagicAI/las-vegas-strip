"""Original Park Towers garden pool and tennis court study; aerial-fitted.
Tower shells are never rebuilt. Shared arrival registration remains separate.
"""
from common import *
from rio_amenities import AmenityMeshes
from hughes_site import roads
RECORD=Path('docs/project-records/hughes-center-amenities');Y=.18

def plan():
 r=next(r['coordinateFit'] for r in json.loads((RECORD/'research.json').read_text())['references'] if r['building']=='park-towers' and 'coordinateFit' in r)
 lon,lat=r['centreLonLat'];cx=6378137*math.radians(lon+115.173)*math.cos(math.radians(36.116));cz=-6378137*math.radians(lat-36.116)
 def xy(p):return cx+(p[0]-676)*.2412,cz+(p[1]-360)*.2412
 pool=Polygon([xy(p) for p in r['poolApproxPixels']]);a,b,c,d=r['tennisBoundsPixels'];court=Polygon([xy(p) for p in [(a,b),(c,b),(c,d),(a,d)]])
 occupied=unary_union([footprint(i) for i in ['way/182464616','way/182464631']]).buffer(.4)
 # Preserve the mapped streets: the provisional aerial fit crossed their edge.
 court=translate(court,xoff=6,yoff=2)
 deck=pool.buffer(4.8,join_style=2).difference(occupied).difference(roads())
 assert not court.intersects(roads());assert not court.intersects(deck)
 assert not court.intersects(occupied);assert deck.buffer(-1.3).covers(pool)
 return deck,pool,court

def build(B):
 B.property='parkHughesAmenities-exterior';B.source='park-hughes-amenities';B.detail=0
 deck,pool,court=plan();B.planar('pha-paving',deck.difference(pool),Y,True);B.planar('pha_pool',pool,Y+.01);B.planar('pha-coping',pool.buffer(.3,join_style=2).difference(pool),Y+.035,True)
 # Standard tennis markings inside the aerial-fitted runoff; dimensions remain inferred.
 x,z=court.centroid.x,court.centroid.y;F=Frame(B,x,z,y=Y)
 B.planar('pha-court-surround',court,Y,True);B.planar('pha-court',box(x-5.485,z-11.885,x+5.485,z+11.885),Y+.009)
 def line(a,b,width=.045):
  B.planar('pha-line',LineString([(x+a[0],z+a[1]),(x+b[0],z+b[1])]).buffer(width/2,cap_style=2),Y+.016)
 for u in [-5.485,-4.115,4.115,5.485]:line((u,-11.885),(u,11.885))
 for v in [-11.885,11.885]:line((-5.485,v),(5.485,v))
 for v in [-6.4,6.4]:line((-4.115,v),(4.115,v))
 line((0,-6.4),(0,6.4))
 for u in [-6.1,6.1]:F.box('pha-metal',(u,.54,0),(.09,1.08,.09),True)
 for h in np.arange(.08,.93,.13):F.box('pha-net',(0,float(h),0),(12.2,.012,.012))
 for u in np.arange(-6.1,6.11,.16):F.box('pha-net',(float(u),.49,0),(.012,.88,.012))
 F.box('pha-line',(0,.96,0),(12.2,.045,.025))
 # High dark perimeter mesh visually suggested with a sparse grid, simple collision panels.
 boundary=LineString(court.exterior.coords);gate=Point(court.bounds[2],z+8)
 for a,b in zip(list(boundary.coords),list(boundary.coords)[1:]):
  pieces=LineString([a,b]).difference(gate.buffer(1.15))
  for segment in ([pieces] if pieces.geom_type=='LineString' else pieces.geoms):
   if segment.length<.01:continue
   aa,bb=segment.coords[0],segment.coords[-1]
   for h in [.1,.8,1.5,2.2,2.9]:B.tube('pha-net',(aa[0],Y+h,aa[1]),(bb[0],Y+h,bb[1]),.014,4)
   for t in np.arange(0,segment.length+.01,.65):
    q=segment.interpolate(float(t));B.box('pha-metal',(q.x,Y+1.5,q.y),(.025,3,.025))
   c=B.solids[B.property];n=len(c['vertices'])//3
   for px,py,pz in [(aa[0],Y,aa[1]),(bb[0],Y,bb[1]),(bb[0],Y+3,bb[1]),(aa[0],Y+3,aa[1])]:c['vertices'].extend([px,py,pz])
   c['indices'].extend([n,n+1,n+2,n,n+2,n+3])
 # Pale garden deck and long chaises; placement inferred from available clear apron.
 free=deck.buffer(-.3).difference(pool.buffer(1.9));used=[];count=0
 edge=pool.buffer(3.3,join_style=2).exterior
 for t in np.arange(0,edge.length,2.1):
  q=edge.interpolate(float(t));n=pool.exterior.interpolate(pool.exterior.project(q));F=Frame(B,q.x,q.y,math.atan2(n.x-q.x,n.y-q.y)+math.pi,y=Y)
  p=F.poly([(-.4,-.9),(.4,-.9),(.4,.9),(-.4,.9)])
  if not free.covers(p) or any(p.intersects(o) for o in used):continue
  used.append(p.buffer(.15));count+=1;F.box('pha-fabric',(0,.42,0),(.7,.12,1.8),True)
  for u in [-.32,.32]:
   for v in [-.65,.65]:F.box('pha-metal',(u,.19,v),(.05,.38,.05))
 route=pool.buffer(1.1,join_style=2).exterior;assert deck.covers(LineString(route).buffer(.4))
 (RECORD/'park-routes.json').write_text(json.dumps([{'name':'park-pool-circuit','points':[[x,Y,z] for x,z in route.coords]}],indent=2)+'\n')
 audit={'poolAreaM2':pool.area,'courtBounds':list(court.bounds),'courtFitOffsetM':[6,2],'roadOverlapM2':court.union(deck).intersection(roads()).area,'poolBounds':list(pool.bounds),'loungers':count,'limitations':['Uninstalled original source study.','Aerial fit and ground elevation inferred; road/site-boundary validation pending.','Arrival rotunda and fountain omitted until mapped tower/ground parallax reconciled.','Cabana, planting, pool enclosure and full connections unfinished.','Sport net is visual only; no game mechanics.']}
 (RECORD/'park-geometry.json').write_text(json.dumps(audit,indent=2)+'\n');return audit
if __name__=='__main__':
 B=AmenityMeshes();print(build(B));B.save_all()
