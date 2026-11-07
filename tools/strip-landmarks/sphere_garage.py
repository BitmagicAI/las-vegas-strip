"""Wynn employee parking beside Sphere, Earth2022 reference. Heights estimated
except mapped garage25m. Exterior and visible open parking decks only.
"""
from common import *
from forum_shops import facade_frame
KEY='sphereGarage';IDS=['way/111339081','way/1001560970']
def exterior(B):
 B.property=KEY+'-exterior';B.source='sphere-garage';B.detail=0
 p=footprint(IDS[0]);h=25;pitch=h/7
 # Central paired ramps have deck openings; landings stay continuous at ends.
 hole=box(863,-521,878,-460);deck=p.difference(hole)
 for level in range(8):
  y=.24+level*pitch;shape=p if level==0 else deck
  B.shell(shape,max(.01,y-.27),y,'skg-slab',roof=False)
  B.planar('skg-deck',shape,y,True)
  if level<7:
   x0=863 if level%2==0 else 870.5;x1=x0+7.5
   za,zb=(-521,-460) if level%2==0 else (-460,-521)
   B.upface('skg-deck',[(x0,y,za),(x1,y,za),(x1,y+pitch,zb),(x0,y+pitch,zb)],True)
   for x in [x0,x1]:B.face('skg-rail',[(x,y,za),(x,y+pitch,zb),(x,y+pitch+.8,zb),(x,y+.8,za)],True)
 for pp in parts(p):
  ps=list(pp.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,0)
   for x in np.linspace(.2,max(.2,L-.2),max(2,round(L/7.5)+1)):
    F.box('skg-rail',(x,h/2+.24,0),(.48,h,.6),True)
   for level in range(8):
    # Ground-floor bays kept open; rail at upper parking edges only.
    if level:F.box('skg-rail',(L/2,.24+level*pitch+.52,-.08),(L,1.04,.2),True)
   # February2025 west reference: warm inset bands and slender guard frames.
   # Visual trim only; retain every existing deck, ramp and rail collider.
   if nx<-.8 and L>5:
    for level in range(1,8):
     y=.24+level*pitch
     F.box('wy-stone',(L/2,y+.5,-.195),(max(.1,L-.6),.58,.035))
     F.box('wy-joint',(L/2,y+1.62,-.21),(L,.055,.055))
     for u in np.arange(.8,L-.2,1.5):
      F.box('wy-joint',(u,y+1.32,-.21),(.035,.6,.055))
 # Warm stair/service panels interrupt the long west edge.
 for z,w in [(-642,14),(-558,14),(-477,14)]:
  core=box(824.4,z-w/2,830,z+w/2).intersection(p)
  B.shell(core,.24,26.8,'wy-stone',roof=False);B.planar('skg-deck',core,26.8,True)
  # Stair panels project in front of the deck rails, as in the west reference.
  B.box('wy-stone',(823.95,13.52,z),(.85,26.56,w),True)
  for y in np.arange(4,24,3.57):B.box('st-grey',(823.48,y,z),(.08,.5,2.8))
 # Markings are shared batched faces, confined to the mapped footprint.
 for z in np.arange(-671,-442,2.7):
  for x in [827,846,881,892]:
   B.planar('skg-line',box(x,z,x+5,z+.08).intersection(p.buffer(-1.0)).difference(hole.buffer(.5)),25.29)
 q=footprint(IDS[1]);B.source='sphere-garage-service'
 B.shell(q,.24,13.5,'st-stone',roof=False);B.planar('st-roof',q,13.5,True)
 for pp in parts(q):
  ps=list(pp.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,q,.06)
   F.box('st-white',(L/2,13.5,0),(L,.5,.35))
   if nx<-.8 and L>20:
    # January2025 shows four tall reflective window banks, not roller doors.
    # Dimensions are visual estimates fitted to the unchanged mapped facade.
    bay=L/4;w=bay-2.0;bottom=.65;top=11.85
    for i in range(4):
     x=bay*(i+.5)
     F.box('wy-bronze',(x,(bottom+top)/2,-.15),(w,top-bottom,.10))
     for side in [-1,1]:
      F.box('wy-trim',(x+side*(w/2+.12),(bottom+top)/2,-.23),(.24,top-bottom+.35,.25))
     for y in [bottom,top]:F.box('wy-trim',(x,y,-.23),(w+.48,.18,.25))
     for y in np.linspace(bottom,top,7)[1:-1]:
      F.box('wy-rim',(x,y,-.22),(w,.065,.065))
     for u in [-w/6,w/6]:
      F.box('wy-rim',(x+u,(bottom+top)/2,-.22),(.055,top-bottom,.065))
   else:
    for x in np.arange(1,L,6):F.box('st-grey',(x,6.5,-.03),(.06,12.5,.06))
 for x in [834,854,874,891]:
  for z in [-422,-401]:B.box('st-grey',(x,13.85,z),(2,.7,2));B.box('st-white',(x,14.25,z),(2.2,.1,2.2))
 return dict(key=KEY,name='Sphere neighboring parking and service building',center=[862,0,-540],bounds=list(p.union(q).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
