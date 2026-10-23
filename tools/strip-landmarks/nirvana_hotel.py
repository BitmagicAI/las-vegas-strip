"""Nirvana Hotel exterior, mapped outline and June 2023 owner photos.
Room positions and heights are photo-estimates; existing unrelated sites retained.
"""
from common import *
from forum_shops import facade_frame
KEY='nirvanaHotel'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/motel';B.detail=0
 p=footprint('way/364846548');F=Frame(B,0,0,y=0)
 B.shell(p,.04,3.35,'nv-masonry',roof=False);B.planar('nv-roof',p,3.35,True)
 B.planar('nv-paving',p.buffer(.9).difference(p),.12,True)
 # Complete the office forecourt to the existing roadside pavement.
 forecourt=box(35,2677.5,51,2709).difference(p.buffer(.9))
 for x in range(35,51,4):
  for z in range(2659,2709,4):B.planar('nv-paving',forecourt.intersection(box(x,z,x+4,z+4)),.02,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,p,.06)
  G.box('nv-fascia',(L/2,3.38,-.12),(L,.27,.4))
  G.box('nv-fascia',(L/2,3.12,-.1),(L,.07,.3))
  # Subtle mortar courses, subordinate to the white painted masonry.
  for y in np.arange(.22,3.15,.22):G.box('nv-joint',(L/2,y,-.018),(L,.012,.018))
  # Guest doors belong on the south-facing courtyard side of the east wing.
  if abs(a[1]-2699.15)<.2 and abs(b[1]-2699.15)<.2:
   for u in np.arange(2.1,L-1.8,4.2):
    G.box('nv-glass',(u-.55,1.78,-.08),(1.65,1.35,.12))
    for dx in [-.85,0,.85]:G.box('nv-white',(u-.55+dx,1.78,-.17),(.045,1.46,.08))
    for yy in [1.08,2.48]:G.box('nv-white',(u-.55,yy,-.17),(1.75,.06,.08))
    G.box('nv-door',(u+1.05,1.32,-.08),(.94,2.5,.13))
    for dx in [-.5,.5]:G.box('nv-white',(u+1.05+dx,1.32,-.16),(.055,2.58,.08))
    for yy in [.55,1.25,1.95]:
     G.box('nv-panel',(u+1.05,yy,-.16),(.66,.49,.035))
    G.box('nv-metal',(u+1.38,1.25,-.2),(.04,.18,.07))
    G.box('nv-ac',(u-.55,.7,-.23),(.95,.57,.43))
    for yy in np.arange(.48,.92,.07):G.box('nv-shadow',(u-.55,yy,-.46),(.85,.025,.02))
    G.box('nv-metal',(u+.9,2.9,-.23),(.18,.2,.17))
    G.box('nv-bulb',(u+.9,2.88,-.33),(.12,.12,.06))
    G.box('nv-planter',(u-1.6,.37,-.7),(.48,.5,.48))
    for j in range(5):
     x=u-1.6+.15*math.sin(j*2.4);z=-.7+.15*math.cos(j*2.4)
     G.tube('nv-leaf',(x,.6,z),(x,.94,z),.018,5)
     B.sphere('nv-flower',G.p(x,.95,z),.075,8,6)
  elif L>8 and a[0]<72 and b[0]<72:
   # Front office/retail bays; conservative window rhythm where exact fit is uncertain.
   for u in np.arange(2,L-1.5,3.8):
    G.box('nv-glass',(u,1.65,-.08),(2.5,2.25,.1))
    for dx in [-1.27,0,1.27]:G.box('nv-fascia',(u+dx,1.65,-.16),(.06,2.35,.08))
    G.box('nv-white',(u,.47,-.19),(2.7,.12,.24))
 # Parking lot to north of the long guest wing. Preserve its actual narrow plan.
 lot=box(47,2677.5,119,2690).difference(p.buffer(.9))
 for x in range(47,119,4):
  for z in range(2659,2690,4):B.planar('nv-asphalt',lot.intersection(box(x,z,x+4,z+4)),.02,True)
 # Guest parking is in the southern courtyard, owned by nirvanaAncillary.
 # Roof-mounted sign at front; white board, black lettering and lotus emblem.
 G=Frame(B,50.45,2683,math.pi/2,y=0)
 G.box('nv-white',(0,4.12,0),(7.5,1.3,.18))
 G.text('NIRVANA HOTEL',(.4,4.12,-.13),.54,'nv-fascia')
 for j in range(7):
  a=(j-3)*.25;cx=-2.8+.38*math.sin(a);cy=4.0+.34*math.cos(a)
  G.path('nv-lotus',[(-2.8,3.9,-.16),(cx-.1,cy,-.16),(cx,cy+.22,-.16),(cx+.1,cy,-.16),(-2.8,3.9,-.16)],.035,6)
 for u in [-2.5,2.5]:G.box('nv-metal',(u,3.55,.03),(.08,.9,.08))
 # String bulbs attached to the office eave, no runtime light creation.
 G=Frame(B,50.35,2683,math.pi/2,y=0)
 pts=[(-5+10*t,2.94-.22*math.sin(t*math.pi),-.25) for t in np.linspace(0,1,25)];G.path('nv-fascia',pts,.012,5)
 for t in np.linspace(0,1,13):
  u=-5+10*t;y=2.94-.22*math.sin(t*math.pi);G.tube('nv-fascia',(u,y,-.25),(u,y-.12,-.25),.016,5);B.sphere('nv-bulb',G.p(u,y-.16,-.25),.045,8,6)
 # Roof service equipment as seen in satellite imagery.
 for x,z in [(61,2681),(76,2682),(91,2694),(108,2694)]:
  F.box('nv-ac',(x,3.69,z),(1.3,.68,1.1));F.lathe('nv-metal',x,z,[(3.99,.35),(4.03,.35)],16)
 # Boundary rail defines yard without blocking the driveway from the Strip.
 for x in [119]:
  F.box('nv-masonry',(x,.65,2674),(.22,1.3,26),True)
 B.detail=0
 return dict(key=KEY,name='Nirvana Hotel exterior',center=[82,0,2688],bounds=[46,2658,120,2709],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
