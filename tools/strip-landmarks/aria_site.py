"""ARIA missing west podium and convention wing from Earth2022/official plan.
Physical elevations are explicitly estimated; original casino interiors are retained.
"""
from common import *
import random
from forum_shops import facade_frame
from luxor_parking import soffit
from venetian_pool_garden import gardens
KEY='ariaSite';IDS=['way/463856739'];DECK=14.7

def oval(x,z,rx,rz,a=0):return rotate(scale(Point(x,z).buffer(1,resolution=32),rx,rz,origin=(x,z)),a,origin=(x,z))
def pool_shapes():
 return [oval(-575,983,10,16,-15),oval(-519,995,19,9,-20),oval(-549,1037,24,9,-20),oval(-472,1033,19,13,15)]
def deck_shape():return Polygon([(-610,956),(-578,969),(-537,978),(-498,978),(-466,983),(-418,991),(-411,1038),(-433,1085),(-602,1085)]).buffer(2).buffer(-2).union(unary_union(pool_shapes()).buffer(3))
def exterior(B):
 B.property=KEY+'-exterior';B.source='aria-west-podium';B.detail=0
 deck=deck_shape();wet=unary_union(pool_shapes());stairwell=box(-605.3,1021.8,-599.7,1031.2);paving=deck.difference(wet.buffer(.35)).difference(stairwell);B.planar('aria-paving',paving,DECK,True);B.shell(paving,DECK-.35,DECK,'wa-stone',roof=False);soffit(B,deck.difference(stairwell),DECK-.35)
 # Pool bottoms and coping; water material name opts into the existing water renderer.
 for p in pool_shapes():
  B.planar('vh-pool-tile',p,DECK-1.1,True);B.shell(p,DECK-1.1,DECK,'vh-pool-tile',roof=False)
  B.planar('aria_pool',p,DECK-.15);B.planar('wa-stone',p.buffer(.6).difference(p),DECK+.04,True)
 # West perimeter has a gently draped metal scrim, not a generic solid wall.
 west=list(deck.exterior.coords)
 for a,b in zip(west,west[1:]):
  F,L,nx,nz=facade_frame(B,a,b,deck,0)
  if nx<-.65:
   opening=LineString([a,b]).intersection(box(-617,1019,-595,1023))
   wall=box(0,.2,L,13.8)
   if not opening.is_empty:
    ends=list(opening.coords);u0=LineString([a,b]).project(Point(ends[0]));u1=LineString([a,b]).project(Point(ends[-1]));wall=wall.difference(box(min(u0,u1),0,max(u0,u1),3.0))
   for pp in parts(wall):
    for tri in triangles(pp):B.face('wa-vent',[F.p(u,y,.25) for u,y in list(tri.exterior.coords)[:-1]],True)
   for q in np.arange(0,L,.65):
    if 1019<F.p(q,0,0)[2]<1023:continue
    offset=-.45-1.1*(.5+.5*math.cos(q*math.tau/8))
    F.box('aria-trim',(q,8.1,offset),(.055,12.5,.09))
   for yy in np.arange(2,14,.8):
    line=[]
    for q in np.arange(0,L+.3,.3):
     if yy<3 and 1019<F.p(q,0,0)[2]<1023:
      if len(line)>1:F.path('aria-trim',line,.025,4)
      line=[];continue
     line.append((q,yy,-.45-1.1*(.5+.5*math.cos(q*math.tau/8))))
    if len(line)>1:F.path('aria-trim',line,.025,4)
  # Deck safety edge, with substantial collision but no per-baluster collider.
  F.box('aria-trim',(L/2,DECK+.55,0),(L,1.1,.08),True)
 # Curved spa wing follows the actual mapped footprint; pool-facing glazing is segmented.
 spa=footprint(IDS[0]);B.source='aria-spa';B.planar('cp-roof',spa,25.4,True);B.shell(spa,0,DECK,'wa-stone',roof=False)
 for pp in parts(spa):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   if L<.2:continue
   F.box('wa-glass',(L/2,19.5,-.03),(L,9.4,.12),True)
   for y in [15,18.4,21.8,25.15]:F.box('aria-trim',(L/2,y,-.18),(L,.15,.18))
   for q in np.arange(.2,L,2.4):F.box('aria-trim',(q,19.5,-.18),(.075,9.4,.2))
   F.box('aria-trim',(L/2,25.6,-.2),(L,.4,.7))
 # Roof ribs make the curved plant trellis visible from the towers.
 inner=spa.buffer(-1)
 for x in np.arange(spa.bounds[0]+2,spa.bounds[2],2):
  cut=LineString([(x,920),(x,990)]).intersection(inner)
  for line in (list(cut.geoms) if hasattr(cut,'geoms') else [cut]):
   if line.geom_type=='LineString':B.path('aria-trim',[(xx,26.1,zz) for xx,zz in line.coords],.055,5)
 # Southern convention volume and its glazed faceted north concourse.
 B.source='aria-convention';hall=box(-603,1100,-428,1209);B.planar('aria-paving',hall,DECK,True);B.planar('cp-roof',hall,33,True);soffit(B,hall,32.65)
 B.shell(hall,0,33,'copperpanel',roof=False)
 B.shell(hall.buffer(.08),0,2.4,'wa-stone',roof=False)
 # Long west/south elevation: warm horizontal metal panels, narrow dark joints.
 for a,b in [((-603,1100),(-603,1209)),((-603,1209),(-428,1209))]:
  F,L,nx,nz=facade_frame(B,a,b,hall,0)
  for yy in np.arange(2.9,32,1.05):
   for i,x in enumerate(np.arange(0,L,14)):
    F.box(['copper2','copper3','copperpanel'][(i+int(yy))%3],(x+min(14,L-x)/2,yy,-.10),(min(14,L-x)-.10,.79,.12))
  F.box('aria-trim',(L/2,32.8,-.2),(L,.5,.65))
 # Undercroft columns keep existing service access unblocked.
 for x in [-600,-550,-500,-431]:
  for z in [1104,1142,1205]:B.box('skg-slab',(x,DECK/2,z),(.85,DECK,.85),True)
 concourse=box(-603,1083,-428,1100);B.planar('aria-paving',concourse,DECK,True);soffit(B,concourse,DECK-.3)
 for i in range(9):
  x0=-603+i*175/9;x1=-603+(i+1)*175/9;z0=1083+1.4*(i%2);y0=30.5-1.0*(i%2)
  wall=box(x0,DECK,x1,y0)
  if i==8:wall=wall.difference(box(-443,DECK-.1,-437,DECK+3.5))
  for pp in parts(wall):
   for tri in triangles(pp):B.face('wa-glass',[(x,y,z0+1.1*(x-x0)/(x1-x0)) for x,y in list(tri.exterior.coords)[:-1]],True)
  B.upface('wa-metal-light',[(x0,y0,z0),(x1,y0,z0+1.1),(x1,33,1100),(x0,33,1100)],True)
  for t in np.arange(0,1,.125):
   x=x0+(x1-x0)*t;z=z0+1.1*t
   if i==8 and -443<x<-437:continue
   B.box('aria-trim',(x,(DECK+y0)/2,z-.1),(.09,y0-DECK,.22))
  for yy in [18,22,26,30]:B.path('aria-trim',[(x0,yy,z0-.12),(x1,yy,z0+.98)],.05,4)
 # Rooftop mechanical islands, parapets and equipment screened from pool side.
 for x,z,w,h in [(-559,1170,35,13),(-456,1124,18,12),(-468,1188,19,10)]:
  B.box('wa-vent',(x,34.1,z),(w,2.2,h));B.box('aria-trim',(x,35.25,z),(w+.25,.15,h+.25))
 for x in np.arange(-590,-434,18):
  for z in [1140,1200]:B.box('wa-vent',(x,33.7,z),(3.1,1.4,2.2))
 # Curved pool bar pavilion between the long southern pool and eastern Yucca pool.
 B.source='aria-pool-deck';bar=Polygon([(-535,1053),(-521,1048),(-507,1060),(-488,1067),(-492,1080),(-531,1076)]).buffer(1.5).buffer(-1.5)
 B.shell(bar,DECK,DECK+3.4,'wa-glass',roof=False)
 B.planar('wa-roof',bar.buffer(2),DECK+4,True);soffit(B,bar.buffer(2),DECK+3.8)
 # Outdoor cabanas and seats follow the pool perimeters, with clear walking space.
 # Dense planting islands separate pool courts, as in the 2022 aerial.
 beds=deck.buffer(-2).difference(wet.buffer(7)).difference(bar.buffer(4)).difference(box(-607,1018,-597,1035)).difference(box(-449,1074,-432,1101))
 paths=unary_union([LineString([(-602,1032),(-585,1020),(-538,1015),(-495,1010),(-438,1079)]).buffer(2.1),LineString([(-585,1020),(-586,1065),(-544,1079),(-486,1080),(-439,1079)]).buffer(2.1)])
 beds=beds.difference(paths)
 B.planar('aria-mulch',beds,DECK+.07);B.shell(beds,DECK,DECK+.16,'wa-stone',roof=False,solid=False)
 rng=random.Random(2319);shrubs=[]
 for xx in np.arange(-606,-415,2.2):
  for zz in np.arange(975,1083,2.2):
   x=xx+rng.uniform(-.7,.7);z=zz+rng.uniform(-.7,.7)
   if not beds.buffer(-.3).contains(Point(x,z)):continue
   shrubs.append((x,z));B.detail=1
   for j in range(32):
    a=rng.random()*math.tau;r=rng.random()*.95;y=DECK+.2+rng.random()*.55
    cx=x+r*math.cos(a);cz=z+r*math.sin(a);d=.13+rng.random()*.12
    B.face('foliage',[(cx-d,y,cz),(cx-d*.4,y+.04,cz-d*.38),(cx+d*.4,y+.04,cz-d*.38),(cx+d,y,cz),(cx+d*.4,y-.03,cz+d*.38),(cx-d*.4,y-.03,cz+d*.38)])
 B.detail=0
 # Canvas cabanas follow the west and southern court edges.
 cabanas=[(-596,z,math.pi/2) for z in [987,997,1007,1042,1052,1062]]+[ (x,1076,0) for x in [-579,-569,-559,-478,-468,-458]]
 for x,z,a in cabanas:
  F=Frame(B,x,z,a,y=DECK)
  for dx in [-1.8,1.8]:
   for dz in [-1.6,1.6]:F.box('aria-trim',(dx,1.45,dz),(.09,2.9,.09))
  F.box('wa-cushion',(0,.48,.5),(3.2,.28,1.65))
  B.face('wa-cushion',[F.p(-2,2.8,-1.8),F.p(2,2.8,-1.8),F.p(2,3.2,0),F.p(-2,3.2,0)])
  B.face('wa-cushion',[F.p(-2,3.2,0),F.p(2,3.2,0),F.p(2,2.8,1.8),F.p(-2,2.8,1.8)])
  F.box('wa-cushion',(-1.85,1.5,.2),(.04,2.5,3));F.box('wa-cushion',(1.85,1.5,.2),(.04,2.5,3))
 reserved=[bar.buffer(2),beds]

 for j,p in enumerate(pool_shapes()):
  ring=p.buffer(5).exterior
  for i in range(int(ring.length/3.2)):
   q=ring.interpolate(i*3.2);near=p.exterior.interpolate(p.exterior.project(q));a=math.atan2(near.x-q.x,near.y-q.y)
   area=Point(q.x,q.y).buffer(1.5)
   if not deck.buffer(-1.5).covers(area) or any(r.intersects(area) for r in reserved) or wet.buffer(2).intersects(area):continue
   F=Frame(B,q.x,q.y,a,y=DECK);B.detail=1
   F.box('wa-cushion',(0,.42,0),(.75,.12,1.55));B.face('wa-cushion',[F.p(-.375,.48,-.72),F.p(.375,.48,-.72),F.p(.375,1.02,-1.05),F.p(-.375,1.02,-1.05)])
   for s in [-1,1]:F.box('aria-trim',(s*.29,.2,0),(.04,.4,1.3))
 B.detail=0
 points=[(-598,z) for z in range(986,1076,13)]+[(-570,1009),(-533,1016),(-507,1020),(-453,1008),(-445,1057),(-474,1071),(-553,1067),(-582,1068),(-554,990)]
 points += [(x,z) for i,(x,z) in enumerate(shrubs) if i%45==0]
 gardens(B,deck,wet.union(bar.buffer(3)),lambda q:q,DECK,points,crown_clearance=3)
 # Supported western emergency stair: four flights to the exterior sidewalk datum.
 B.detail=0;B.source='aria-pool-egress';z=1022
 B.planar('aria-paving',box(-616,1019.4,-599.8,1022),.24,True)
 for i in range(4):
  yy=.24+i*(DECK-.24)/4;x=-601 if i%2==0 else -604.1
  F=Frame(B,x,z+(0 if i%2==0 else 9),0 if i%2==0 else math.pi,y=0)
  F.stairs(0,0,2.2,(DECK-.24)/4,9,y=yy)
  landing=box(-605.3,z+9 if i%2==0 else z-2,-599.7,z+11 if i%2==0 else z)
  B.planar('aria-paving',landing,yy+(DECK-.24)/4,True);soffit(B,landing,yy+(DECK-.24)/4-.2)
 return dict(key=KEY,name='ARIA west podium, pools and convention wing',center=[-520,14,1040],bounds=[-615,925,-402,1211],building='aria',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
