"""Converted small offices at Oakey/Santa Paula; Aug2024 north and Dec2022 side references."""
from common import *
from forum_shops import facade_frame
KEY='oakeyOffices'
def hip(B,p,eave,rise):
 x0,z0,x1,z1=p.bounds;x0-=.38;x1+=.38;z0-=.38;z1+=.38;cx=(x0+x1)/2;cz=(z0+z1)/2
 if x1-x0>z1-z0:
  h=(z1-z0)/2;a=(x0+h,eave+rise,cz);b=(x1-h,eave+rise,cz)
  faces=[[(x0,eave,z0),(x1,eave,z0),b,a],[(x1,eave,z0),(x1,eave,z1),b],[(x1,eave,z1),(x0,eave,z1),a,b],[(x0,eave,z1),(x0,eave,z0),a]]
 else:
  h=(x1-x0)/2;a=(cx,eave+rise,z0+h);b=(cx,eave+rise,z1-h)
  faces=[[(x0,eave,z0),(x1,eave,z0),a],[(x1,eave,z0),(x1,eave,z1),b,a],[(x1,eave,z1),(x0,eave,z1),b],[(x0,eave,z1),(x0,eave,z0),a,b]]
 for face in faces:B.upface('oo-roof-paint',face)
 W=Frame(B,0,0,y=0)
 for a,b in zip([(x0,eave,z0),(x1,eave,z0),(x1,eave,z1),(x0,eave,z1)],[(x1,eave,z0),(x1,eave,z1),(x0,eave,z1),(x0,eave,z0)]):W.tube('oo-fascia-paint',a,b,.085,4)
def window(G,u,width=1.7):
 G.box('oo-window-frame-paint',(u,1.65,-.08),(width+.14,1.14,.16))
 G.box('oo-glass',(u,1.65,-.17),(width,1,.025))
 for x in np.arange(u-width/2+.13,u+width/2,.27):G.tube('oo-bars-paint',(float(x),1.13,-.23),(float(x),2.17,-.23),.013,5)
 for yy in [1.2,1.65,2.1]:G.tube('oo-bars-paint',(u-width/2,yy,-.23),(u+width/2,yy,-.23),.016,5)
def door(G,u):
 G.box('oo-door-frame-paint',(u,1.27,-.08),(1.1,2.24,.15));G.box('oo-door-paint',(u,1.23,-.17),(.93,2.08,.05));G.box('oo-glass',(u,1.55,-.205),(.63,1.06,.025));G.box('oo-handle',(u+.33,1.08,-.24),(.035,.16,.03))
 G.box('oo-step',(u,.21,-.55),(1.6,.2,1.1),True)
def fence(B,a,b):
 dx=b[0]-a[0];dz=b[1]-a[1];L=math.hypot(dx,dz);G=Frame(B,a[0],a[1],yaw=-math.atan2(dz,dx),y=0)
 G.box('oo-fence-paint',(L/2,1.13,0),(L,2.0,.08),True)
 for u in np.arange(.1,L,.16):G.box('oo-fence-seam-paint',(float(u),1.13,-.052),(.018,2.0,.035))
 for u in np.arange(0,L,2.4):G.box('oo-fence-post-paint',(float(u),1.2,0),(.09,2.15,.11))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/offices';B.detail=0;W=Frame(B,0,0,y=0)
 west=footprint('way/1236725799');east=footprint('way/1236725798');carport=footprint('way/1236725800');site=box(1935,-3919,1984,-3881)
 B.planar('oo-asphalt',site,.105,True)
 for p in [west,east]:
  B.shell(p,.15,2.8,'oo-white-stucco',roof=False);hip(B,p,2.84,1.45)
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,.03)
   G.box('oo-base-paint',(L/2,.35,-.04),(L,.4,.08))
   if L<4:continue
   if nz<-.7:
    if L>15:
     for u in [L*.16,L*.40,L*.67]:window(G,u,2.05)
     door(G,L*.9)
     G.box('oo-sign-paint',(L*.65,1.65,-.3),(4.6,1.2,.045));G.text('SIN CITY',(L*.65,1.84,-.34),.26,'oo-dark-letter');G.text('HEATING & COOLING',(L*.65,1.43,-.34),.17,'oo-dark-letter')
    else:window(G,L*.28,1.9);door(G,L*.78)
   elif nx>.7 and L>7:
    for u in [L*.22,L*.76]:window(G,u,1.5)
    if L>10:door(G,L*.5);G.text('528',(L*.5-1,2.25,-.17),.24,'oo-dark-letter')
   elif nz>.7:
    door(G,L*.26);window(G,L*.70,1.2)
   elif nx<-.7:window(G,L*.5,1.5)
  x,z=p.centroid.x,p.centroid.y
  for dx,dz in [(-1,0),(2,1)]:
   W.box('oo-service-paint',(x+dx,4.38,z+dz),(1.2,.6,1.0));W.box('oo-vent',(x+dx,4.69,z+dz),(1,.025,.8))
 # Open carport: a roof on posts, not the solid third footprint in the old map.
 x0,z0,x1,z1=carport.bounds
 B.planar('oo-carport-roof-paint',carport,2.75)
 for x in [x0+.15,x1-.15]:
  for z in [z0+.2,(z0+z1)/2,z1-.2]:W.box('oo-post-paint',(x,1.45,z),(.09,2.65,.09),True)
 for a,b in zip(list(carport.exterior.coords),list(carport.exterior.coords)[1:]):W.tube('oo-post-paint',(a[0],2.72,a[1]),(b[0],2.72,b[1]),.065,4)
 # Side/rear fenced yards, keeping both street-facing parking approaches open.
 for a,b in [((1935,-3902),(1935,-3881)),((1935,-3881),(1962,-3881)),((1958,-3901),(1962,-3901)),((1974,-3882),(1983,-3882)),((1983,-3882),(1983,-3894))]:fence(B,a,b)
 for x in [1939,1943,1947,1951,1955,1965,1970]:
  W.box('oo-line-paint',(x,.115,-3907),(.085,.008,5))
 for x in [1941,1945,1949,1953,1967]:W.box('oo-wheelstop',(x,.2,-3903.3),(1.6,.18,.16),True)
 # Plumbing banners seen on the north parking apron, distinct from permanent wall graphics.
 for x in [1957,1975]:
  W.tube('oo-post-paint',(x,.12,-3913),(x,3.65,-3913),.027,7)
  F=Frame(B,x+.3,-3913,y=0)
  outline=[(-.3,.9,0),(.15,1.06,0),(.32,2.8,0),(.25,3.45,0),(.08,3.65,0),(-.3,3.7,0)]
  B.face('oo-banner-paint',[F.p(*v) for v in reversed(outline)])
  for i,c in enumerate('PLUMBING'):F.text(c,(0,3.22-i*.25,-.018),.19,'oo-white-letter')
 samples=[]
 for x in np.arange(1936,1983,1.2):
  for z in np.arange(-3918,-3906,1.2):
   if abs(z+3913)<.6 and min(abs(x-1957),abs(x-1975))<1:continue
   samples.append([float(x),.105,float(z)])
 Path('build/city-exteriors/oakey-offices-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Oakey small offices and carport',center=[1958,0,-3897],bounds=[1934,-3920,1985,-3880],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
