"""LINQ blue/white tower and hexagonal street-front volumes, Caesars photo reference.
Surveyed plan, retained 63m tower; 29.5m front screen estimated from photographs.
Render-only facade details; existing public entrance and wheel remain authoritative.
"""
import math,random
from common import np,parts,Point,Polygon,Frame,triangles,box,LineString

def tower(B,shape):
 B.source='guest-linq';B.detail=0
 B.shell(shape,17.12,63,'white',solid=False)
 for poly in parts(shape):
  # Simplification joins collinear survey vertices so windows stay regularly spaced.
  clean=list(poly.simplify(.06,preserve_topology=True).exterior.coords)
  for a,b in zip(clean,clean[1:]):
   L=math.dist(a,b)
   if L<1:continue
   ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
   if shape.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
   def p(x,y,d):return(a[0]+ux*x+nx*d,y,a[1]+uz*x+nz*d)
   def quad(mat,x,y,xx,yy,d=.12):B.face(mat,[p(x,y,d),p(xx,y,d),p(xx,yy,d),p(x,yy,d)])
   if L<18:
    if L>11.5 and nx<-.7:
     B.text('THE',p(L/2,59.8,.2),.6,math.atan2(uz,ux)+math.pi,'linq-blue')
     B.text('LINQ',p(L/2,57.8,.2),1.7,math.atan2(uz,ux)+math.pi,'linq-blue')
    continue # white structural end frames are a defining silhouette
   # Each room is a shallow three-sided glazed bay, not a painted window grid.
   # Blue reveals/slab edges wrap the fields; white is reserved for the broad
   # structural end frames and crown visible in the creator's aerial reference.
   margin=3.1 if L>35 else 1.45;count=max(2,round((L-2*margin)/3.1));step=(L-2*margin)/count;dy=2.62
   quad('linq-blue',margin,17.8,L-margin,60.2,.12)
   for j in range(count):
    x=margin+j*step
    for row in range(16):
     y=18+row*dy;w=step-.10;hh=dy-.12
     # Faceted glass has a projecting centre and recessed jambs, with all
     # normals authored by actual depth. Facets remain present in coarse views.
     ribs=[(x+.08,.18),(x+w*.22,.76),(x+w*.78,.76),(x+w-.08,.18)]
     for k,((xa,da),(xb,db)) in enumerate(zip(ribs,ribs[1:])):
      mat='linq-glass' if k==1 else 'linq-glass-side'
      B.face(mat,[p(xa,y+.23,da),p(xb,y+.23,db),p(xb,y+hh-.18,db),p(xa,y+hh-.18,da)])
      B.face('linq-facet-light',[p(xa,y+.10,da+.03),p(xb,y+.10,db+.03),p(xb,y+.23,db+.03),p(xa,y+.23,da+.03)])
      B.face('linq-facet-dark',[p(xa,y+hh-.18,da+.03),p(xb,y+hh-.18,db+.03),p(xb,y+hh,db+.03),p(xa,y+hh,da+.03)])
      # Sloping sill and head return, avoiding a coincident solid box.
      B.face('linq-blue',[p(xa,y+.10,.13),p(xb,y+.10,.13),p(xb,y+.10,db+.03),p(xa,y+.10,da+.03)])
      B.face('linq-blue',[p(xa,y+hh,da+.03),p(xb,y+hh,db+.03),p(xb,y+hh,.13),p(xa,y+hh,.13)])
     for xx in [x+.08,x+w-.08]:quad('linq-facet-light',xx-.055,y+.1,xx+.055,y+hh,.24)
     B.detail=1
     quad('linq-mullion',x+w*.5-.022,y+.23,x+w*.5+.022,y+hh-.18,.80)
     quad('linq-mullion',x+w*.22,y+hh*.59,x+w*.78,y+hh*.59+.045,.80)
     # A small number of drawn blinds, behind the centre pane.
     if (row*13+j*7)%23==0:quad('linq-curtain',x+w*.23,y+.25,x+w*.47,y+hh-.20,.77)
     B.detail=0
   for y,hh,d in [(17.15,.65,.88),(60.2,2.8,.82),(62.95,.32,1.02)]:
    quad('white',0,y,L,y+hh,d)
    B.face('white',[p(0,y+hh,.03),p(L,y+hh,.03),p(L,y+hh,d),p(0,y+hh,d)])
   for x,xx in [(0,margin),(L-margin,L)]:
    quad('white',x,17.15,xx,63,.92)
    for edge in [x,xx]:B.face('white',[p(edge,17.15,.03),p(edge,63,.03),p(edge,63,.92),p(edge,17.15,.92)])
    for y in np.arange(19,62,2.7):quad('linq-joint',x,y,xx,y+.025,.94)
   # Open-looking horizontal base bands are a distinct part of the real hotel.
   quad('linq-facet-dark',0,5.1,L,16.8,.20)
   for y in [5.5,8.2,10.9,13.6,16.3]:quad('white',0,y,L,y+.40,.78)
   for x in [0,L-1.1]:quad('white',x,5.1,x+1.1,17.1,.80)
   # Signs only on the two western broad faces; actual lettering, no generic grid.
   if nx<-.75 and L>25:
    x=L-margin*.48
    B.text('LINQ',p(x,60.6,.73),.95,math.atan2(uz,ux)+math.pi,'linq-blue')
 B.detail=1
 for poly in parts(shape.buffer(-2)):
  B.shell(poly,63.05,64,'white',solid=False,roof=False)
 for x in np.arange(shape.bounds[0]+5,shape.bounds[2]-4,14):
  for z in np.arange(shape.bounds[1]+5,shape.bounds[3]-4,14):
   if shape.contains(Point(x,z).buffer(2)):
    B.box('white',(x,63.6,z),(3.7,1.2,2.6));B.box('charcoal',(x,64.25,z),(3.2,.08,2.2))
 B.detail=0

def street(B,pod,F):
 B.source='linq-street';B.detail=0
 # Add the tall front cladding wings, leaving the retained central arrival at ground.
 # Reference: tall north/south screens and recessed central High Roller display.
 front=pod.intersection(box(0,-294,64,-210))
 high=front.difference(box(0,-261.567,100,-234.261))
 B.shell(front,17,26,'white',solid=False,roof=False)
 B.planar('white',front.difference(high),26)
 B.shell(high,26,29.5,'white',solid=False,roof=False)
 B.planar('white',high,29.5)
 points=list(pod.exterior.coords)
 for a,b in zip(points,points[1:]):
  segment=LineString([a,b]).intersection(box(0,-294,64,-210))
  if segment.is_empty or segment.geom_type!='LineString':continue
  a,b=list(segment.coords)[0],list(segment.coords)[-1]
  L=math.dist(a,b)
  if min(a[0],b[0])>80 or L<2:continue
  ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
  if pod.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
  if nx>.1:continue
  def p(x,y,d):return(a[0]+ux*x+nx*d,y,a[1]+uz*x+nz*d)
  def q(mat,x,y,xx,yy,d):B.face(mat,[p(x,y,d),p(xx,y,d),p(xx,yy,d),p(x,yy,d)])
  midz=(a[1]+b[1])/2;recess=-261.568<midz<-234.260;central=recess and nx<-.8 and L>15
  # Panel surfaces sit away from the original 17m shell (no shared coplanar face).
  top=26 if recess else 29.5
  q('linq-joint',0,7.2,L,top,.31)
  # Structure comes from the union above; individual survey-edge caps caused
  # intersecting panels across concave corners. Keep only the thin surface skin.
  # Large flat hexagons tile the wall, with narrow real joints between them.
  rng=random.Random(round(a[1]*3));r=1.2;step=math.sqrt(3)*r;domain=box(0,7.3,L,top-.12)
  if central:domain=domain.difference(box(2,15,L-2,top-.5))
  for row,y in enumerate(np.arange(7,top+2,1.5*r)):
   for col,x in enumerate(np.arange(-step,L+step,step)):
    cx=x+(row%2)*step/2;hexagon=Polygon([(cx+(r-.028)*math.cos(t),y+(r-.028)*math.sin(t)) for t in np.linspace(math.pi/6,math.pi/6+math.tau,7)[:-1]]).intersection(domain)
    v=rng.random();mat='white' if v<.62 else 'linq-hex-grey' if v<.77 else 'linq-facet-light' if v<.89 else 'linq-hex-dark'
    for poly in parts(hexagon):
     for tri in triangles(poly):B.face(mat,[p(xx,yy,.35) for xx,yy in list(tri.exterior.coords)[:-1]])
  for y in np.arange(7.2,top,.60):q('linq-joint',0,y,L,min(y+.015,top),.36)
  # Broad smooth coping and a recess at the base, avoiding the existing door zone.
  q('white',0,top,L,top+.35,.48)
  if central:
   q('charcoal',2,15,L-2,top-.5,.4)
   c=p(L/2,0,.6);J=Frame(B,c[0],c[2],math.atan2(-nx,-nz),y=0)
   J.text('HIGH ROLLER',(0,22.8,-.05),1.08,'letter');J.text('THE LINQ',(0,17.4,-.05),.75,'letter');J.text('LAS VEGAS',(0,16.2,-.05),.37,'letter')
   J.path('white',[(3.1*math.cos(t),20.8+3.1*math.sin(t),-.08) for t in np.linspace(0,math.tau,65)],.075,6)
   for t in np.linspace(0,math.tau,28,endpoint=False):B.sphere('white',J.p(3.1*math.cos(t),20.8+3.1*math.sin(t),-.13),.14,8,6)
  elif L>12:
   if nx<-.65:
    q('linq-glass',1,.5,L-1,5.1,.38)
    for xx in np.arange(1,L-1,1.4):q('silver',xx,.5,xx+.07,5.1,.49)
    q('white',.7,5.15,L-.7,5.5,.65)
    for xx in np.arange(2,L-2,5):
     for off in [-.14,.14]:q('silver',xx+off,1,xx+off+.035,1.65,.52)
   c=p(L/2,0,.62);J=Frame(B,c[0],c[2],math.atan2(-nx,-nz),y=0);J.text('THE',(0,27.9,0),.48,'linq-hex-dark');J.text('LINQ',(0,26.2,0),1.5,'linq-hex-dark')
 # Casino arrival: shallow canopy and colored vertical light bars frame the doorway.
 F.box('white',(0,5.6,-2),(28,.5,4.4));F.box('linq-blue',(0,5.2,-4.25),(28,.4,.13));F.text('THE LINQ',(0,11.6,-.65),1.45,'linq-hex-dark')
 for side in [-1,1]:
  for j in range(7):
   x=side*(4.5+j*.72);F.box('silver',(x,4.9,-.3),(.27,9.1,.33));F.box(['ledblue','pinkled','yellowled'][j%3],(x,4.9,-.49),(.11,8.9,.035))
  # Ground-level window bays, solid trim and individually separated double doors.
  for x in [side*11.5,side*15]:
   F.box('linq-glass',(x,2.1,-.31),(3.15,3.65,.10))
   for xx in [x-1.57,x,x+1.57]:F.box('silver',(xx,2.1,-.41),(.085,3.65,.16))
   for xx in [x-.17,x+.17]:F.box('silver',(xx,1.25,-.54),(.025,.56,.045))
 # The vortex is a small promenade-end canopy, not a large roof over the casino sign.
 B.source='linq-vortex';J=Frame(B,34,-217,math.pi/2,y=0)
 for i in range(47):
  x=-11.5+i*.5;pts=[]
  for z in np.linspace(-4,7,20):pts.append(J.p(x,11+1.9*math.sin((x+11.5)*math.pi/23)+1.25*math.sin((z+4)*math.pi/11+.07*x),z))
  B.path('vortex'+str(i%3),pts,.07,6)
 for side in [-1,1]:J.tube('white',(side*11.5,0,4),(side*11.5,11,4),.22,12)
 B.detail=0
