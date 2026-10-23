"""Wyoming/Casino Center one-storey frontage; August2024 photo and satellite."""
from common import *
from forum_shops import facade_frame
from courtyard_525 import palm
KEY='wyoming17Frontage';YAW=-math.atan2(1.648,30.17)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/wyoming-17';B.detail=0;p=footprint('way/689003952');F=Frame(B,1771.835,-4049.525,YAW,y=0)
 B.shell(p,.18,4.1,'w17-white-stucco',roof=False);B.planar('w17-roof-paint',p,3.95,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.02)
  G.box('w17-red-paint',(L/2,3.87,-.07),(L,.45,.16));G.box('w17-cream-paint',(L/2,4.16,-.06),(L,.14,.19))
  if nz>.8:
   # Two grouped storefronts, central opaque pier, black security grilles.
   for lo,hi in [(1.1,14.2),(21.3,26.0)]:
    G.box('w17-frame-paint',((lo+hi)/2,1.85,-.10),(hi-lo,2.58,.12));G.box('w17-glass',((lo+hi)/2,1.85,-.18),(hi-lo-.12,2.42,.04))
    for u in np.arange(lo,hi,.92):G.box('w17-frame-paint',(float(u),1.85,-.23),(.045,2.56,.05))
    for y in [.56,2.85,3.12]:G.box('w17-frame-paint',((lo+hi)/2,y,-.23),(hi-lo,.05,.05))
   for u in [10.4,12.0,23.2]:
    G.box('w17-frame-paint',(u,1.4,-.27),(1.22,2.42,.07));G.box('w17-glass',(u,1.4,-.32),(1.1,2.28,.04));G.tube('w17-metal-paint',(u-.39,1.0,-.37),(u-.39,1.55,-.37),.022,6)
   for u in np.arange(1.2,14.1,.18):G.box('w17-grille-paint',(float(u),1.84,-.4),(.018,2.45,.025))
   for y in [.7,1.45,2.2,3.05]:G.box('w17-grille-paint',(7.65,y,-.4),(12.9,.025,.025))
   for u in [3,8,24.5]:G.box('w17-paper-paint',(u,1.83,-.26),(1.12,1.88,.015))
   for u in [4.5,18,27.2]:G.box('w17-fixture-paint',(u,3.5,-.27),(.3,.22,.35))
  elif nx>.8:
   # Historical painted signage omitted until current east wall is corroborated.
   G.box('w17-frame-paint',(L*.75,1.4,-.1),(1.1,2.4,.1));G.box('w17-door-paint',(L*.75,1.4,-.18),(.95,2.25,.04))
  else:
   for u in [L*.2,L*.7]:G.box('w17-vent-paint',(u,2.4,-.09),(1.2,.55,.16))
   G.box('w17-door-paint',(L*.45,1.36,-.09),(1.15,2.35,.13))
  for u in [.3,L-.3]:G.tube('w17-metal-paint',(u,.3,-.11),(u,3.6,-.11),.03,6)
 # Weathered roof: mechanical plant, ducting and the back of a large billboard.
 for u,w,ww,dd in [(6,4,1.6,1.4),(12,10,2.8,2.0),(21,11,1.6,1.8),(27,5,1.4,1.2)]:
  F.box('w17-service-paint',(u,4.38,w),(ww,.8,dd));F.box('w17-vent-paint',(u,4.8,w),(ww*.8,.04,dd*.8))
 for u in [4,11,19,26]:F.box('w17-rooflight-paint',(u,4.08,3.5),(3.2,.18,.7))
 F.box('w17-billboard-back-paint',(12.0,5.56,13.25),(18,2.5,.12))
 for u in np.arange(3,21.1,1.5):
  F.tube('w17-metal-paint',(float(u),3.96,13.2),(float(u),6.8,13.2),.045,6);F.tube('w17-metal-paint',(float(u),4,10.7),(float(u),6.2,13.2),.035,6)
 for y in [4.3,6.8]:F.tube('w17-metal-paint',(3,y,13.2),(21,y,13.2),.045,6)
 # Ground aprons and narrow service sheds at the west boundary.
 site=F.poly([(-5,-1),(35,-1),(35,18),(-5,18)]).difference(p);B.planar('w17-paving-concrete',site,.18,True)
 for w in [3.5,10.3]:
  F.box('w17-shed-paint',(-2.65,1.55,w),(3.8,2.7,4.8),True)
  for sign in [-1,1]:B.upface('w17-roof-paint',[F.p(-2.65,3.4,w-2.5),F.p(-2.65+sign*2,2.95,w-2.5),F.p(-2.65+sign*2,2.95,w+2.5),F.p(-2.65,3.4,w+2.5)])
  F.box('w17-door-paint',(-2.65,1.5,w+2.42),(1.6,2.5,.05))
 for u in [8,17]:palm(B,F,u,16.3,9.5 if u==8 else 11)
 # Remove hidden palm colliders from visible batches, retain in collision.
 B.groups={k:g for k,g in B.groups.items() if g['material']!='c525-collision'}
 samples=[]
 for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.2):
  for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.2):
   if p.buffer(-.3).contains(Point(x,z)):samples.append([float(x),4.5,float(z)])
 Path('build/city-exteriors/wyoming-17-frontage-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Wyoming17 street frontage',center=[1787,0,-4041],bounds=[1765,-4052,1808,-4028],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
