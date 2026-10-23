"""1701 Rexford exterior courtyard block. Jan2021/22 references; dimensions estimated.
Courtyard is an actual open void, not water placed on a solid roof. No unit interiors.
"""
from common import *
from forum_shops import facade_frame
KEY='rexfordCourtyard1701'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/apartments';B.detail=0
 F=Frame(B,2049.834,-3920.572,yaw=-math.atan2(1.636,35.863),y=0)
 p=footprint('way/1236725809');p=p.buffer(-1.7,join_style=1).buffer(1.7,resolution=12)
 court=F.poly([(13,11),(23,11),(23,39),(13,39)])
 rooms=p.difference(court.buffer(2,join_style=2));passage=F.poly([(23,10.8),(37,10.8),(37,13.2),(23,13.2)])
 B.shell(rooms.difference(passage),.18,3.0,'rc-pale-stucco',roof=False)
 B.shell(rooms,3.0,5.95,'rc-pale-stucco',roof=False)
 roof=p.buffer(.35,join_style=1).difference(court)
 B.shell(roof,5.95,6.12,'rc-roof-edge-paint',roof=False);B.planar('rc-roof-paint',roof,6.12,True)
 floors=p.difference(rooms).union(passage.intersection(p))
 pool=F.poly([(16.3,22),(21.7,22),(21.7,35),(16.3,35)])
 B.planar('rc-floor-concrete',floors.difference(pool),.18,True)
 gallery=court.buffer(2,join_style=2).difference(court)
 B.shell(gallery,2.86,3.0,'rc-roof-edge-paint',roof=False);B.planar('rc-floor-concrete',gallery,3.0,True)
 # Street/rear horizontal windows and local frames; no transparent holes into invented rooms.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.035)
  if L<3:continue
  for y in [1.75,4.65]:
   count=max(1,round(L/4.2))
   for j in range(count):
    u=(j+.5)*L/count;x,_,z=G.p(u,0,0)
    if passage.buffer(.4).contains(Point(x,z)) and y<3:continue
    if nx>.7 and any(abs(u-strip)<1.1 for strip in np.arange(6,L,13)):continue
    width=2.1 if j%3!=1 else .85
    G.box('rc-frame-paint',(u,y,-.1),(width+.12,1.03,.09));G.box('rc-glass',(u,y,-.16),(width,.9,.04))
    for dy in [-.25,0,.25]:G.box('rc-louver-paint',(u,y+dy,-.2),(width,.028,.065))
    G.box('rc-frame-paint',(u,y,-.22),(.045,.9,.07))
  if nx>.7:
   # Alternating white screen strips from the eastern street image.
   for u in np.arange(6,L,13):
    x,_,z=G.p(u,0,0)
    if passage.buffer(1.2).contains(Point(x,z)):continue
    for yy in np.arange(.35,5.8,.23):
     for dx in [-.34,0,.34]:
      G.box('rc-screen-paint',(u+dx,yy,-.17),(.27,.17,.09))
 # Courtyard faces with exterior room doors and upper access galleries.
 inner=rooms.intersection(court.buffer(2.01,join_style=2))
 for a,b in zip(list(court.buffer(2,join_style=2).exterior.coords),list(court.buffer(2,join_style=2).exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,rooms,.025)
  for u in np.arange(1.8,L-1,4.2):
   x,_,z=G.p(u,0,0)
   for y in [.18,3.0]:
    if y<1 and passage.buffer(.6).contains(Point(x,z)):continue
    G.box('rc-door-paint',(u,y+1.07,-.1),(.88,2.1,.08));G.box('rc-handle-paint',(u+.3,y+1,-.16),(.06,.13,.05))
    G.box('rc-glass',(u+1.2,y+1.5,-.12),(1.1,.85,.05))
 # Continuous upper inner guard; west stair connection uses outer landing.
 edges=[((13,11),(13,18.6)),((13,20.2),(13,39)),((13,39),(23,39)),((23,39),(23,11)),((23,11),(13,11))]
 for aa,bb in edges:
  ap,bp=F.p(aa[0],0,aa[1]),F.p(bb[0],0,bb[1]);a,b=(ap[0],ap[2]),(bp[0],bp[2])
  length=math.dist(a,b)
  for t in np.linspace(0,1,max(2,math.ceil(length/.35)+1)):
   x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t
   B.tube('rc-rail-paint',(x,3.05,z),(x,4.05,z),.025,6)
  B.tube('rc-rail-paint',(a[0],4.05,a[1]),(b[0],4.05,b[1]),.035,8)
  G,L,_,_=facade_frame(B,a,b,court,0);G.box('rc-collision',(L/2,3.55,0),(L,1.05,.1),True)
 # Stair entirely in the court, with landing connecting to west gallery.
 F.stairs(15,13,1.4,2.82,5.6,y=.18)
 landing=F.poly([(11,18.6),(15.7,18.6),(15.7,20.2),(11,20.2)])
 B.planar('rc-floor-concrete',landing,3.0,True)
 for a,b in [((13,20.2),(15.7,20.2)),((15.7,20.2),(15.7,18.6))]:
  F.tube('rc-rail-paint',(a[0],4.05,a[1]),(b[0],4.05,b[1]),.035,8)
  for t in np.linspace(0,1,9):
   u=a[0]+(b[0]-a[0])*t;w=a[1]+(b[1]-a[1])*t;F.tube('rc-rail-paint',(u,3,w),(u,4.05,w),.025,6)
  aa,bb=F.p(a[0],0,a[1]),F.p(b[0],0,b[1]);G,L,_,_=facade_frame(B,(aa[0],aa[2]),(bb[0],bb[2]),court,0);G.box('rc-collision',(L/2,3.55,0),(L,1.05,.1),True)
 # West inner guard is split at the actual stair landing above.
 # Replace ground under pool with basin to avoid coplanar water/floor.
 B.source='podium/pool'
 B.planar('rc-pool-tile',pool,-1.1,True);B.shell(pool,-1.1,.17,'rc-pool-tile',roof=False)
 B.planar('rc_pool',pool,.11)
 B.planar('rc-coping-concrete',pool.buffer(.3,join_style=2).difference(pool),.23,True)
 # Collision-only guard boxes are omitted from rendered batches.
 for k,g in list(B.groups.items()):
  if g['material']=='rc-collision':del B.groups[k]
 site=p.buffer(1.2,join_style=2).difference(p);B.planar('rc-apron-concrete',site,.18,True)
 samples=[]
 for u in np.arange(12,24,.65):
  for w in np.arange(10,40,.65):
   x,y,z=F.p(u,.18,w)
   if floors.buffer(-.4).contains(Point(x,z)) and not pool.buffer(.5).contains(Point(x,z)) and not (14<u<16 and 12<w<20):samples.append([x,y,z])
 Path('build/city-exteriors/rexford-courtyard-1701-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='1701 Rexford courtyard apartments',center=[2067,0,-3894],bounds=[2045,-3923,2088,-3865],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
