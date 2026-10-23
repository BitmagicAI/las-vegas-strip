"""Haven Street paired courtyard buildings. StreetView December2022 + satellite.
Measured footprint; heights, concealed doors and court access inferred explicitly.
"""
from common import *
from forum_shops import facade_frame
from courtyard_525 import palm
KEY='havenCourtyards';IDS=['way/1414161011','way/1414161010']
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/haven-courtyards';B.detail=0
 ps=[footprint(i) for i in IDS];W=Frame(B,0,0,y=0);samples=[]
 for index,p in enumerate(ps):
  B.shell(p,.18,6.45,'hc-cream-stucco',roof=False);B.planar('hc-roof-paint',p.buffer(-.12),6.16,True)
  # Four recessed rusty-red window strips on long outer side wings.
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,0)
   G.box('hc-coping-paint',(L/2,6.47,0),(L,.12,.30))
   if L<4:continue
   mx,mz=G.p(L/2,0,0)[0],G.p(L/2,0,0)[2]
   court=(180<mx<204 and ((index==0 and mz>2739) or(index==1 and mz<2793)))
   if abs(nx)>.8 and L>18:
    for u in np.linspace(3.7,L-3.7,4):
     G.box('hc-rust-paint',(float(u),3.14,-.035),(1.55,5.92,.05))
     for y in [1.65,4.75]:window(G,float(u),y)
    for u in [1.25,L-1.25]:G.box('hc-cream-stucco',(u,3.36,-.10),(2.5,6.36,.20))
   elif court:
    for u in np.arange(1.4,L-1,3.9):
     for y in [.18,3.18]:
      G.box('hc-frame-paint',(float(u),y+1.08,-.08),(.98,2.16,.12));G.box('hc-door-paint',(float(u),y+1.08,-.16),(.84,2.02,.04));G.box('hc-handle-paint',(float(u)+.29,y+1,-.20),(.035,.15,.035))
      if u+1.7<L-1:window(G,float(u)+1.7,y+1.5)
   elif L>10:
    for u in np.arange(3,L-2,4.4):
     for y in [1.7,4.7]:window(G,float(u),y)
   G.box('hc-plinth-paint',(L/2,.35,-.055),(L,.34,.10))
   if L>15:
    for u in [1,L-1]:G.tube('hc-downpipe-paint',(u,.25,-.22),(u,6.3,-.22),.035,8)
  # Individual mechanical units, vent stacks and conduits on the three roof masses.
  for x in [175.5,190.8,208.2]:
   zlist=([2733,2741,2748] if index==0 else [2784,2792,2798]) if x!=190.8 else ([2733] if index==0 else [2798])
   for z in zlist:
    if not p.buffer(-1).contains(Point(x,z)):continue
    W.box('hc-curb-paint',(x,6.28,z),(1.7,.24,1.6));W.box('hc-service-paint',(x,6.74,z),(1.45,.7,1.35));W.box('hc-grille-paint',(x,7.10,z),(1.15,.025,1.05))
    B.lathe('hc-grille-paint',(x+.42,z),[(7.12,.24),(7.15,.24)],16)
    W.tube('hc-downpipe-paint',(x,6.21,z),(x+2,6.21,z),.045,7)
    B.lathe('hc-service-paint',(x-1,z+1.7),[(6.16,.10),(6.85,.10),(6.85,.17),(6.95,.17)],12)
  for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.5):
   for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.5):
    if p.buffer(-.25).contains(Point(x,z)):samples.append([float(x),7,float(z)])
 # Upper court gallery with a stair on the west side, clear of the garden.
 for index,(back,front,sgn) in enumerate([(2740.3,2752.8,1),(2791.9,2779.0,-1)]):
  # Gallery follows inner U, leaving a wide open central garden below.
  zmid=(back+front)/2;length=abs(front-back);wx=181.65+index*.8
  for x in [wx,201.65]:
   
   if x>190:W.box('hc-gallery-concrete',(x,3.08,zmid),(1.7,.2,length),True)
   else:W.box('hc-gallery-concrete',(x,3.08,back+sgn*.65),(1.7,.2,1.3),True)
   # Raised continuous guard along garden edge.
   gx=x+(.80 if x<190 else -.80)
   rail(B,[(gx,back),(gx,front-sgn*1.25)],3.18)
  W.box('hc-gallery-concrete',(191.65,3.08,back+sgn*.65),(21.7,.2,1.5),True)
  rail(B,[(wx+.8,back+sgn*1.4),(200.85,back+sgn*1.4)],3.18)
  # Stair rises toward front; landing occupies only the end, not the flight.
  start=front-sgn*6.7;S=Frame(B,wx,start,yaw=0 if sgn>0 else math.pi,y=0)
  S.stairs(0,0,1.7,3,5.5,y=.18)
  # Cut the side gallery above stair flight so it never creates a head obstruction.
  # Built below as replacement surface over shorter reach.
  W.box('hc-gallery-concrete',(191.65,3.08,front-sgn*.6),(21.7,.2,1.2),True)
  rail(B,[(180.8,front),(202.5,front)],3.18)
  rail(B,[(wx+.95,front-sgn*1.2),(200.8,front-sgn*1.2)],3.18)
  # Garden island and winding pedestrian path from court mouth to rear cross passage.
  garden=box(184, min(back,front)+2,199.8,max(back,front)-2)
  path=LineString([(192,front),(193.5,front-sgn*4),(190,back+sgn*3),(191.5,back)]).buffer(.8)
  B.planar('hc-gravel',garden.difference(path),.20,True)
  for x,z,h in [(187,back+sgn*4.8,7.7),(196.5,back+sgn*7,8.7),(185,front-sgn*3,6.8)]:palm(B,W,x,z,h)
 # Collision floor across courtyards and shared aisle only. Keep public roads unchanged.
 B.planar('hc-gravel',box(217,2727,249,2805),.10,True)
 site=box(166,2727,217,2805).difference(unary_union(ps));B.planar('hc-asphalt',site,.15,True)
 for index,(back,front) in enumerate([(2740.3,2752.8),(2791.9,2779.0)]):
  B.planar('hc-paving-concrete',box(180.7,min(back,front),202.5,max(back,front)),.18,True)
 # Shared parking rows and wheel stops leave a central drive aisle.
 for z in [2757.1,2774.5]:
  for x in np.arange(170,211,2.8):
   W.box('hc-line-paint',(float(x),.17,z),(.07,.015,4.7))
   W.box('hc-wheelstop-concrete',(float(x)+1.4,.26,z+(-1.8 if z<2760 else 1.8)),(1.7,.20,.15),True)
 # Exterior trim and blank end walls reflect the visible street-facing blocks.
 for index,z in enumerate([2734,2795]):
  G=Frame(B,213.46,z,yaw=-math.pi/2,y=0);G.text('A' if index==0 else 'B',(0,.65,-.15),.30,'hc-dark-letter')
 for k in list(B.groups):
  if B.groups[k]['material']in ('c525-collision','hc-collision'):del B.groups[k]
 Path('build/city-exteriors/haven-courtyards-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Haven Street courtyard buildings',center=[191,0,2766],bounds=[166,2727,249,2805],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
def window(G,u,y):
 G.box('hc-frame-paint',(u,y,-.09),(1.30,1.16,.12));G.box('hc-glass',(u,y,-.17),(1.16,1.02,.04));G.box('hc-frame-paint',(u,y,-.20),(.035,1.02,.035));G.box('hc-sill-paint',(u,y-.61,-.19),(1.40,.09,.30))
def rail(B,points,y):
 W=Frame(B,0,0,y=0)
 for a,b in zip(points,points[1:]):
  L=math.dist(a,b)
  for t in np.linspace(0,1,math.ceil(L/.16)+1):
   x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t;W.box('hc-rail-paint',(x,y+.54,z),(.025,1.08,.025))
  for h in [.1,1.08]:W.tube('hc-rail-paint',(a[0],y+h,a[1]),(b[0],y+h,b[1]),.028,6)
  B.face('hc-collision',[(a[0],y,a[1]),(b[0],y,b[1]),(b[0],y+1.08,b[1]),(a[0],y+1.08,a[1])],True)
