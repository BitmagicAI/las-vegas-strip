"""1809 Strip IHOP and adjoining former mis-tagged mapped block.
Current restaurant fitted approximately from Google satellite view (2026 access),
city's 2020 photo establishes blue cylinder and corrugated cladding.
"""
from common import *
from forum_shops import facade_frame
KEY='ihopNorth'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/restaurant';B.detail=0
 F=Frame(B,1777.5765,-3746.975,math.atan2(18.424,9.181),y=0)
 p=footprint('way/1265036423')
 B.planar('ih-paving',F.poly([(-17,-6),(13,-6),(13,33),(-17,33)]),-.12,True)
 B.planar('ih-paving',F.poly([(-11,-3.5),(10.3,-3.5),(10.3,0),(-11,0)]),.04,True)
 B.shell(p,.1,5.4,'ih-silver',roof=False,solid=True);B.planar('ih-roof',p,5.4,True)
 # Main fascia and wide recessed dining windows on street and drive elevations.
 for offset,yaw,width in [((0,0),0,20.59),((-10.295,14.7),math.pi/2,29.4),((10.295,14.7),-math.pi/2,29.4)]:
  a=F.p(offset[0],0,offset[1]);G=Frame(B,a[0],a[2],F.yaw+yaw,y=0)
  for y in np.arange(.35,5.4,.16):G.box('ih-rib',(0,y,-.05),(width,.045,.08))
  G.box('ih-blue',(0,5.65,-.05),(width,.5,.2))
  for u in np.arange(-width/2+3,width/2-2,5):
   G.box('ih-red',(u,2.8,-.12),(4.65,3.4,.18))
   G.box('ih-glass',(u,2.8,-.23),(4.4,3.15,.1))
   for dx in [-2.2,0,2.2]:G.box('ih-metal',(u+dx,2.8,-.31),(.07,3.2,.08))
   G.box('ih-red',(u,4.45,-.65),(4.8,.12,1.1))
 # Cylindrical southwest entry: glass below, blue drum above.
 cx=-8.8;cz=.2
 F.lathe('ih-glass',cx,cz,[(.15,3),(5.5,3)],64)
 F.lathe('ih-blue',cx,cz,[(5.5,3.03),(10.2,3.03)],64)
 for y in [5.5,8.5,9.5,10.2]:F.lathe('ih-metal',cx,cz,[(y-.035,3.09),(y+.035,3.09)],64)
 for a in np.linspace(0,math.tau,33)[:-1]:
  x,z=cx+3.07*math.cos(a),cz+3.07*math.sin(a);F.tube('ih-metal',(x,.15,z),(x,5.5,z),.055,8)
 B.planar('ih-roof',Point(F.p(cx,0,cz)[0],F.p(cx,0,cz)[2]).buffer(3.04,resolution=32),10.24)
 F.text('IHOP',(1.7,4.5,-.31),1.15,'ih-letter')
 F.text('1809',(1.5,5.6,-.2),.35,'ih-letter')
 F.box('ih-glass',(1.5,1.7,-.16),(3.1,3.1,.16))
 for x in [0,1.5,3]:F.box('ih-metal',(x,1.7,-.28),(.08,3.1,.12))
 for x in [1.35,1.65]:F.tube('ih-metal',(x,1,-.4),(x,1.9,-.4),.025,8)
 # Detached corrugated pylon at the street edge.
 G=Frame(B,*[F.p(-14.5,0,-3)[i] for i in [0,2]],F.yaw,y=0)
 G.box('ih-silver',(0,4.1,0),(2.4,8.2,.6),True)
 for y in np.arange(.3,8.2,.17):G.box('ih-rib',(0,y,-.34),(2.5,.045,.07))
 for yaw in [F.yaw,F.yaw+math.pi]:
  H=Frame(B,G.x,G.z,yaw,y=0)
  H.box('ih-blue',(0,8.7,-.4),(4,2.8,.2));H.text('IHOP',(0,8.65,-.52),1.05,'ih-letter')
  H.text('1809',(0,5.2,-.4),.55,'ih-blue')
 # Roof/service fixtures stay behind the parapet.
 B.detail=1
 for x,z in [(-3,14),(3,23),(-3,26)]:F.box('ih-metal',(x,5.9,z),(2.7,1,2));F.box('ih-dark',(x,6.42,z),(2.4,.04,1.8))
 B.detail=0
 # Satellite places Culinary Health Fund in the old mapped L footprint,
 # NOT the restaurant. Keep mapped structure/collision and author neutral facade.
 B.source='podium/health-fund';old=footprint('way/364845140');ps=list(old.exterior.coords)
 for a,b in zip(ps,ps[1:]):
  if math.dist(a,b)<.2:continue
  H,L,nx,nz=facade_frame(B,a,b,old,.16)
  H.box('ih-cream',(L/2,3.1,0),(L,6,.12));H.box('ih-red-roof',(L/2,6.2,-.2),(L,.28,.6))
  if nx<-.3 or nz<-.3:
   for u in np.arange(3,L-2,5):
    H.box('ih-glass',(u,2.6,-.1),(2.5,2.5,.12));H.box('ih-metal',(u,2.6,-.2),(.06,2.5,.08))
 B.planar('ih-roof',old,6.4)
 return dict(key=KEY,name='North Strip IHOP and adjacent health-fund exterior',center=[1795,0,-3700],bounds=[1755,-3765,1844,-3605],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
