"""1800 Tacos Mexico: contemporary sign reference, older daytime structural views."""
from common import *
from forum_shops import facade_frame
KEY='tacosMexico'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/restaurant';B.detail=0
 p=footprint('way/364846568');B.shell(p,.18,3.75,'tm-stucco',roof=False);B.planar('tm-roof-paint',p,3.65,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.04)
  G.box('tm-red-paint',(L/2,.34,-.08),(L,.32,.16));G.box('tm-red-paint',(L/2,3.8,-.08),(L,.16,.18))
  if L>5:
   # Folded striped metal hood has a sloping upper surface and closed vertical hem.
   count=max(2,round(L/.85));width=L/count
   for j in range(count):
    lo=j*width;hi=(j+1)*width;mat='tm-red-paint' if j%2 else 'tm-white-paint'
    B.face(mat,[G.p(lo,3.65,-.12),G.p(hi,3.65,-.12),G.p(hi,2.85,-1.25),G.p(lo,2.85,-1.25)])
    G.box(mat,((lo+hi)/2,2.72,-1.25),(width,.26,.06))
   B.face('tm-white-paint',[G.p(0,3.65,-.12),G.p(0,2.59,-1.25),G.p(0,2.85,-1.25)])
   B.face('tm-white-paint',[G.p(L,3.65,-.12),G.p(L,2.85,-1.25),G.p(L,2.59,-1.25)])
   for u in np.arange(.2,L,3.1):G.box('tm-white-paint',(float(u),1.55,-.09),(.08,2.5,.12))
  if nx>.8:
   for u in [L*.2,L*.5,L*.8]:
    G.box('tm-glass',(u,1.52,-.18),(1.45,1.95,.1))
    for du in [-.77,.77]:G.box('tm-red-paint',(u+du,1.52,-.25),(.065,2.08,.07))
    for yy in [.51,2.55]:G.box('tm-red-paint',(u,yy,-.25),(1.6,.065,.07))
    G.box('tm-metal-paint',(u,1.52,-.29),(.035,1.98,.04));G.box('tm-metal-paint',(u,1.9,-.29),(1.45,.035,.04))
   G.text('TACOS MEXICO',(L/2,3.92,-.18),.57,'tm-red-letter');G.text('1800',(.35,2.1,-.2),.23,'tm-red-letter')
  elif nz>.7 and L>8:
   for u in [2,5]:
    G.box('tm-glass',(u,1.55,-.18),(1.9,1.9,.1))
    for du in [-1,1]:G.box('tm-red-paint',(u+du,1.55,-.25),(.06,2,.07))
    for yy in [.57,2.53]:G.box('tm-red-paint',(u,yy,-.25),(2,.06,.07))
   G.text('TACOS MEXICO',(4,3.94,-.18),.54,'tm-red-letter')
  elif nz<-.7 and L>6:
   G.box('tm-glass',(L*.48,1.6,-.13),(1.5,1.2,.12));G.box('tm-metal-paint',(L*.48,.96,-.45),(1.8,.12,.85));G.text('PICK UP',(L*.48,2.45,-.13),.3,'tm-red-letter')
  elif nx<-.7:G.box('tm-service-paint',(L/2,1.38,-.1),(1.1,2.4,.12))
 W=Frame(B,0,0,y=0)
 W.box('tm-stucco',(1733.2,3.93,-3787.9),(8.2,.36,11.45));W.box('tm-red-paint',(1733.2,4.14,-3787.9),(8.35,.1,11.6));W.box('tm-roof-paint',(1733.2,4.2,-3787.9),(8.1,.025,11.35))
 for x in [1724,1730,1736]:W.box('tm-service-paint',(x,4,-3787),(1.2,.7,1.4));W.box('tm-vent',(x,4.37,-3787),(.9,.04,1.1))
 site=box(1715,-3799,1750,-3776).difference(p)
 B.planar('tm-asphalt',site,.18,True);B.planar('tm-paving',p.buffer(1.25,join_style=2).difference(p),.24,True)
 # Red low perimeter curb stops at the east entrance route and drive-through aisle.
 for z in [-3794.8,-3780.4]:W.box('tm-red-paint',(1731,.28,z),(24,.2,.18),True)
 # Separate southwest roadside pylon. No historical prices/telephone numbers invented.
 S=Frame(B,1718,-3777,yaw=-math.pi/2,y=0)
 S.box('tm-red-paint',(0,3,0),(.28,5.7,.28),True);S.box('tm-white-paint',(0,5.8,0),(2.2,1.5,.2))
 S.text('TACOS',(0,6,-.13),.36,'tm-red-letter');S.text('MEXICO',(0,5.55,-.13),.32,'tm-red-letter');S.box('tm-red-paint',(0,4.6,0),(1.7,.6,.2));S.text('DRIVE THRU',(0,4.48,-.13),.2,'tm-white-letter')
 # Outdoor bin and service guard posts; no individual window colliders.
 W.box('tm-metal-paint',(1721, .75,-3794),(.65,1.1,.65),True)
 for x in [1720,1722]:W.tube('tm-red-paint',(x,.18,-3794),(x,1.1,-3794),.06,8)
 samples=[]
 for x in np.arange(1716,1749,1):
  for z in np.arange(-3798,-3777,1):
   q=Point(x,z)
   if site.buffer(-.5).covers(q) and not p.buffer(1.7).covers(q) and abs(z+3794.8)>.5 and abs(z+3780.4)>.5 and q.distance(Point(1721,-3794))>1 and q.distance(Point(1718,-3777))>1:samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/tacos-mexico-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Tacos Mexico1800 exterior',center=[1732,0,-3787],bounds=[1714,-3800,1751,-3775],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
