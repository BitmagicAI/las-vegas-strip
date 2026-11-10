"""Original public arcade details fitted to mapped piers and April 2025 Street View.
Existing flat route datum retained; elevations and trim sizes are estimates.
"""
from common import *
IDS=['way/399352452','way/399352453','way/399352454','way/399352455','way/399352456','way/399352457','way/399352458','way/399352459','way/399352467','way/399352470']
def exterior(B):
 B.property='excaliburFrontage-exterior';B.source='public-arcade';B.detail=0
 for ident in IDS:
  p=footprint(ident);c=p.centroid
  width=4.2 if p.area>10 else 2.0
  B.box('castle-limestone',(c.x,2.4,c.y),(width,4.2,width),True,-math.pi/4)
  B.box('nyny-white',(c.x,4.65,c.y),(width+.24,.3,width+.24),False,-math.pi/4)
 # Shallow pointed openings along each side of the diagonal public passage.
 for ids in [['way/399352458','way/399352453','way/399352459'],['way/399352456','way/399352454','way/399352455']]:
  cs=[footprint(i).centroid for i in ids]
  for a,b in zip(cs,cs[1:]):
   dx,dz=b.x-a.x,b.y-a.y;L=math.hypot(dx,dz);ux,uz=dx/L,dz/L;nx,nz=-uz,ux
   # Actual pier footprints own the side supports; arch is open below the spring.
   pts=[(1.0,3.25),(L/2,4.15),(L-1,3.25),(L-1,4.8),(1,4.8)]
   for side in [-.28,.28]:
    poly=Polygon(pts)
    for tri in triangles(poly):
     points=[(a.x+ux*x+nx*side,y,a.y+uz*x+nz*side) for x,y in list(tri.exterior.coords)[:-1]]
     B.face('castle-limestone',points if side>0 else points[::-1])
   for pa,pb in zip(pts,pts[1:]+pts[:1]):
    B.face('castle-limestone',[(a.x+ux*x+nx*s,y,a.y+uz*x+nz*s)for x,y,s in [(pa[0],pa[1],-.28),(pb[0],pb[1],-.28),(pb[0],pb[1],.28),(pa[0],pa[1],.28)]])
   # Tan masonry blocks at the spring and sloped trim, visible on both sides.
   F=Frame(B,a.x,a.y,math.atan2(-uz,ux),y=0)
   for side in [-.36,.36]:
    for x in [1.2,L-1.2]:
     for y in [2.9,3.35,3.8]:F.box('sandstone',(x,y,side),(.7,.32,.18))
    F.box('sandstone',(L/2,1.2,side),(L-1.8,.22,.2))
   F.box('castle-limestone',(L/2,.8,0),(L-1.8,1,.5),True)
   for x in np.arange(1.6,L-1.4,1.5):F.box('castle-limestone',(x,1.45,0),(.75,.3,.5))
   B.path('ivory',[(a.x+ux*x+nx*.31,y,a.y+uz*x+nz*.31) for x,y in pts[:3]],.13,6)
 # Flat pale ceiling above the public lane, with original inset fixture panels.
 A=(-99,1775);Z=(-124,1802);L=math.dist(A,Z);yaw=math.atan2(-(Z[1]-A[1]),Z[0]-A[0]);cx=(A[0]+Z[0])/2;cz=(A[1]+Z[1])/2
 B.box('nyny-white',(cx,4.95,cz),(L+3,.3,10.2),True,yaw)
 B.detail=1
 for t in [.15,.4,.65,.9]:
  x=A[0]+(Z[0]-A[0])*t;z=A[1]+(Z[1]-A[1])*t
  B.box('ivory',(x,4.785,z),(1.2,.025,.5),False,yaw)
 B.detail=0
