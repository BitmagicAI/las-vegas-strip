"""Park MGM garage: Earth2022 tiers, southwest plant and central ramp.
Elevations and ramp endpoint positions are visual estimates, not measured plans.
"""
from common import *
from forum_shops import facade_frame
KEY='parkMgmParking';IDS=['way/133879585']
RAMPS=[(-555,1248,-518,1268)]
def exterior(B):
 B.property=KEY+'-exterior';B.source='park-mgm-parking';B.detail=0
 p=footprint(IDS[0]);mechanical=box(-611.5,1300,-561,1346);holes=unary_union([box(*r) for r in RAMPS]);pitch=3.;top=.24+9*pitch
 for level in range(10):
  y=.24+level*pitch;deck=p if level==0 else p.difference(holes)
  if level==2:deck=deck.difference(box(-424,1240.8,-415,1246))
  B.planar('skg-deck',deck,y,True);B.shell(deck,max(.01,y-.23),y,'skg-slab',roof=False)
  if level>0:
   for pp in parts(deck):
    for tri in triangles(pp):
     pts=[(x,y-.23,z) for x,z in list(tri.exterior.coords)[:-1]]
     if np.cross(np.subtract(pts[1],pts[0]),np.subtract(pts[2],pts[0]))[1]>0:pts.reverse()
     B.face('skg-slab',pts)

 # Continuous ramps in the two observed roof slots. All decks are cut at these slots.
 for x0,z0,x1,z1 in RAMPS:
  for level in range(9):
   y0=.24+level*pitch;y1=y0+pitch
   B.upface('skg-deck',[(x0,y0,z0),(x1,y1,z0),(x1,y1,z1),(x0,y0,z1)],True)
   B.face('skg-slab',[(x0,y0-.23,z0),(x1,y1-.23,z0),(x1,y1-.23,z1),(x0,y0-.23,z1)])
   for z in [z0,z1]:
    B.face('skg-slab',[(x0,y0-.23,z),(x1,y1-.23,z),(x1,y1,z),(x0,y0,z)],True)
    B.face('st-white',[(x0,y0,z),(x1,y1,z),(x1,y1+.92,z),(x0,y0+.92,z)],True)
   B.upface('skg-line',[(x0,y0+.015,(z0+z1)/2-.05),(x1,y1+.015,(z0+z1)/2-.05),(x1,y1+.015,(z0+z1)/2+.05),(x0,y0+.015,(z0+z1)/2+.05)])
 for pp in parts(p):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   for level in range(1,10):
    cut=mechanical.union(box(-418,1240.7,-414,1246.1)) if level==2 else mechanical
    for seg in parts(LineString([a,b]).difference(cut),'LineString'):
     aa,bb=list(seg.coords)[0],list(seg.coords)[-1];G,ll,_,_=facade_frame(B,aa,bb,pp,0);G.box('st-white',(ll/2,.24+level*pitch+.4,-.08),(ll,.8,.24),True)
   for x in np.linspace(.23,max(.23,L-.23),max(2,round(L/8)+1)):
    q=F.p(x,0,0)
    if (q[0]>-419 and 1240.3<q[2]<1246.3) or mechanical.contains(Point(q[0],q[2])):continue
    F.box('st-white',(x,top/2,0),(.5,top,.65),True)
   F.box('st-white',(L/2,top+.91,-.08),(L,.18,.32))
   # Southwest service annex has a deeper fascia and opaque service walls.
   if False:
    F.box('mandalay-stone',(L/2,1.4,0),(L,2.8,.3),True)
 # Interior columns and transverse beams are visible through the open elevations.
 usable=p.buffer(-1).difference(holes.buffer(.6))
 for x in np.arange(-603,-424,8):
  for z in np.arange(1218,1338,17):
   if usable.contains(Point(x,z)):
    B.box('skg-slab',(x,top/2,z),(.48,top,.48),True)
  for level in range(1,10):
   beam=box(x-.18,1210,x+.18,1345).intersection(usable)
   B.shell(beam,.24+level*pitch-.48,.24+level*pitch-.23,'skg-slab',roof=False)
 # Southwest six-fan mechanical court visible from the freeway.
 plant=box(-611.7,1299.8,-561,1346);B.shell(plant,.24,top,'park-stone',roof=False);B.planar('skg-slab',plant,top+.03)
 for x in [-600,-585,-570]:
  for z in [1312,1331]:
   disk=Point(x,z).buffer(5.8,resolution=24);B.shell(disk,top,top+3.1,'st-grey',roof=False);B.planar('darkglass',disk,top+3.1)
   for ang in np.linspace(0,math.tau,16,endpoint=False):
    ax=x+5.3*math.cos(ang);az=z+5.3*math.sin(ang)
    B.upface('skg-slab',[(x,top+3.13,z),(ax,top+3.13,az),(ax+.15,top+3.13,az+.15)])
 cc=list(plant.exterior.coords)
 for a,b in zip(cc,cc[1:]):
  F,L,_,_=facade_frame(B,a,b,plant,0)
  for y in [top+.2,top+5.5]:F.box('st-grey',(L/2,y,0),(L,.18,.2))
  for x in np.arange(.2,L,1):F.box('st-grey',(x,top+2.85,0),(.1,5.5,.15))
 # East elevator/stair core and west freeway stair panel.
 for x,z,w,d in [(-420,1331,5,17),(-607,1270,4,9)]:
  B.box('st-white',(x,top/2,z),(w,top,d),True)
  B.box('st-white',(x,top+1.3,z),(w,2.6,d),True)
  for y in np.arange(2,top,3):B.box('darkglass',(x+w/2+.03,y,z),(.06,.55,d*.55))
 # Preserve bridge543422872, close its existing gap to the garage at matching elevation.
 deck=box(-424,1240.9,-407.7,1245.9)
 B.upface('skg-deck',[(-424,6.24,1240.9),(-407.7,6.035,1240.9),(-407.7,6.035,1245.9),(-424,6.24,1245.9)],True)
 for z in [1240.9,1245.9]:
  B.box('st-white',(-412,6.7,z),(8,.95,.2),True)
 # Entrance fascia remains above clear ground access on the freeway side.
 F=Frame(B,-611.5,1284,math.pi/2,y=0)
 F.box('park-stone',(0,3,0),(22,.65,.25));F.text('PARK MGM',(0,2.83,-.18),.68,'park-green')
 # Stall paint is clipped to the deck; no stripes crossing a ramp opening.
 roof=p.buffer(-1).difference(holes.buffer(.3)).difference(plant.buffer(1))
 for z in np.arange(1214,1340,17):
  for x in np.arange(-607,-420,2.7):
   B.planar('skg-line',box(x,z,x+.08,z+5).intersection(roof),top+.014)
   B.planar('skg-line',box(x,z+5,x+2.7,z+5.08).intersection(roof),top+.014)
 # Slender pole housings only, retaining the game's fixed light pool.
 for x in [-585,-540,-495,-450]:
  for z in [1226,1278,1325]:
   if not roof.contains(Point(x,z)):continue
   B.box('st-grey',(x,top+2.7,z),(.1,5.4,.1))
   B.box('st-grey',(x,top+5.42,z),(.85,.14,.32))
 return dict(key=KEY,name='Park MGM self parking',center=[-510,0,1280],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
