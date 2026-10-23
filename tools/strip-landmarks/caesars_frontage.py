"""Caesars small street frontage, mapped plans and photograph-derived sections.
Hell's Kitchen: CSD Architecture entrance and David Lambert 2021 east facade.
Earth 2022-11-09 establishes north/south orientation. Heights are estimates.
"""
from common import *
from forum_shops import facade_frame
IDS=['way/34000287']
def exterior(B):
 B.source='caesars-hells-kitchen';B.detail=0
 p=footprint(IDS[0]);base=1.05;roof=7.4
 # Main entrance is on the south end, facing the pedestrian plaza.
 door=dict(p=[-28,base,52.4],width=4.4,height=4.8)
 B.shell(p,base,roof,'cp-white',openings=[door],roof=False)
 B.planar('cp-flat-roof',p,roof,True);B.planar('stone',p,base,True)
 B.shell(p,0,base,'cp-stone',roof=False)
 for poly in parts(p):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.035)
   F.box('cp-white',(L/2,roof+.2,-.12),(L,.4,.3))
   F.box('cp-white',(L/2,roof-.55,-.25),(L,.24,.55))
   if L<8:continue
   if nx>.8 or nx<-.8:
    count=max(2,round(L/4.6));w=L/count
    for k in range(count):
     x=(k+.5)*w
     F.box('cp-glass',(x,3.85,-.09),(w-.65,4.6,.10))
     for yy in [1.65,3.9,6.1]:F.box('blackiron',(x,yy,-.16),(w-.65,.065,.08))
     F.box('blackiron',(x,3.85,-.16),(.065,4.6,.08))
    for k in range(count+1):
     x=k*w
     F.box('cp-white',(x,3.75,-.33),(.65,5.4,.6))
     for dx in [-.2,0,.2]:F.box('cp-shadow',(x+dx,3.8,-.641),(.025,4.8,.008))
     if 0<k<count:
      F.box('blackiron',(x,3.25,-.72),(.29,.75,.16));F.box('warm',(x,3.25,-.81),(.17,.55,.015))
    # Balcony strip and simple black handrail, no geometry under adjacent road.
    if nx>.8:
     F.box('stone',(L/2,base-.09,-1.03),(L,.18,1.7),True)
     F.rail((.15,-1.75),(L-.15,-1.75),base+1.05)
     F.text("HELL'S KITCHEN",(L/2,6.65,-.57),.55,'red')
     for x in np.arange(.4,L,.65):F.box('blackiron',(x,base+.55,-1.75),(.025,1.0,.025))
   elif nz>.8:
    # Red vertical reveals, separate wall piers and glazed entrance surround.
    for x in np.arange(.7,L,3.6):
     wp=F.p(x,0,0)
     if abs(wp[0]+28)<2.4:continue
     F.box('cp-white',(x,3.8,-.24),(.42,5.6,.46))
     F.box('red',(x-.26,3.8,-.07),(.065,5.6,.055))
    x=L/2
    # Locate the sign over the actual door in world coordinates rather than edge midpoint.
    x=((door['p'][0]-F.x)*F.co-(door['p'][2]-F.z)*F.si)
    if 0<x<L:
     F.box('blackiron',(x,5.2,-.26),(4.8,2.5,.4))
     F.text('GORDON RAMSAY',(x,5.7,-.48),.3,'cp-white')
     F.text("HELL'S KITCHEN",(x,4.95,-.49),.46,'red')
     for side in [-1,1]:F.box('blackiron',(x+side*2.15,3,-.17),(.12,3.9,.25))
 # The signature monumental letters and pitchfork sit beside the entrance.
 S=Frame(B,-19,54.1,math.pi,y=0)
 S.box('cp-stone',(0,.95,0),(5.6,1.9,1.8),True)
 S.text('HK',(0,2.0,-.94),3.8,'bronze')
 S.tube('bronze',(0,1.9,-1.0),(0,6.7,-1.0),.075,12)
 for side in [-1,1]:
  S.path('bronze',[(0,4.9,-1),(side*.7,5.2,-1),(side*.8,5.7,-1),(side*.62,6.7,-1)],.065,10)
 # Raised forecourt with physically walkable stairs; interior only vestibule.
 B.box('stone',(-28,base/2,54.1),(12,base,3.6),True)
 F=Frame(B,-28,59.1,math.pi,y=0);F.stairs(0,0,10,base,3.2)
 B.box('cp-white',(-28,2.9,48),(8,3.8,.2),True)
 for x in [-32,-24]:B.box('cp-white',(x,2.9,50),( .2,3.8,4),True)
 # Rooftop equipment fits the observed central service lane.
 B.detail=1
 for z in [16,23,31,38,45]:
  B.box('cp-service',(-26,roof+.55,z),(3.3,1.1,2.3));B.box('cp-shadow',(-26,roof+1.11,z),(3,.035,2))
 B.detail=0
 return dict(id=IDS[0],baseM=base,roofM=roof,door=door,dimensions='Roof and raised-floor heights estimated from photographs; footprint mapped.',remaining='Refine simplified HK sign and flames; detailed garden planting, dining interior and accessible ramp still missing.')
