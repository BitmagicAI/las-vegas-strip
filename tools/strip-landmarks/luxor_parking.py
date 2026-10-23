"""Luxor west garage and raised pedestrian approach, Earth2022 and MGM map.
4.24m deck and canopy8m are estimates. Pyramid indoor endpoint remains separate.
"""
from common import *
from forum_shops import facade_frame
KEY='luxorParking';IDS=['way/29710490','way/118344866','way/118344868','way/118344871']
def soffit(B,p,y):
 for pp in parts(p):
  for t in triangles(pp):
   pts=[(x,y,z) for x,z in list(t.exterior.coords)[:-1]]
   if np.cross(np.subtract(pts[1],pts[0]),np.subtract(pts[2],pts[0]))[1]>0:pts.reverse()
   B.face('skg-slab',pts)
def exterior(B):
 B.property=KEY+'-exterior';B.source='luxor-parking';B.detail=0
 p=footprint(IDS[0]);top=4.24
 for y in [.24,top]:
  B.planar('skg-deck',p,y,True);B.shell(p,max(.01,y-.28),y,'skg-slab',roof=False)
 soffit(B,p,top-.28)
 openings=unary_union([box(-558,2318,-538,2323),box(-467,2283,-462,2291)])
 for pp in parts(p):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   for x in np.linspace(.25,max(.25,L-.25),max(2,round(L/7.5)+1)):
    pos=F.p(x,0,0)
    if openings.contains(Point(pos[0],pos[2])):continue
    F.box('st-white',(x,top/2,0),(.46,top,.52),True)
   for seg in parts(LineString([a,b]).difference(openings),'LineString'):
    aa,bb=list(seg.coords)[0],list(seg.coords)[-1];G,ll,_,_=facade_frame(B,aa,bb,pp,0)
    for y in [top+.2,top+.9]:G.box('st-white',(ll/2,y,0),(ll,.15,.22),True)
    for x in np.arange(.2,ll,2.3):G.box('st-white',(x,top+.53,0),(.12,1.04,.16),True)
 # Existing mapped central notch carries the long shallow vehicle ramp.
 x0,x1=-554.8,-541.2;z0,z1=2320.6,2395.2
 B.upface('skg-deck',[(x0,top,z0),(x1,top,z0),(x1,.24,z1),(x0,.24,z1)],True)
 for x in [x0,x1]:B.face('st-white',[(x,.24,z1),(x,top,z0),(x,top+.7,z0),(x,.94,z1)],True)
 for z in np.arange(z0+2,z1-2,5):
  def yy(q):return .24+(z1-q)/(z1-z0)*4
  B.upface('skg-line',[(-548.04,yy(z)+.015,z),(-547.96,yy(z)+.015,z),(-547.96,yy(z+2)+.015,z+2),(-548.04,yy(z+2)+.015,z+2)])
 usable=p.buffer(-1)
 for x in np.arange(-621,-470,8):
  for z in np.arange(2201,2390,17):
   if usable.contains(Point(x,z)):B.box('skg-slab',(x,top/2,z),(.45,top,.45),True)
 for x in np.arange(-624,-470,17):
  for z in np.arange(2198,2390,2.7):
   B.planar('skg-line',box(x,z,x+5,z+.075).intersection(usable),top+.014)
 for x in [-619,-581,-530,-479]:
  for z in [2220,2280,2340,2385]:
   if not usable.contains(Point(x,z)):continue
   B.box('st-grey',(x,top+2.4,z),(.09,4.8,.09));B.box('st-grey',(x,top+4.85,z),(.65,.14,.35))
 # Raised public approach: actual axis from the garage through the pool pavilions.
 B.source='luxor-pool-approach';center=2287
 walk=box(-466,center-2.8,-340.7,center+2.8)
 landing=footprint(IDS[1]);entry=footprint(IDS[2]);island=footprint(IDS[3]);deck=unary_union([walk,landing,island,entry])
 B.planar('tile',deck,top,True);B.shell(deck,top-.3,top,'luxor-stone',roof=False);soffit(B,deck,top-.3)
 # Pool pavilion lower rooms support an open upper passage.
 B.shell(island,.24,top-.3,'luxor-stone',roof=False)
 for pp in parts(deck):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   mid=LineString([a,b]).interpolate(.5,normalized=True)
   if mid.x<-464.4 or mid.x>-341:continue
   F,L,_,_=facade_frame(B,a,b,pp,0)
   for y in [top+.15,top+1.02]:F.box('luxor-stone',(L/2,y,0),(L,.16,.24),True)
   for x in np.arange(.2,L,.3):F.box('st-grey',(x,top+.59,0),(.035,.85,.035))
 # One continuous canopy surface; separate bay roofs left visible gaps.
 canopy=box(-466,center-3,-355.5,center+3).difference(island.buffer(.65,join_style=2))
 holes=[]
 for x in np.arange(-458,-347,9):
  if -420<x<-388 or x>-374:continue
  for z in [center-2.5,center+2.5]:
   B.box('luxor-stone',(x,top+1.75,z),(.38,3.5,.38),True)
   B.box('luxor-band',(x,top+3.25,z),(.7,.28,.7))
  hole=box(x-1.7,center-1.7,x+1.7,center+1.7);holes.append(hole)
  cc=list(hole.exterior.coords)
  for a,b in zip(cc,cc[1:]):B.face('luxor-glass',[(a[0],top+3.6,a[1]),(b[0],top+3.6,b[1]),(x,top+4.4,center)])
 canopy=canopy.difference(unary_union(holes))
 B.planar('luxor-stone',canopy,top+3.6);soffit(B,canopy,top+3.4)
 B.shell(canopy,top+3.4,top+3.6,'luxor-stone',roof=False,solid=False)
 # Central broad cornice, dark roof light and Egyptian flared shoulders.
 roof=island.buffer(.65,join_style=2);light=box(-408,2283,-401,2290)
 B.planar('luxor-stone',roof.difference(light),8.1);soffit(B,roof.difference(light),7.8)
 B.shell(roof,7.8,8.1,'luxor-stone',roof=False,solid=False)
 cc=list(light.exterior.coords)
 for a,b in zip(cc,cc[1:]):B.face('luxor-glass',[(a[0],8.1,a[1]),(b[0],8.1,b[1]),(-404.5,9.3,2286.5)])
 for x in [-412,-397]:
  for z in [2280,2294]:B.box('luxor-stone',(x,6,z),(.75,3.52,.75),True)
 # Entry portal facing the pyramid; indoor continuation is owned by Luxor.
 for z in [2279,2294]:B.box('luxor-stone',(-348,6,z),(10,3.52,.7),True)
 B.box('luxor-stone',(-348,8.1,2286.5),(15,.4,17))
 return dict(key=KEY,name='Luxor west parking and pool approach',center=[-520,0,2290],bounds=list(unary_union([p,deck]).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
