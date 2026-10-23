"""Nirvana southern wings. Mapped plans, owner September2025 balcony photograph.
Wing heights and room spacing are photo estimates; no room interiors implied.
"""
from common import *
from forum_shops import facade_frame
KEY='nirvanaAncillary'
IDS=['way/364846549','way/364846550','way/1424222039']
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/motel';B.detail=0
 W=Frame(B,0,0,y=0);plans=[footprint(i) for i in IDS[:2]]
 for p in plans:
  B.shell(p,.24,6.3,'nv-masonry',roof=False);B.planar('nv-roof',p,6.3,True)
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,_,_=facade_frame(B,a,b,p,0)
   G.box('nv-white',(L/2,6.27,-.21),(L+.1,.22,.55))
   for y in [.4,3.2]:G.box('nv-fascia',(L/2,y,-.045),(L,.16,.12))
   north=(a[1]+b[1])/2<2720 and L>8
   for u in np.arange(1.9,L-1,3.9):
    for base in [.35,3.25]:
     G.box('nv-glass',(u,base+1.45,-.075),(1.4,1.35,.12))
     for dx in [-.73,0,.73]:G.box('nv-white',(u+dx,base+1.45,-.16),(.045,1.44,.08))
     for y in [.75,2.15]:G.box('nv-white',(u,base+y,-.16),(1.5,.05,.08))
     if north:
      G.box('nv-door',(u+1.25,base+1.1,-.08),(.85,2.2,.13))
      for dx in [-.46,.46]:G.box('nv-fascia',(u+1.25+dx,base+1.12,-.16),(.05,2.3,.07))
      G.box('nv-fascia',(u+1.25,base+2.26,-.16),(.95,.06,.08))
      for yy in [.5,1.15,1.8]:G.box('nv-panel',(u+1.25,base+yy,-.17),(.6,.4,.04))
      G.box('nv-metal',(u+1.56,base+1.1,-.21),(.035,.18,.05))
      G.box('nv-ac',(u-.5,base+2.15,-.3),(.8,.48,.52))
      for yy in np.arange(1.97,2.35,.06):G.box('nv-shadow',(u-.5,base+yy,-.57),(.7,.022,.02))
      G.box('nv-planter',(u,base+.86,-1.63),(.6,.23,.24))
      for j in range(5):B.sphere('nv-flower',G.p(u+(j-2)*.1,base+1.02,-1.63),.085,6,4)
   if north:
    # Floor and upper gallery, with an opening in the rail at the eastern stair.
    for base in [.35,3.25]:
     G.box('nv-fascia',(L/2,base-.08,-.85),(L,.16,1.7),True)
     for u in np.arange(.15,L,.22):
      if base>2 and p.bounds[0]>98 and 5.15<u<6.85:continue
      G.box('nv-fascia',(u,base+.5,-1.67),(.025,1,.025))
     segments=[(0,L)] if base<2 or p.bounds[0]<98 else [(0,5.15),(6.85,L)]
     for lo,hi in segments:G.box('nv-fascia',((lo+hi)/2,base+1,-1.67),(hi-lo,.055,.06),True)
    for u in np.arange(.3,L,4):G.box('nv-fascia',(u,1.75,-1.6),(.08,3.1,.08),True)
  cx,cz=p.centroid.coords[0]
  W.box('nv-ac',(cx,6.6,cz),(1.5,.6,1.2))
 # Stairs rise southward toward the north-facing gallery of the long wing.
 x=105.65;z=2711.35;run=5.85;rise=2.9
 B.face('nv-fascia',[(x-.65,.35,z),(x+.65,.35,z),(x+.65,3.25,z+run),(x-.65,3.25,z+run)],True)
 for i in range(18):W.box('nv-fascia',(x,.35+(i+1)*rise/18-.03,z+(i+.5)*run/18),(1.3,.06,run/18))
 for xx in [x-.7,x+.7]:
  W.tube('nv-fascia',(xx,1.4,z),(xx,4.3,z+run),.03,6)
  for t in np.linspace(0,1,19):W.tube('nv-fascia',(xx,.35+rise*t,z+run*t),(xx,1.4+rise*t,z+run*t),.018,5)
 # Existing small mapped roof is an open entry awning, not an enclosed gray block.
 canopy=footprint(IDS[2]);B.shell(canopy,2.95,3.12,'nv-white',roof=True)
 for x,z in [(60.5,2707.8),(70.4,2707.8)]:W.box('nv-fascia',(x,1.65,z),(.09,2.6,.09),True)
 main=footprint('way/364846548');site=box(35,2699.2,125,2728).difference(unary_union(plans+[main.buffer(.9)]))
 for x in range(35,125,3):
  for z in range(2699,2728,3):B.planar('nv-asphalt',site.intersection(box(x,z,x+3,z+3)),.26,True)
 for x in np.arange(74,120,2.8):W.box('nv-line',(x,.275,2703),(.07,.018,4.6))
 # Small circular landscaped court in satellite imagery west of the rear wing.
 garden=Point(79,2720).buffer(3.15,resolution=32)
 B.planar('nv-paving',garden,.29,True)
 W.lathe('nv-planter',79,2720,[(.29,.85),(.65,.85)],20)
 W.lathe('nv-paving',79,2720,[(.65,.5),(.86,.35)],20)
 for x,z in [(120.5,2703),(120.5,2710),(82,2718)]:
  W.box('nv-planter',(x,.5,z),(.7,.5,.7))
  for j in range(8):
   a=j*math.tau/8;W.tube('nv-leaf',(x,.7,z),(x+.35*math.sin(a),1.5,z+.35*math.cos(a)),.025,5)
 return dict(key=KEY,name='Nirvana southern motel wings',center=[94,0,2717],bounds=[34,2698,126,2729],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
