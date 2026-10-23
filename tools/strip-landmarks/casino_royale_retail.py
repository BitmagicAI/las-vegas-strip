"""Two-level restaurant frontage beside Casino Royale.
Mapped plan + Fotospot west frontage. Heights/arch placement estimated.
"""
from common import *
from forum_shops import facade_frame
KEY='casinoRoyaleRetail';ID='way/345534561'
def exterior(B):
 B.property=KEY+'-exterior';B.source='casino-royale-retail';B.detail=0;W=Frame(B,0,0,y=0);p=footprint(ID)
 B.planar('rr-paving-concrete',box(78,-465,94,-446.6).difference(p),.24,True)
 # Full lower floor and setback upper restaurant leave an outdoor arrival deck.
 upper=p.intersection(box(100,-470,160,-440));B.shell(p,.24,4.45,'rr-tan-stucco',roof=False);B.planar('rr-paving-concrete',p,4.48,True)
 B.shell(upper,4.48,8.9,'rr-cream-paint',roof=False);B.planar('rr-roof-paint',upper,8.91,True)
 B.planar('rr-paving-concrete',p,.24,True)
 for poly,lo,hi in [(p,.24,4.45),(upper,4.48,8.9)]:
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   F,L,nx,nz=facade_frame(B,a,b,poly,.03)
   if L<.2:continue
   for y in [lo+.12,hi-.3]:F.box('rr-cream-paint',(L/2,y,-.12),(L,.2,.18))
   if nx<-.7:
    F.box('rr-glass',(L/2,(lo+hi)/2,-.12),(L-.4,hi-lo-.55,.06))
    for u in np.arange(.3,L,1.2):F.box('rr-frame-paint',(u,(lo+hi)/2,-.18),(.055,hi-lo-.45,.08))
    F.box('rr-burgundy-paint',(L/2,hi-.2,-.35),(L,.55,.5))
   else:
    # Service-side stucco panels and recessed, shuttered openings.
    for u in np.arange(1.2,L-.8,5):
     F.box('rr-shadow-paint',(u,(lo+hi)/2,-.08),(1.35,1.65,.035))
     for yy in np.arange((lo+hi)/2-.7,(lo+hi)/2+.7,.12):F.box('rr-louver-paint',(u,yy,-.11),(1.3,.045,.07))
    for u in np.arange(.2,L,6):F.box('rr-cream-paint',(u,(lo+hi)/2,-.12),(.16,hi-lo,.17))
 # West upper deck with metal rails and a small curved cylindrical end pier.
 for z in [-459.7,-447.7]:
  W.box('rr-cream-paint',(96.7,4.35,z),(6.5,.3,.35),True)
  for x in np.arange(93.6,100,1.1):W.box('rr-frame-paint',(x,5.03,z),(.06,1.1,.06))
  B.tube('rr-frame-paint',(93.6,5.58,z),(100,5.58,z),.05,8)
  W.box('rr-collision',(96.8,5.02,z),(6.4,1.08,.08),True)
 # Stair and neighboring escalator-shaped access, same walkable slope.
 S=Frame(B,81.4,-450.8,math.pi/2,y=.24)
 S.stairs(0,0,1.6,4.24,12.2)
 S.stairs(2.25,0,1.7,4.24,12.2)
 for u in [-.88,.88,1.35,3.15]:
  S.tube('rr-escalator-paint',(u,.7,0),(u,4.94,12.2),.12,12)
 # Entry fascia and round restaurant signs are part of the permanent frontage.
 F=Frame(B,99.85,-453.6,math.pi/2,y=0)
 F.box('rr-red-paint',(0,8.1,-.1),(12.2,1.3,.28));F.text("McDonald's",(0,7.77,-.27),.85,'rr-white-letter')
 L=Frame(B,93.1,-453.5,math.pi/2,y=0)
 for u,word in [(-3.2,'CHIPOTLE'),(3.2,'CHIPOTLE')]:
  pts=[L.p(u+1.1*math.cos(t),2.95+1.1*math.sin(t),-.1)for t in np.linspace(0,math.tau,48,endpoint=False)];B.face('rr-burgundy-paint',pts)
  B.path('rr-cream-paint',pts+[pts[0]],.065,8);L.text(word,(u,3.35,-.2),.25,'rr-white-letter');L.text('MEXICAN GRILL',(u,2.25,-.2),.15,'rr-white-letter')
  L.path('rr-white-letter',[(u-.25,3.05,-.22),(u+.2,3.15,-.22),(u+.37,2.75,-.22),(u,2.55,-.22),(u-.25,3.05,-.22)],.035,8)
 # One continuous arched ribbon, bending from sidewalk to upper restaurant.
 A=Frame(B,94,-454.65,-math.atan2(11.7,18),y=.24)
 def pt(t):
  u=1-t;return np.array([u**3*-10.735+3*u*u*t*-10+3*u*t*t*8+t**3*10.735,3*u*u*t*27+3*u*t*t*24+t**3*8.7])
 ts=np.linspace(0,1,73);curve=[pt(t)for t in ts]
 for i,(a,b) in enumerate(zip(curve,curve[1:])):
  d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d);aa=a+n*.43;ab=b+n*.43;ba=a-n*.43;bb=b-n*.43
  for z in [-1.25,1.25]:B.face('rr-gold-paint',[A.p(*q,z)for q in [aa,ab,bb,ba]],True)
  for c,d in [(aa,ab),(ba,bb)]:B.face('rr-gold-paint',[A.p(c[0],c[1],-1.25),A.p(d[0],d[1],-1.25),A.p(d[0],d[1],1.25),A.p(c[0],c[1],1.25)],True)
  if i%2==0:
   c=(aa+ab)/2;A.tube('rr-gold-trim-paint',(c[0],c[1],-1.27),(c[0],c[1],1.27),.025,6)
 # Projecting red street sign on arch's near foot, horizontal text baseline.
 G=Frame(B,81.8,-457,math.pi/2,y=0);G.box('rr-red-paint',(0,10.8,0),(8.6,1.8,.65));G.text("McDonald's",(0,10.35,-.36),.65,'rr-white-letter')
 # Roof plant equipment from aerial arrangement; all restrained, batched props.
 for x in [112,119,126,133,140]:
  for z in [-457,-451]:
   if upper.buffer(-1.3).contains(Point(x,z)):
    W.box('rr-service-paint',(x,9.65,z),(2.1,1.4,2.2));W.box('rr-shadow-paint',(x,10.36,z),(1.65,.04,1.7))
    for dz in np.arange(-.8,.9,.2):W.box('rr-frame-paint',(x,10.4,z+dz),(1.7,.04,.035))
 for k in list(B.groups):
  if B.groups[k]['material']=='rr-collision':del B.groups[k]
 return dict(key=KEY,name='Casino Royale restaurant frontage',center=[119,0,-453],bounds=[80,-467,153,-446],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
