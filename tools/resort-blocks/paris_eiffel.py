"""Paris Las Vegas Eiffel replica, world metres, never legacy-mapped again.
541 ft overall and 460 ft viewing deck corroborated by fabricator / operator.
Intermediate steel sections are photo-fitted estimates, not engineering drawings.
"""
import math
import numpy as np
from shapely.geometry import Polygon, LineString, box
from common import Frame

CENTER=(74.5,400.5)
HEIGHT=164.9

def build(ctx):
 b=ctx['b'];source=ctx['source'];F=Frame(b,*CENTER,math.pi/4,0)
 iron='paris-eiffel';edge='paris-eiffel-edge';dark='paris-eiffel-shadow'
 def face(mat,pts,solid=False):b.face(mat,[F.p(*p) for p in pts],solid)
 def beam(a,c,r=.1,mat=iron):F.tube(mat,a,c,r,4)
 def strip(points,r=.12,mat=iron):F.path(mat,points,r,4)
 def plated(a,c,width=.72,depth=.52):
  # Real flange/web volume, not a hairline cylindrical wire. Kept in one batch.
  a=np.array(a,float);c=np.array(c,float);axis=c-a;axis/=np.linalg.norm(axis)
  u=np.cross(axis,[0,1,0] if abs(axis[2])>.9 else [0,0,1]);u/=np.linalg.norm(u);v=np.cross(axis,u)
  def prism(uc,vc,w,d):
   cross=[u*(uc+x*w/2)+v*(vc+z*d/2) for x,z in [(-1,-1),(1,-1),(1,1),(-1,1)]]
   lo=[a+q for q in cross];hi=[c+q for q in cross]
   face(iron,lo[::-1]);face(iron,hi)
   for k in range(4):j=(k+1)%4;face(iron,[lo[k],lo[j],hi[j],hi[k]])
  t=min(.10,depth*.2)
  prism(0,-depth/2+t/2,width,t);prism(0,depth/2-t/2,width,t);prism(0,0,t,depth-2*t)
 def frame(y,r,th=.2):
  strip([(-r,y,-r),(r,y,-r),(r,y,r),(-r,y,r),(-r,y,-r)],th)
 def quadweb(corners,rows=1,cols=1,primary=.12,secondary=.045):
  a,c,d,e=[np.array(p,dtype=float) for p in corners]
  def at(u,v):return (1-v)*((1-u)*a+u*c)+v*((1-u)*e+u*d)
  for j in range(rows):
   for i in range(cols):
    p,q,r,s=at(i/cols,j/rows),at((i+1)/cols,j/rows),at((i+1)/cols,(j+1)/rows),at(i/cols,(j+1)/rows)
    beam(p,r,primary);beam(q,s,primary)
    if secondary:
     mid=(p+q+r+s)/4
     for pp in [(p+q)/2,(q+r)/2,(r+s)/2,(s+p)/2]:beam(pp,mid,secondary)
  for j in range(1,rows):beam(at(0,j/rows),at(1,j/rows),primary*.7)
 # The four lower legs are curved by closely spaced sections. Their members
 # broaden near the feet; upper mast becomes ONE square truss above level two.
 # Wider piers grow into the first platform. Earlier narrow constant-width
 # legs made a spindly outward kick and an enormous opening between floors.
 tiers=[(0.24,24.0,8.4),(6,22.0,9.0),(12,19.2,9.8),(20,15.2,10.6),(28,11.8,10.8),(35,10.4,9.8),(45,8.0,8.1),(56,5.9,6.4)]
 def envelope(y):
  for (a,r,w),(c,rr,ww) in zip(tiers,tiers[1:]):
   if y<=c:
    t=max(0,min(1,(y-a)/(c-a)));return r+(rr-r)*t+(w+(ww-w)*t)/2
  return 9.1
 source('guest-eiffel-structure')
 for sx in [-1,1]:
  for sz in [-1,1]:
   F.box('paris-ashlar',(sx*24.0,.35,sz*24.0),(9.2,.7,9.2),True)
   for (y,r,w),(yy,rr,ww) in zip(tiers,tiers[1:]):
    low=[(sx*r+u*w/2,y,sz*r+v*w/2) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    high=[(sx*rr+u*ww/2,yy,sz*rr+v*ww/2) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    for k in range(4):plated(low[k],high[k],.82 if y<28 else .68,.58)
    # Primary diagonals and horizontal ties carry visual mass at all LODs.
    for k in range(4):
     j=(k+1)%4
     quadweb([low[k],low[j],high[j],high[k]],max(1,round((yy-y)/4)),1,.21,0)
    # Secondary riveted lattice reads as a mesh skin across the wide piers.
    source('guest-eiffel-lattice',1)
    for k in range(4):
     j=(k+1)%4;quadweb([low[k],low[j],high[j],high[k]],max(2,math.ceil((yy-y)/1.45)),5,.085,0)
    source('guest-eiffel-structure')
    for k in range(4):plated(high[k],high[(k+1)%4],.42,.26)
    # Lower leg collision is a single convex prism surface, not every rivet.
    if y<28:
     for k in range(4):
      j=(k+1)%4
      before={key:(len(g['vertices']),len(g['faces'])) for key,g in b.groups.items()}
      face(iron,[low[k],low[j],high[j],high[k]],True)
      for key,g in b.groups.items():
       nv,nf=before[key];del g['vertices'][nv:];del g['faces'][nf:]
 # Broad parabolic arch bands follow the curved outer face of the piers.
 # The old elliptical profile rose vertically at its ends, detached from the
 # narrow legs, and its sparse spandrel looked like a hanging wire curtain.
 for side in range(4):
  def turn(p):
   x,y,z=p
   for _ in range(side):x,z=-z,x
   return (x,y,z)
  for half,base,rise,top,band in [(20.1,1.0,19.4,27.1,1.25),(6.85,33.0,16.0,56.2,.85)]:
   curve=[];upper=[]
   for t in np.linspace(-1,1,49):
    yy=base+rise*((1-t*t) if base<30 else min(1,(1-abs(t))/.36))
    curve.append(turn((half*t,yy,envelope(yy)+.12)))
    upper.append(turn((half*t,yy+band,envelope(yy+band)+.12)))
   source('guest-eiffel-structure')
   strip(curve,.34,edge);strip(upper,.24)
   for i in range(48):
    beam(curve[i],upper[i+1],.13);beam(upper[i],curve[i+1],.13)
   # Top apron closes the oversized opening below the second platform.
   source('guest-eiffel-lattice',1)
   # Uniform diamonds clipped to the opening; avoid stretched, almost vertical
   # wires from one narrow fan cell all the way to the platform.
   boundary=[]
   for t in np.linspace(-1,1,49):
    yy=base+rise*((1-t*t) if base<30 else min(1,(1-abs(t))/.36))+band
    boundary.append((half*t,yy))
   region=Polygon(boundary+[(half,top),(-half,top)]).intersection(box(-envelope(top),0,envelope(top),top))
   for slope in [-1,1]:
    for offset in np.arange(-100,101,1.55):
     line=LineString([(-40,slope*-40+offset),(40,slope*40+offset)]).intersection(region)
     segments=list(line.geoms) if hasattr(line,'geoms') else [line]
     for seg in segments:
      if seg.geom_type!='LineString' or seg.length<.05:continue
      coords=list(seg.coords);a,c=coords[0],coords[-1]
      points=[]
      for t in np.linspace(0,1,max(2,math.ceil(seg.length/.8)+1)):
       x=a[0]+(c[0]-a[0])*t;y=a[1]+(c[1]-a[1])*t
       points.append(turn((x,y,envelope(y)+.1)))
      strip(points,.10)
   source('guest-eiffel-structure')
   if base>30:
    # Heavy diagonal transom at the head of the arched opening.
    for x in np.arange(-8.6,8.6,2.1):
     beam(turn((x,52.5,envelope(52.5))),turn((x+2,56.2,envelope(56.2))),.18)
     beam(turn((x+2,52.5,envelope(52.5))),turn((x,56.2,envelope(56.2))),.18)
 # Restaurant and second-stage platforms: deep ribbed fascias and broad eaves.
 def platform(y,r,restaurant):
  source('guest-eiffel-structure')
  F.box(iron,(0,y-.55,0),(2*r,1.1,2*r));frame(y-1.2,r+.2,.17);frame(y+.1,r+.2,.17)
  if restaurant:
   F.box(iron,(0,y+4.22,0),(2*r-2.2,.16,2*r-2.2))
   for side in range(4):
    def pp(x,yy,z):
     for _ in range(side):x,z=-z,x
     return (x,yy,z)
    face('paris-eiffel-glass',[pp(-r,y+.25,r-.55),pp(r,y+.25,r-.55),pp(r,y+2.45,r-.55),pp(-r,y+2.45,r-.55)])
    for x in np.arange(-r+.5,r,1.55):beam(pp(x,y+.2,r-.51),pp(x,y+2.5,r-.51),.055)
    face(iron,[pp(-r-1,y+2.45,r+1),pp(r+1,y+2.45,r+1),pp(r-1.1,y+4.3,r-1.1),pp(-r+1.1,y+4.3,r-1.1)])
    for x in np.arange(-r,r,1.0):beam(pp(x,y+2.48,r+.97),pp(x*.9,y+4.32,r-1.08),.018,edge)
    for x in np.arange(-r+1,r,2.3):
     beam(pp(x,y-1.15,r+.12),pp(x,y+.08,r+.12),.14)
     beam(pp(x,y-1.15,r+.1),pp(x,y-2.9,r-1.8),.12)
  else:
   # Thin open gallery, closely spaced uprights rather than black window boxes.
   frame(y+1.65,r,.13);frame(y+.7,r,.045)
   for side in range(4):
    for x in np.arange(-r,r,.7):
     a=(x,y,r);c=(x,y+1.6,r)
     for _ in range(side):a=(-a[2],a[1],a[0]);c=(-c[2],c[1],c[0])
     beam(a,c,.04)
   F.box(iron,(0,y+1.8,0),(2*r+.9,.24,2*r+.9))
  source('guest-eiffel-lattice',1)
  for side in range(4):
   for x in np.arange(-r+.5,r,1.4):
    def pp(xx,yy,zz):
     for _ in range(side):xx,zz=-zz,xx
     return (xx,yy,zz)
    beam(pp(x,y-1.1,r),pp(x+.65,y-.15,r),.045);beam(pp(x+.65,y-.15,r),pp(x+1.3,y-1.1,r),.045)
 platform(28.5,17.6,True);platform(57.5,10.2,False)
 # Four continuously tapered faces. Strong X diagonals define the far silhouette;
 # close lattice is a baked detail layer, no individual runtime members.
 mast=[(59.4,8.3),(67,6.95),(78,5.65),(91,4.6),(105,3.65),(119,2.95),(132,2.45),(139.4,2.30)]
 for (y,r),(yy,rr) in zip(mast,mast[1:]):
  source('guest-eiffel-structure')
  for side in range(4):
   def turn(x,h,z):
    for _ in range(side):x,z=-z,x
    return(x,h,z)
   a,c,d,e=turn(-r,y,r),turn(r,y,r),turn(rr,yy,rr),turn(-rr,yy,rr)
   plated(a,e,.58,.42);plated(c,d,.58,.42)
   quadweb([a,c,d,e],max(1,round((yy-y)/5)),1,.23,0)
   source('guest-eiffel-lattice',1)
   quadweb([a,c,d,e],math.ceil((yy-y)/1.3),4,.075,0)
   source('guest-eiffel-structure')
  frame(yy,rr,.14)
 # The actual viewing deck is chamfered, caged, and open to the skyline.
 source('guest-eiffel-observation')
 outline=[(-5.9,-4.5),(-4.5,-5.9),(4.5,-5.9),(5.9,-4.5),(5.9,4.5),(4.5,5.9),(-4.5,5.9),(-5.9,4.5)]
 deck=F.poly(outline);b.shell(deck,139.55,140,iron,roof=False,solid=True);b.planar(iron,deck,140,True)
 for a,c in zip(outline,outline[1:]+outline[:1]):
  beam((a[0],140,a[1]),(c[0],140,c[1]),.17)
  beam((a[0],143.35,a[1]),(c[0],143.35,c[1]),.13)
  beam((a[0],141.05,a[1]),(c[0],141.05,c[1]),.05)
  beam((a[0],140,a[1]),(a[0],143.35,a[1]),.09)
  # Real cage collision is one wall per side; rods remain visual only.
  face(iron,[(a[0],140,a[1]),(c[0],140,c[1]),(c[0],143.35,c[1]),(a[0],143.35,a[1])],True)
  # Remove the just-added visible wall, retaining its collision triangles.
  key=(b.property,b.source,iron,b.detail);gg=b.groups[key];del gg['vertices'][-4:];del gg['faces'][-2:]
  for t in np.linspace(0,1,max(2,math.ceil(math.dist(a,c)/.14))):
   x=a[0]+(c[0]-a[0])*t;z=a[1]+(c[1]-a[1])*t;beam((x,140.1,z),(x,143.3,z),.009,edge)
  mid=((a[0]+c[0])/2,(a[1]+c[1])/2);beam((mid[0]*.45,136.3,mid[1]*.45),(mid[0],139.65,mid[1]),.18)
 # Roof and compact latticed crown replacing the old bulbous dome.
 b.planar(iron,deck,143.55,True)
 crown=[(143.55,4.8),(145,4.5),(148,3.5),(151,2.2),(153,1.25)]
 for (y,r),(yy,rr) in zip(crown,crown[1:]):
  for side in range(4):
   def turn(x,h,z):
    for _ in range(side):x,z=-z,x
    return(x,h,z)
   pts=[turn(-r,y,r),turn(r,y,r),turn(rr,yy,rr),turn(-rr,yy,rr)]
   for k in [0,1]:beam(pts[k],pts[3-k],.1)
   quadweb(pts,3,4,.045,0)
  frame(yy,rr,.13)
 F.lathe(iron,0,0,[(153,1.3),(153.4,1.3),(153.6,.65),(156.2,.6),(158.1,.2)],16)
 F.tube(edge,(0,157.7,0),(0,HEIGHT,0),.09,8,.025)
 # Ground and top elevator cabins retain the previously implemented L action.
 for y in [.24,140]:
  F.box(dark,(0,y-.1,0),(3.9,.2,3.3),True)
  F.box(iron,(0,y+3.1,0),(3.9,.18,3.3),True)
  F.box(dark,(1.93,y+1.55,0),(.16,3.1,3.3),True)
  for z in [-1.62,1.62]:F.box(iron,(0,y+1.55,z),(3.9,3.1,.12),True)
  # west side deliberately open; landing position lies inside cabin
  for z in [-1.6,1.6]:F.box(edge,(-1.95,y+1.55,z),(.15,3.1,.16))
  F.text('EIFFEL · LIFT',(-1.94,y+2.9,0),.23,edge)
 for x,z in [(-4,0),(0,4),(4,0),(0,-4)]:
  F.lathe(iron,x,z,[(140,.22),(140.1,.22),(140.2,.07),(141.15,.07)],12)
  F.tube(edge,(x,141.2,z-.15),(x,141.45,z+.35),.13,10)
 return dict(center=list(CENTER),height=HEIGHT,observation=140,platforms=[28.5,57.5],baseHalfExtent=28.6,pierSections=[dict(y=y,centre=r,width=w) for y,r,w in tiers],secondStageArchCrown=49.0,source='541 ft / 460 ft: Schuff Steel and Caesars; intermediate sections photograph-fitted')
