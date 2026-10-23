"""Eataly's diagonal hall and open gable projection, Earth 2022-11-09.
Mapped plan is exact to imported OSM; eave/ridge elevations are photo estimates.
"""
from common import *
from forum_shops import facade_frame
from shapely.affinity import affine_transform

def exterior(B):
 B.source='eataly-south-frontage';B.detail=0
 p=footprint('way/115664840');canopy=footprint('way/1437033263');whole=p.union(canopy)
 # The removed closed box previously owned this ground; give the open porch a floor.
 B.planar('park-stone',canopy,.24,True)
 k=math.sqrt(.5)
 uv=affine_transform(whole,[k,-k,k,k,0,0]);u0,v0,u1,v1=uv.bounds;mid=(u0+u1)/2
 def P(u,v,y):return ((u+v)*k,y,(-u+v)*k)
 def roof_y(u):return 16.1-abs(u-mid)*.23
 for poly in parts(p):
  pts=list(poly.exterior.coords)
  for a,b in zip(pts,pts[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.20)
   if L<2 or nx<0:continue
   F.box('park-window',(L/2,5.9,-.03),(L,11.8,.05))
   for x in np.arange(.25,L,1.55):F.box('steel',(x,5.9,-.14),(.12,11.8,.20))
   for y in [.30,4.1,8,11.8]:F.box('steel',(L/2,y,-.15),(L,.22,.24))
 # Split at ridge to retain a genuine pitched roof over the entire mapped hall.
 for half in [box(u0-1,v0-1,mid,v1+1),box(mid,v0-1,u1+1,v1+1)]:
  for poly in parts(uv.intersection(half)):
   for tri in triangles(poly):
    coords=list(tri.exterior.coords)[:-1]
    B.upface('park-canopy-paint',[P(u,v,roof_y(u)) for u,v in coords],True)
    B.face('steel',list(reversed([P(u,v,roof_y(u)-.18) for u,v in coords])))
   pts=list(poly.exterior.coords)
   for a,b in zip(pts,pts[1:]):B.face('steel',[P(*a,roof_y(a[0])),P(*b,roof_y(b[0])),P(*b,roof_y(b[0])-.18),P(*a,roof_y(a[0])-.18)])
 # Open projection: slender posts on the two front corners, no boxed sidewalls.
 front=affine_transform(canopy,[k,-k,k,k,0,0]);ca,cb,cc,cd=front.bounds
 for u in [ca+.24,cc-.24]:
  x,y,z=P(u,cd-.30,0);B.box('steel',(x,(roof_y(u)-.2)/2,z),(.32,roof_y(u)-.2,.32),solid=True)
 for v in np.arange(v0+1,v1,7):
  line=uv.intersection(LineString([(u0-1,v),(u1+1,v)]))
  for seg in parts(line,'LineString'):
   aa,bb=seg.bounds[0],seg.bounds[2]
   for a,b in [(aa,min(mid,bb)),(max(mid,aa),bb)]:
    if b>a:B.tube('steel',P(a,v,roof_y(a)-.25),P(b,v,roof_y(b)-.25),.10,6)
 B.detail=1
 for u in np.arange(u0+.15,u1,.52):
  line=uv.intersection(LineString([(u,v0-1),(u,v1+1)]))
  for seg in parts(line,'LineString'):
   a,b=list(seg.coords)[0],list(seg.coords)[-1];B.tube('park-roof-rib-paint',P(*a,roof_y(u)+.025),P(*b,roof_y(u)+.025),.025,4)
 B.detail=0
 # Sign faces out toward the Strip/Park junction, matching the diagonal gable.
 x,y,z=P((ca+cc)/2,cd,0);F=Frame(B,x,z,-3*math.pi/4,y=0)
 F.box('steel',(0,11.25,-.06),(cc-ca-.2,2.1,.20))
 F.text('PARK MGM',(0,11.45,-.20),1.05,'ph-letter')
 F.text('E A T A L Y',(0,9.65,-.20),.65,'ph-letter')

 # Keep the neighboring theatre sign when replacing the older shared source.
 F=Frame(B,-184,1388,math.pi,y=.24);F.text('Dolby Live',(0,12.4,-.8),1.4,'steel')
