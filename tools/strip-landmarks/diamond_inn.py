"""Diamond Inn: mapped U plan, primary auction photo and satellite reference.
Closed-site exterior; no operating hotel or accessible room claim.
"""
from common import *
from forum_shops import facade_frame
KEY='diamondInn'
def palm(B,x,z,h=8,crown_scale=1):
 F=Frame(B,x,z,y=0);F.lathe('bark',0,0,[(0,.24),(h*.55,.18),(h,.13)],16)
 for y in np.arange(.2,h,.3):F.lathe('bark',0,0,[(y,.2),(y+.06,.23),(y+.1,.2)],12)
 for j in range(13):
  a=j*math.tau/13;co,si=math.cos(a),math.sin(a);pts=[]
  for t in np.linspace(0,1,12):pts.append((co*3.4*t*crown_scale,h+(1.2*math.sin(t*math.pi)-1.7*t)*crown_scale,si*3.4*t*crown_scale))
  F.path('di-leaf',pts,.025,6)
  for k in range(1,11):
   t=k/11;yy=h+(1.2*math.sin(t*math.pi)-1.7*t)*crown_scale;r=3.4*t*crown_scale;w=.65*math.sin(t*math.pi)*crown_scale
   for s in [-1,1]:
    B.face('di-leaf',[F.p(co*r,yy,si*r),F.p(co*(r+.16)-s*si*w,yy-.28,si*(r+.16)+s*co*w),F.p(co*(r+.3),yy-.12,si*(r+.3))])
def elephant(B):
 F=Frame(B,49,3177,math.pi/2,y=0)
 def sph(c,r,scale):B.sphere('di-pink',F.p(*c),r,32,20,scale=(scale[2],scale[1],scale[0]))
 sph((0,2.45,.3),1,(1.05,1.05,1.8));sph((0,2.9,-1.3),.85,(.9,1.15,.9))
 for x in [-.65,.65]:
  for z in [-.75,1.35]:F.lathe('di-pink',x,z,[(.1,.34),(.25,.38),(1.5,.28),(2.4,.4)],24)
  sph((x*1.65,2.95,-.85),1,(.26,1.25,.88))
  B.sphere('di-eye',F.p(x*.75,3.08,-1.91),.07,12,8)
  path=[(x*.7,2.52,-1.8),(x*.85,2.2,-2.2),(x,2.35,-2.65)]
  for i in range(2):F.tube('di-ivory',path[i],path[i+1],.1-i*.045,16,r2=.055-i*.05)
  for z in [-.75,1.35]:
   for dx in [-.18,0,.18]:B.sphere('di-toe',F.p(x+dx,.18,z-.3),.12,12,8,scale=(.65,1,.5))
 pts=[(0,2.8,-1.9),(0,2.4,-2.2),(0,2.05,-2.6),(0,1.95,-3),(0,2.15,-3.45),(0,2.7,-3.7),(0,3.2,-3.8)]
 for i in range(len(pts)-1):
  F.tube('di-pink',pts[i],pts[i+1],.32-i*.035,24,r2=.285-i*.035)
  sph(pts[i],.32-i*.035,(1,1,1))
 F.path('di-pink',[(0,2.6,1.9),(.1,1.8,2.3),(.2,1.2,2.35)],.07,12)
 F.box('di-paving',(0,.04,0),(3,.08,6.8),True)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/motel';B.detail=0
 p=footprint('way/457939120');B.shell(p,.04,3.65,'di-white',roof=False);B.planar('di-roof',p,3.65,True)
 F=Frame(B,0,0,y=0)
 B.planar('di-paving',p.buffer(1.1).difference(p),.04,True)
 ps=list(p.exterior.coords)
 for a,b in zip(ps,ps[1:]):
  if math.dist(a,b)<.4:continue
  G,L,nx,nz=facade_frame(B,a,b,p,.06)
  G.box('di-blue',(L/2,3.5,-.04),(L,.5,.18));G.box('di-white',(L/2,3.78,-.06),(L,.12,.25))
  G.box('di-blue',(L/2,.3,-.03),(L,.45,.12))
  if L<7:continue
  for u in np.arange(2.4,L-1.8,4.9):
   G.box('di-glass',(u,1.9,-.08),(2.15,1.25,.12))
   for dx in [-1.1,0,1.1]:G.box('di-frame',(u+dx,1.9,-.18),(.055,1.4,.08))
   G.box('di-white',(u,1.2,-.23),(2.4,.12,.4))
   G.box('di-door',(u+1.65,1.3,-.1),(.95,2.5,.14))
   G.box('di-frame',(u+1.95,1.25,-.2),(.04,.2,.07))
   G.box('di-ac',(u,.65,-.18),(1,.65,.35))
   for y in np.arange(.39,.94,.09):G.box('di-shadow',(u,y,-.37),(.9,.025,.025))
 # Front office glass and small setback porch; no fake open room.
 G=Frame(B,61.7,3146,math.pi/2,y=0)
 G.box('di-glass',(0,1.75,-.15),(7.4,2.9,.1));G.text('OFFICE',(0,3.45,-.25),.42,'di-letter')
 for x in [-3.7,-1.3,1.3,3.7]:G.box('di-frame',(x,1.75,-.24),(.07,3,.1))
 # Kidney-shaped drained pool and low enclosure seen in aerial sale imagery.
 pool=Polygon([(66+ (4.4+.8*math.sin(2*a))*math.cos(a),3175+ (7+.7*math.sin(a))*math.sin(a)) for a in np.linspace(0,math.tau,65)[:-1]])
 # Bounded floor triangles avoid long skinny pool-border triangles at world coordinates.
 for x in range(39,130,4):
  for z in range(3138,3215,4):
   B.planar('di-asphalt',box(x,z,min(x+4,130),min(z+4,3215)).difference(pool),.02,True)
 B.planar('di-paving',pool.buffer(2).difference(pool),.09,True)
 B.planar('di-pool',pool,-.25,True);B.shell(pool,-.3,.09,'di-pool',roof=False)
 B.planar('di-white',pool.buffer(.25).difference(pool),.12)
 fence=list(pool.buffer(2).exterior.coords)
 for a,b in zip(fence,fence[1:]):
  B.tube('di-white',(a[0],1.05,a[1]),(b[0],1.05,b[1]),.04,6)
 for a in fence[::3]:B.box('di-white',(a[0],.55,a[1]),(.07,1.1,.07))
 # Pool pavilion and office porch are roof-only structures, not solid boxes.
 gazebo=footprint('way/457939123');B.planar('di-paving',gazebo,.13,True)
 B.planar('di-roof',gazebo,3.2);B.shell(gazebo,3.08,3.28,'di-blue',roof=False,solid=False)
 ring=list(gazebo.exterior.coords)
 for x,z in ring[:-1]:F.box('di-white',(x,1.6,z),(.14,3.2,.14),True)
 # Slender radial roof seams retain its curved footprint.
 gx,gz=gazebo.centroid.x,gazebo.centroid.y
 for x,z in ring[:-1]:B.tube('di-frame',(gx,3.24,gz),(x,3.24,z),.025,6)
 porch=footprint('way/1219935118');B.planar('di-paving',porch,.07,True);B.planar('di-roof',porch,3.4)
 B.shell(porch,3.28,3.5,'di-blue',roof=False,solid=False)
 for x,z in list(porch.exterior.coords)[::2]:F.box('di-white',(x,1.72,z),(.15,3.4,.15),True)
 # Historic north pylon: blue panel, red MOTEL lettering, framed white piers.
 for x in [45,49]:F.box('di-white',(x,5.5,3142),(.6,11,.8),True)
 for yaw in [0,math.pi]:
  G=Frame(B,47,3142,yaw,y=0);G.box('di-white',(0,7.8,-.45),(5.6,3.4,.25));G.box('di-blue',(0,10.3,-.45),(5.6,1.7,.25))
  G.text('DIAMOND INN',(0,10.3,-.61),.51,'di-letter');G.text('MOTEL',(0,8.2,-.61),1.05,'di-red');G.text('4605',(0,6.9,-.61),.45,'di-blue')
 # Separate rectangular roadside sign nearer the elephant.
 for z in [3174.5,3179.5]:F.box('di-white',(42,4,z),(.3,8,.3),True)
 for yaw in [math.pi/2,-math.pi/2]:
  G=Frame(B,42,3177,yaw,y=0);G.box('di-white',(0,7.3,-.25),(5.6,3,.25));G.text('DIAMOND',(0,7.9,-.4),.62,'di-red');G.text('MOTEL',(0,6.8,-.4),.8,'di-red')
 B.source='podium/yard';elephant(B)
 B.detail=1
 for x,z,h in [(58,3162,8),(60,3187,9),(96,3163,8),(102,3189,9),(83,3179,10)]:palm(B,x,z,h)
 for x,z in [(49,3167),(51,3186),(88,3174),(91,3183)]:
  B.planar('di-soil',Point(x,z).buffer(2),.02)
  for j in range(7):B.sphere('di-leaf',(x+math.sin(j*2.4),.6,z+math.cos(j*2.4)),.8,10,6,scale=(1,.7,1))
 for x in np.arange(78,114,4.4):
  F.box('di-line',(x,.015,3157),(.08,.025,5));F.box('di-line',(x,.015,3198),(.08,.025,5))
 for x,z in [(81,3144),(104,3145),(121,3185),(96,3208)]:F.box('di-ac',(x,4,z),(1.5,.7,1.3))
 B.detail=0
 return dict(key=KEY,name='Diamond Inn Motel exterior',center=[88,0,3177],bounds=[38,3137,131,3216],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
