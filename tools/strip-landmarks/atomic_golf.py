"""Atomic Golf: mapped curved clubhouse; four levels per Vertex CO record.
Floor heights/range edge are estimates bounded by mapped streets. Original graphics.
"""
from common import *
from forum_shops import facade_frame
KEY='atomicGolf'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/clubhouse';B.detail=0
 p=footprint('way/1213440758');ps=list(p.exterior.coords)
 # Actual open west bays: slabs/columns, not a sealed warehouse.
 for y in [.24,4.74,9.24,13.74,18.24]:
  B.shell(p,y-.24,y,'ag-white',roof=False,solid=True);B.planar('ag-floor',p,y,True)
 for a,b in zip(ps,ps[1:]):
  if math.dist(a,b)<.3:continue
  F,L,nx,nz=facade_frame(B,a,b,p,.04)
  west=nx<-.6
  if west:
   for u in np.linspace(0,L,max(2,round(L/4.6)+1)):
    F.box('ag-white',(u,9,0),(.35,18,.35),True)
   for floor in range(4):
    y=.24+floor*4.5
    for u in np.arange(2.4,L-1,4.6):
     F.box('ag-mat',(u,y+.025,1.6),(3.6,.05,2.4))
     F.box('ag-black',(u,y+2.8,3),(1.25,.8,.12))
     F.box('ag-screen',(u,y+2.8,2.92),(1.12,.66,.025))
    # Bay furnishings are batched exterior fixtures visible from the range.
    B.detail=1
    for u in np.arange(2.4,L-1,4.6):
     F.box('ag-gray',(u,y+.5,5),(2.7,.16,.8))
     F.box('ag-white',(u,y+.95,5.4),(2.7,.9,.12))
     for dx in [-1.15,1.15]:F.box('ag-metal',(u+dx,y+.22,5),(.05,.45,.6))
     F.box('ag-black',(u,y+.72,3.8),(1.8,.08,.6))
     F.box('ag-metal',(u,y+.37,3.8),(.1,.7,.1))
    B.detail=0
    # back wall stands inside, exposing real-depth covered bays.
    F.box('ag-gray',(L/2,y+2.1,7.2),(L,4.15,.18),True)
    F.box('ag-black',(L/2,y+4.23,3.5),(L,.12,7))
    if floor:
     F.tube('ag-metal',(0,y+.7,.05),(L,y+.7,.05),.025,6)
  else:
   F.box('ag-white',(L/2,9.2,0),(L,18.4,.18),True)
   for u in np.arange(2.4,L,2.4):F.box('ag-joint',(u,9.2,-.12),(.018,18.3,.025))
   for y in [4.7,9.2,13.7]:F.box('ag-joint',(L/2,y,-.12),(L,.018,.025))
  F.box('ag-white',(L/2,18.4,-.1),(L,.32,.6))
 # East entry/photo face, central straight section in mapped footprint.
 F=Frame(B,1647.5,-3718,-math.pi/2,y=0)
 F.box('ag-white',(0,16.3,-.15),(45,5,.4))
 F.box('ag-black',(0,11.8,-.55),(44,3.2,.45))
 F.text('ATOMIC',(0,16.6,-.4),1.55,'ag-blue')
 F.text('GOLF',(1.5,14.8,-.4),1.55,'ag-blue')
 # Raised original atom emblem; no copied photograph or ad texture.
 for tilt in [-.65,.65,0]:
  F.path('ag-purple',[(10+2.2*math.cos(a),16+1.15*math.sin(a)*math.cos(tilt),-.45+1.15*math.sin(a)*math.sin(tilt)) for a in np.linspace(0,math.tau,49)],.08,8)
 B.sphere('ag-blue',F.p(10,16,-.5),.7,20,12)
 F.text('1850',(-20,17.1,-.4),.6,'ag-blue')
 F.text('BIGGER • BETTER • BOLDER',(0,11.7,-.8),.65,'ag-purple')
 for x in [-15,-10,-5,0,5,10,15]:
  F.box('ag-glass',(x,3.15,-.2),(4.7,5.8,.12))
  F.box('ag-metal',(x-2.4,3.15,-.32),(.08,5.9,.16))
 F.box('ag-metal',(0,6.15,-.32),(35,.12,.2))
 F.box('ag-black',(0,6.5,-3.3),(38,.24,6.6),True)
 F.box('ag-white',(0,6.67,-3.3),(38,.10,6.6))
 for x in [-17,-10,-3,4,11,17]:
  F.lathe('ag-white',x,-5.6,[(.24,.24),(4.8,.24),(5.4,.3),(5.85,.55),(6.35,1.05),(6.45,1.05)],24)
  F.box('ag-white',(x,3.2,-5.6),(.4,5.9,.4),True)
 # Entry ball bollards and the freestanding atomic sculpture in the photo.
 for i,x in enumerate(np.arange(-17,18,3.5)):
  B.sphere(['ag-purple','ag-white','ag-red'][i%3],F.p(x,.57,-7.1),.52,20,12)
 F.tube('ag-metal',(12,.2,-5),(12,3.6,-5),.09,10)
 B.sphere('ag-blue',F.p(12,4.2,-5),.65,24,16)
 for tilt in [-.8,0,.8]:
  F.path('ag-purple',[(12+1.9*math.cos(a),4.2+1.6*math.sin(a)*math.cos(tilt),-5+1.6*math.sin(a)*math.sin(tilt)) for a in np.linspace(0,math.tau,65)],.09,10)
 B.source='podium/forecourt';B.planar('ag-paving',box(1648,-3747,1655,-3690),.05,True)
 # Southern terrace omitted by the original clubhouse footprint. Two levels are
 # estimated from the October2025 street panorama, not measured elevations.
 B.source='podium/south-terrace'
 south=footprint('way/1553042969')
 for y in [.24,4.74,9.24]:
  B.shell(south,y-.22,y,'ag-white',roof=False,solid=True)
  B.planar('ag-floor' if y<9 else 'ag-white',south,y,True)
 coords=list(south.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  midpoint=Point((a[0]+b[0])/2,(a[1]+b[1])/2)
  if p.boundary.distance(midpoint)<.03:continue # shared join: no duplicate wall
  F,L,nx,nz=facade_frame(B,a,b,south,.02)
  F.box('ag-white',(L/2,9.34,0),(L,.42,.4))
  F.box('ag-black',(L/2,8.98,.12),(L,.06,.8))
  bays=max(1,round(L/4.5))
  for j in range(bays):
   u=(j+.5)*L/bays
   F.box('ag-glass',(u,2.42,.4),(L/bays-.1,4.24,.10))
   F.box('ag-metal',(u-L/bays/2,2.42,.32),(.08,4.3,.16))
   F.box('ag-glass',(u,5.28,.1),(L/bays-.12,1.06,.065))
   F.box('ag-metal',(u-L/bays/2,5.3,.05),(.055,1.12,.10))
  F.box('ag-metal',(L/2,5.86,.05),(L,.065,.1))
  # Glass guard collision belongs to the terrace, not the ground walkway.
  F.box('ag-collision',(L/2,5.28,.1),(L,1.06,.12),True)
  for u in np.linspace(.5,max(.5,L-.5),max(2,round(L/6)+1)):
   F.box('ag-white',(u,2.48,.75),(.36,4.5,.36),True)
   F.lathe('ag-white',u,.75,[(4.74,.22),(7.5,.22),(8.2,.35),(8.8,.72),(9.0,.88)],24)
   F.box('ag-collision',(u,6.8,.75),(.44,4.1,.44),True)
 apron=south.buffer(2).difference(south.union(p))
 B.planar('ag-paving',apron,.08,True)
 # Keep collision-only boxes out of rendered batches.
 for k in list(B.groups):
  if B.groups[k]['material']=='ag-collision':del B.groups[k]
 # Range is kept between Chicago/Philadelphia mapped street boundaries.
 B.source='podium/range'
 rp=Polygon([(1385,-3766),(1381,-3700),(1547,-3688),(1600,-3678),(1611,-3757)])
 B.planar('ag-range',rp,.02,True)
 for x,z,r,mat in [(1560,-3730,10,'ag-green'),(1535,-3708,9,'ag-purple'),(1510,-3742,12,'ag-blue'),(1470,-3722,15,'ag-red'),(1425,-3730,8,'ag-green')]:
  ring=Point(x,z).buffer(r,resolution=48).difference(Point(x,z).buffer(r-.25,resolution=48));B.planar(mat,ring,.035)
 # Tall poles and tension lines, no dense mesh grid or per-strand colliders.
 edges=[((1385,-3766),(1611,-3757)),((1381,-3700),(1547,-3688)),((1385,-3766),(1381,-3700))]
 for a,b in edges:
  for t in np.linspace(0,1,max(2,round(math.dist(a,b)/18)+1)):
   x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t
   B.tube('ag-metal',(x,.05,z),(x,38,z),.17,10,r2=.09)
  B.detail=1
  for y in [8,16,24,32,38]:B.tube('ag-net',(a[0],y,a[1]),(b[0],y,b[1]),.018,4)
  B.detail=0
 return dict(key=KEY,name='Atomic Golf exterior and range',center=[1600,0,-3715],bounds=[1381,-3766,1655,-3654],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
