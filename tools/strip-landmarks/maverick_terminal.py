"""Maverick visitor terminal and mapped east service wing.
Satellite-traced west terminal; height and bay counts are photo estimates."""
from common import *
from forum_shops import facade_frame
KEY='maverickTerminal'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/terminal';B.detail=0
 F=Frame(B,0,0,y=0);hangar=footprint('way/276437576')
 terminal=Polygon([(66,4101),(103,4101),(104,4153),(82,4153),(82,4147),(67,4147)])
 for p,h,mat in [(terminal,6.2,'mv-stucco'),(hangar,5.3,'mv-service')]:
  B.shell(p,.04,h,mat,roof=False);B.planar('mv-roof',p,h,True)
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,_,_=facade_frame(B,a,b,p,.04)
   G.box('mv-metal',(L/2,h+.035,-.055),(L,.09,.2))
   for y in np.arange(.95,h,.95):G.box('mv-joint',(L/2,y,-.015),(L,.024,.02))
   for u in np.arange(2.8,L,2.8):G.box('mv-joint',(u,h/2,-.015),(.018,h,.02))
   if p==hangar:
    if L>50:
     for u in np.arange(8,L-3,14):
      G.box('mv-door',(u,2.15,-.035),(5,4.2,.05))
      for y in np.arange(.3,4.3,.28):G.box('mv-metal',(u,y,-.07),(4.95,.018,.03))
    continue
   # Glazing at north and east; public road facade remains mainly panelized wall.
   if a[0]>100 and b[0]>100 or a[1]<4102 and b[1]<4102:
    for u in np.arange(2,L-1,3.1):
     G.box('mv-glass',(u,2.7,-.08),(2.6,3.9,.12))
     for dx in [-1.32,0,1.32]:G.box('mv-metal',(u+dx,2.7,-.16),(.06,4.03,.08))
     for y in [.72,2.45,4.68]:G.box('mv-metal',(u,y,-.16),(2.7,.06,.08))
 # Road-facing entrance with silver cantilever, double glazed doors, raised sign.
 G=Frame(B,66+19/46,4120,math.pi/2+math.atan(1/46),y=0)
 G.box('mv-glass',(0,1.85,-.1),(5.8,3.5,.14))
 for x in [-2.94,-1.45,0,1.45,2.94]:G.box('mv-metal',(x,1.85,-.21),(.075,3.6,.1))
 for x in [-.16,.16]:G.tube('mv-metal',(x,1.25,-.3),(x,2,-.3),.025,8)
 G.box('mv-stucco',(0,4.35,-.2),(8,1.15,.75))
 G.box('mv-silver',(0,3.72,-1.25),(8.3,.26,2.8),True)
 for x in np.arange(-4,4.1,.55):G.box('mv-joint',(x,3.59,-1.25),(.02,.02,2.8))
 G.text('6075',(-2.7,4.5,-.6),.42,'mv-dark')
 G.text('Maverick',(11,3.8,-.12),1.2,'mv-red')
 G.text('HELICOPTERS',(11,2.75,-.13),.32,'mv-dark')
 # Raised helicopter silhouette, drawn as sign relief, not a vehicle prop.
 outline=[(-2,.1),(-1.7,.65),(-.7,1),(.4,.85),(1.1,.4),(3.4,.55),(3.55,.9),(3.8,.9),(3.7,-.1),(1,-.15),(.3,-.45),(-1.2,-.45)]
 for i in range(1,len(outline)-1):B.face('mv-dark',[G.p(10+outline[j][0],5+outline[j][1],-.14) for j in [0,i,i+1]])
 G.path('mv-metal',[(7.2,6.03,-.18),(13.4,6.03,-.18)],.035,6)
 G.path('mv-metal',[(8.2,4.4,-.18),(8.5,4.25,-.18),(11.3,4.25,-.18)],.04,6)
 # Roof membrane and service equipment; screened behind parapet.
 for x,z in [(78,4110),(91,4110),(78,4133),(95,4140),(121,4110),(121,4174)]:
  h=6.2 if x<110 else 5.3;F.box('mv-metal',(x,h+.42,z),(2.1,.84,1.7))
  for u in np.arange(-.8,.9,.2):F.box('mv-dark',(x+u,h+.86,z),(.06,.035,1.4))
 # Continuous visitor forecourt/north drive; no changes to airport taxiways.
 B.source='podium/grounds'
 site=box(42,4088,111,4188).difference(terminal).difference(hangar)
 walk=box(60,4098,67,4149).union(box(62,4115,68,4125)).difference(terminal)
 landscape=box(44,4100,59,4152)
 for x in range(42,111,4):
  for z in range(4088,4188,4):
   cell=box(x,z,x+4,z+4).intersection(site)
   B.planar('mv-asphalt',cell.difference(walk).difference(landscape),.02,True)
   B.planar('mv-paving',cell.intersection(walk),.12,True)
   B.planar('mv-gravel',cell.intersection(landscape),.05,True)
 # Bridge the existing .28m roadside curb with a gradual driveway apron.
 for xa,xb,ya,yb in [(46,49,.04,.34),(49,53,.34,.34),(53,59,.34,.04)]:
  B.face('mv-asphalt',[(xa,ya,4091),(xb,yb,4091),(xb,yb,4097),(xa,ya,4097)],True)
 for z in np.arange(4158,4187,2.8):F.box('mv-line',(76,.15,z),(5,.025,.07))
 # Small planting beds are rough mulch; no placeholder sphere shrubs.
 for z in [4105,4133,4143]:
  F.box('mv-stone',(58,.28,z),(3,.5,3));F.box('mv-soil',(58,.55,z),(2.75,.06,2.75))
 for z in np.arange(4116,4125,2):F.tube('mv-metal',(61,.12,z),(61,1,z),.085,10)
 B.detail=0
 return dict(key=KEY,name='Maverick Las Vegas terminal exterior',center=[88,0,4137],bounds=[41,4087,132,4189],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
