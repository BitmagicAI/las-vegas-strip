"""1822 Denny's: south butterfly fascia, east entry screen; exterior only."""
from common import *
from forum_shops import facade_frame
KEY='dennys1822'
def window(G,u,y,w,h,depth=-.12):
 G.box('dn-glass',(u,y,depth),(w,h,.1))
 for x in [u-w/2,u+w/2]:G.box('dn-black-paint',(x,y,depth-.07),(.055,h+.08,.08))
 for yy in [y-h/2,y+h/2]:G.box('dn-black-paint',(u,yy,depth-.07),(w+.08,.055,.08))
 G.box('dn-black-paint',(u,y+.4,depth-.08),(w,.045,.08))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/diner';B.detail=0
 p=footprint('way/1236725970');B.shell(p,.18,4.1,'dn-gray-paint',roof=False);B.planar('dn-roof-paint',p,4.05,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.035)
  G.box('dn-black-paint',(L/2,.45,-.07),(L,.55,.14));G.box('dn-red-paint',(L/2,.78,-.07),(L,.16,.16))
  if nz>.7:
   front=G;flen=L
   # Southern facade local u increases westwards. Right-hand entry is east at low u.
   center=L*.53;half=7.2
   # Swept roof edge: low central valley and rising outer wings; closed fascia and roof returns.
   N=40
   def top(u):return 4.45+1.15*(abs((u-center)/half)**1.4)
   for i in range(N):
    u0=center-half+2*half*i/N;u1=center-half+2*half*(i+1)/N;y0=top(u0);y1=top(u1)
    B.face('dn-cream-paint',[G.p(u0,.8,-.1),G.p(u1,.8,-.1),G.p(u1,y1-.22,-.1),G.p(u0,y0-.22,-.1)])
    B.face('dn-red-paint',[G.p(u0,y0-.22,-.35),G.p(u1,y1-.22,-.35),G.p(u1,y1+.1,-.35),G.p(u0,y0+.1,-.35)])
    B.face('dn-roof-paint',[G.p(u0,y0+.1,-.35),G.p(u1,y1+.1,-.35),G.p(u1,4.2,2.1),G.p(u0,4.2,2.1)])
   # Broad gray recessed portal surrounds central dining windows.
   G.box('dn-gray-paint',(center,2.22,-.21),(9.5,3.3,.12))
   for u in np.linspace(center-3.6,center+3.6,5):window(G,float(u),1.79,1.65,2.0,-.3)
   G.text("AMERICA'S DINER",(center,3.47,-.3),.39,'dn-red-letter')
   # Diagonal joint lines confined to solid side piers.
   for side in [-1,1]:
    lo=center+side*5.65
    for y in [.9,2.1,3.3]:
     G.tube('dn-panel-seam-paint',(lo-.65,y,-.18),(lo+.65,y+1.1,-.18),.012,4)
     G.tube('dn-panel-seam-paint',(lo-.65,y+1.1,-.18),(lo+.65,y,-.18),.012,4)
   # East vestibule: black metal glazing and red flat cap, opaque rear retained until interior pass.
   entry=2.4
   G.box('dn-black-paint',(entry,1.75,-.85),(4.25,3.05,1.8),True)
   for u in [entry-1.45,entry,entry+1.45]:window(G,u,1.7,1.3,2.6,-1.81)
   G.box('dn-red-paint',(entry,3.35,-.9),(4.6,.22,2.05));G.box('dn-metal-paint',(entry,1.55,-1.92),(.045,.6,.07))
   for u in [entry-2.5,entry+2.5]:G.tube('dn-yellow-paint',(u,.18,-2),(u,1.22,-2),.06,8)
   # Pentagonal red/gold roof sign; no emissive building walls.
   sy=top(center)+.5;outline=[(-1.55,sy+.65),(1.55,sy+.65),(1.55,sy-.35),(0,sy-.65),(-1.55,sy-.35)]
   B.face('dn-sign-red-paint',[G.p(center+x,y,-.44) for x,y in reversed(outline)])
   G.path('dn-sign-gold-paint',[(center+x,y,-.47) for x,y in outline+[outline[0]]],.055,6)
   G.text("Denny's",(center,sy-.17,-.5),.62,'dn-white-letter')
   G.box('dn-paving',(L/2,.23,-2.2),(L+1,.1,4.4),True)
  elif nx>.7:
   # Red screen at southeast entry, light wall to north with lower horizontal window bands.
   for u in [3.8,8.2,12.6]:window(G,u,1.8,3.2,1.55,-.13)
   u=L-3.0
   for x in [u-1.8,u+1.8]:G.box('dn-red-paint',(x,3.4,-.22),(.18,5.5,.25))
   for y in np.arange(1.15,6.16,.19):G.box('dn-red-paint',(u,float(y),-.25),(3.75,.09,.22))
   G.box('dn-red-paint',(u,6.2,-.25),(4,.18,.3))
  elif nx<-.7:
   for u in [3,7,11,15]:window(G,u,1.85,2.8,1.6)
  else:
   G.box('dn-service-paint',(L*.7,1.4,-.08),(1.2,2.4,.12));G.box('dn-vent',(L*.3,2.6,-.08),(1.6,.8,.12))
 W=Frame(B,0,0,y=0)
 for x,z in [(1708,-3756),(1714,-3756),(1720,-3755),(1713,-3750)]:W.box('dn-service-paint',(x,4.45,z),(1.5,.75,1.25));W.box('dn-vent',(x,4.84,z),(1.25,.04,1))
 # Parking surface and boundary fit remain local to this block; no road changes.
 site=Polygon([(1698,-3764),(1733,-3764),(1736,-3740),(1727,-3719),(1699,-3723)]).difference(p)
 B.planar('dn-asphalt',site,.18,True)
 for x in np.arange(1702,1728,2.7):W.box('dn-line-paint',(float(x),.195,-3735),(.07,.025,4.5))
 # Tall site sign placed in the southern parking pocket.
 S=Frame(B,1720,-3724,yaw=-math.pi/2,y=0)
 S.box('dn-gray-paint',(0,4,0),(.4,7.6,.4),True);S.box('dn-sign-red-paint',(0,7.5,0),(2.5,1.5,.24));S.text("Denny's",(0,7.23,-.15),.58,'dn-white-letter')
 samples=[]
 for x in np.arange(1700,1734,1.2):
  for z in np.arange(-3762,-3722,1.2):
   pt=Point(x,z)
   if site.buffer(-.7).covers(pt) and not p.buffer(4.7).covers(pt) and pt.distance(Point(1720,-3724))>1:samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/dennys-1822-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Denny’s1822 exterior',center=[1716,0,-3746],bounds=[1697,-3765,1737,-3718],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
