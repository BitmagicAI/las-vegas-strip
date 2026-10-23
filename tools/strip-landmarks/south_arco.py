"""3873 S Las Vegas Blvd ARCO/ampm. Jan2024 photo and satellite.
Mapped canopy/store retained; heights and pump locations estimated.
"""
from common import *
from forum_shops import facade_frame
KEY='southArco'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/fuel';B.detail=0;W=Frame(B,0,0,y=0)
 canopy=footprint('way/402587341');store=footprint('way/402587340')
 B.shell(canopy,4.6,5.12,'sar-white',roof=False);B.planar('sar-soffit',canopy,4.6,True)
 # Hip roof: a shallow terracotta skirt surrounding the raised central flat cap.
 outer=list(canopy.exterior.coords)[:-1];inner=list(canopy.buffer(-2).exterior.coords)[:-1]
 # offset polygon's ordering may differ; pair nearest corners explicitly.
 for i,a in enumerate(outer):
  b=outer[(i+1)%4];aa=min(inner,key=lambda q:math.dist(a,q));bb=min(inner,key=lambda q:math.dist(b,q))
  B.face('sar-tile',[(a[0],5.12,a[1]),(b[0],5.12,b[1]),(bb[0],5.88,bb[1]),(aa[0],5.88,aa[1])])
 B.planar('sar-roof',canopy.buffer(-2),5.88)
 for a,b in zip(list(canopy.exterior.coords),list(canopy.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,canopy,.015)
  G.box('sar-blue',(L/2,4.91,-.05),(L,.18,.12))
  G.box('sar-white',(L/2,4.66,-.05),(L,.07,.12))
  G.box('sar-white',(L/2,5.12,-.05),(L,.08,.12))
  if a[0]<50 and b[0]<50 or a[1]>2113 and b[1]>2113:
   G.box('sar-white',(L/2,4.91,-.14),(4.3,.5,.13));G.text('ARCO',(L/2-.3,4.91,-.22),.42,'sar-blue')
   pts=[G.p(L/2+1.5,5.12,-.23),G.p(L/2+1.75,4.91,-.23),G.p(L/2+1.5,4.7,-.23),G.p(L/2+1.25,4.91,-.23)];B.face('sar-red',pts)
 for x in [52.5,61.9]:
  for z in [2100,2109]:
   W.box('sar-cream',(x,2.43,z),(.7,4.34,.7),True)
   W.box('sar-island',(x,.32,z),(1.7,.22,3.5),True)
   px=x;zz=z+1.05
   W.box('sar-white',(px,1.25,zz),(1.05,1.65,.65),True)
   W.box('sar-blue',(px,.65,zz),(1.08,.45,.68))
   for side in [-1,1]:
    G=Frame(B,px,zz+side*.34,math.pi if side>0 else 0,y=0)
    G.box('sar-black',(0,1.47,-.02),(.86,.62,.05));G.box('sar-display',(0,1.62,-.055),(.52,.19,.025))
    G.text('00.00',(0,1.62,-.075),.12,'sar-white')
    for u in [-.27,0,.27]:G.box('sar-yellow',(u,1.22,-.055),(.16,.08,.025))
   for side in [-1,1]:
    W.path('sar-black',[(px+side*.55,1.95,zz),(px+side*.77,1.75,zz),(px+side*.87,.7,zz),(px+side*.73,.56,zz),(px+side*.57,.9,zz)],.035,6)
   for dx in [-.68,.68]:W.tube('sar-white',(x+dx,.26,z+1.5),(x+dx,1.15,z+1.5),.065,8)
 for x in [53,61]:
  for z in [2098,2106,2111]:W.box('sar-light',(x,4.57,z),(.35,.05,.65))
 B.shell(store,.24,4.1,'sar-cream',roof=False);B.planar('sar-roof',store,4.1,True)
 for a,b in zip(list(store.exterior.coords),list(store.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,store,.035)
  G.box('sar-white',(L/2,4.05,-.08),(L,.15,.24))
  west=a[0]<87 and b[0]<87
  if west:
   G.box('sar-orange',(L/2,3.05,-.14),(L,.32,.38))
   G.box('sar-panel',(L/2,3.63,-.07),(L,.75,.15))
   for y in np.arange(3.32,3.95,.08):G.box('sar-joint',(L/2,y,-.16),(L,.024,.02))
   for u in np.arange(1,L-.5,1.45):
    G.box('sar-glass',(u,1.63,-.08),(1.35,2.35,.13))
    for dx in [-.69,.69]:G.box('sar-frame',(u+dx,1.63,-.17),(.055,2.45,.07))
    G.box('sar-frame',(u,.43,-.17),(1.45,.08,.08));G.box('sar-frame',(u,2.82,-.17),(1.45,.08,.08))
    if int(u)%3==0:
     G.box('sar-poster',(u,1.2,-.185),(.72,1,.015));G.text('FRESH',(u,1.48,-.2),.13,'sar-white');G.text('DAILY',(u,1.23,-.2),.15,'sar-white')
   if L>10:
    G.box('sar-white',(L/2,3.68,-.21),(3.6,.95,.12));G.text('ampm',(L/2,3.68,-.29),.67,'sar-orange')
    for u in [L/2-.45,L/2+.45]:G.box('sar-metal',(u,1.35,-.23),(.04,.4,.07))
  else:
   G.box('sar-joint',(L/2,1,-.03),(L,.025,.02))
   if L>10:
    G.box('sar-service',(L*.65,1.4,-.08),(1,2.3,.12))
    G.box('sar-vent',(L*.3,2.8,-.08),(1.3,.8,.12))
 for x,z in [(90,2107),(91,2119)]:W.box('sar-metal',(x,4.5,z),(1.6,.8,1.4))
 # Tall roadside pylon and lower price cabinet. Rates intentionally omitted.
 P=Frame(B,40,2124,math.pi/2,y=.26)
 P.box('sar-white',(0,5.5,0),(.28,11,.3),True);P.box('sar-white',(0,10.7,0),(5.7,1.15,.2),True)
 P.box('sar-blue',(-1,10.7,-.13),(3.5,.94,.05));P.text('ARCO',(-1,10.7,-.18),.6,'sar-white');P.text('ampm',(1.85,10.7,-.18),.46,'sar-orange')
 P.box('sar-cream',(0,.65,0),(5.8,1.3,.5),True);P.box('sar-blue',(0,1.65,-.02),(5.6,1.2,.3),True)
 P.text('ARCO',(0,1.9,-.2),.36,'sar-white');P.text('GASOLINE   DIESEL',(0,1.4,-.2),.22,'sar-white')
 site=box(34,2090,99,2129).difference(store.buffer(.1))
 for x in range(34,99,3):
  for z in range(2090,2129,3):B.planar('sar-asphalt',site.intersection(box(x,z,x+3,z+3)),.26,True)
 B.planar('sar-paving',store.buffer(1.35).difference(store),.34,True)
 for x in np.arange(68,82,2.8):W.box('sar-line',(x,.28,2125),(.07,.02,4.2))
 return dict(key=KEY,name='ARCO and ampm south Strip',center=[70,0,2110],bounds=[33,2089,100,2130],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
