"""ARCO1619: mapped canopy/store, August2024 imagery, 11ft posted clearance."""
from common import *
from forum_shops import facade_frame
KEY='oakeyArco'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/fuel';B.detail=0;W=Frame(B,0,0,y=0)
 canopy=footprint('way/316303729');store=footprint('way/316303728');ground=.18;clear=ground+3.3528
 B.shell(canopy,clear,clear+.48,'oa-white-paint',roof=False,solid=False);B.planar('oa-roof-paint',canopy,clear+.48);B.planar('oa-white-paint',canopy,clear,True)
 for a,b in zip(list(canopy.exterior.coords),list(canopy.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,canopy,.025)
  G.box('oa-blue-paint',(L/2,clear+.25,-.035),(L,.24,.09))
  if L<10:
   G.text('ARCO',(L/2,clear+.19,-.11),.24,'oa-white-letter')
 # Two longitudinal pump islands, each with a structural white brick pier and two dispensers.
 F=Frame(B,1891.8,-3954.15,yaw=-math.atan2(7.002,12.922),y=0)
 for u in [-4.5,4.5]:
  F.box('oa-island',(u,.28,0),(1.6,.2,4.4),True);F.box('ms-white-brick-paint',(u,(ground+clear)/2,0),(.55,clear-ground,.55),True)
  for w in [-1.43,1.43]:
   F.box('oa-white-paint',(u,1.25,w),(1.0,1.8,.55),True);F.box('oa-blue-paint',(u,.57,w),(1.02,.4,.58));F.box('oa-blue-paint',(u,2.25,w),(1.15,.33,.65))
   for side in [-1,1]:
    F.box('oa-black-paint',(u,1.53,w+side*.3),(.82,.7,.05));F.box('oa-display',(u,1.7,w+side*.33),(.5,.18,.025))
    for dx in [-.27,0,.27]:F.box('oa-yellow-paint',(u+dx,1.3,w+side*.33),(.15,.08,.025))
   for side in [-1,1]:F.path('oa-black-paint',[(u+side*.53,2,w),(u+side*.7,1.8,w),(u+side*.73,.6,w),(u+side*.56,.55,w),(u+side*.52,.95,w)],.033,8)
   for dx in [-.65,.65]:F.tube('oa-yellow-paint',(u+dx,.18,w),(u+dx,1.05,w),.055,10)
 for u in [-5,0,5]:
  for w in [-2.1,2.1]:F.box('oa-white-paint',(u,clear-.035,w),(.38,.06,.6))
 B.shell(store,ground,3.12,'oa-tan-stucco',roof=False)
 outer=store.buffer(.35,join_style=2);inner=store.buffer(-1.8,join_style=2)
 for poly in parts(outer.difference(inner)):
  for tri in triangles(poly):
   pts=[(x,3.12+min(1,outer.boundary.distance(Point(x,z))/2.15)*.85,z) for x,z in list(tri.exterior.coords)[:-1]];B.upface('oa-terracotta-paint',pts)
 B.planar('oa-roof-paint',inner,3.97)
 for a,b in zip(list(store.exterior.coords),list(store.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,store,.035);G.box('oa-orange-paint',(L/2,3.1,-.18),(L,.15,.45))
  if nx<-.7 and L>10:
   for u in np.arange(1,L-.5,1.5):
    G.box('oa-glass',(float(u),1.65,-.1),(1.38,2.25,.1))
    for dx in [-.7,.7]:G.box('oa-metal-paint',(float(u)+dx,1.65,-.19),(.05,2.35,.06))
    for y in [.48,2.82]:G.box('oa-metal-paint',(float(u),y,-.19),(1.5,.06,.06))
   G.box('oa-white-paint',(L/2,2.66,-.4),(3.3,.55,.13));G.text('ampm',(L/2,2.51,-.5),.43,'oa-orange-letter')
   for u in [L/2-.4,L/2+.4]:G.box('oa-metal-paint',(u,1.4,-.25),(.04,.5,.07))
  elif L>8:
   G.box('oa-metal-paint',(L*.7,1.4,-.08),(1.05,2.4,.12));G.box('oa-vent',(L*.25,2.35,-.1),(1.3,.65,.15))
 for x,z in [(1915,-3955),(1918,-3948)]:W.box('oa-service',(x,4.3,z),(1.4,.65,1.2))
 # Roadside sign; historic variable fuel prices deliberately omitted.
 P=Frame(B,1886,-3944,yaw=math.pi/2,y=0)
 for u in [-.66,.66]:P.box('oa-white-paint',(u,3.15,0),(.12,5.95,.17),True);P.lathe('oa-black-paint',u,0,[(.18,.31),(.82,.31)],16)
 for y,h,mat in [(5.7,.65,'oa-blue-paint'),(4.98,.62,'oa-white-paint'),(3.5,2.05,'oa-blue-paint')]:
  P.box('oa-white-paint',(0,y,0),(1.8,h+.14,.18));P.box(mat,(0,y,-.11),(1.66,h,.05))
 P.text('ARCO',(0,5.55,-.16),.36,'oa-white-letter');P.text('ampm',(0,4.83,-.16),.4,'oa-orange-letter');P.text('GASOLINE',(0,3.9,-.16),.19,'oa-white-letter');P.text('CASH / CREDIT',(0,3.1,-.16),.16,'oa-white-letter')
 # Forecourt follows the bounded property apron, leaves city roads and neighboring Luv-It untouched.
 site=Polygon([(1880,-3968),(1903,-3972),(1920,-3967),(1924,-3961),(1924,-3939),(1896,-3936),(1878,-3946)]).difference(store)
 B.planar('oa-asphalt',site,.18,True);B.planar('oa-paving',store.buffer(.8).difference(store),.22,True)
 obstacles=unary_union([F.poly([(u-.9,-2.4),(u+.9,-2.4),(u+.9,2.4),(u-.9,2.4)]) for u in [-4.5,4.5]])
 samples=[]
 for x in np.arange(1880,1924,1.3):
  for z in np.arange(-3970,-3937,1.3):
   q=Point(x,z)
   if site.buffer(-.65).covers(q) and not obstacles.buffer(.4).covers(q) and q.distance(Point(1886,-3944))>1.3:samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/oakey-arco-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='ARCO and ampm at Oakey',center=[1904,0,-3952],bounds=[1877,-3973,1926,-3935],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
