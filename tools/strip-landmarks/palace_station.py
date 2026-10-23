"""Palace Station mapped tower and low wings, referenced to Earth November 2022.
Heights except mapped65m tower are photographic estimates; no interior replacement.
"""
from common import *
from forum_shops import facade_frame
KEY='palaceStation';IDS=['way/543645430','way/276425915','way/146612127','relation/19559597']
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 for ident in IDS:
  p=footprint(ident);tower=ident==IDS[0];garage=ident in IDS[2:];h=60 if tower else 21 if ident==IDS[2] else 9 if garage else 11
  B.source='palace-station/'+('tower' if tower else 'garage' if garage else 'casino')
  ps=list(p.simplify(.35,preserve_topology=True).exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,_,_=facade_frame(B,a,b,p,.08)
   if L<.3:continue
   if garage:
    for yy in np.arange(0,h,3):F.box('ps-white',(L/2,yy+.65,0),(L,1.15,.3),True)
    for xx in np.arange(.25,L,6):F.box('ps-stone',(xx,h/2,-.13),(.6,h,.6),True)
    if L>55:F.box('ps-stone',(L*.5,h/2,-.2),(7,h,.7),True)
   elif tower:
    F.box('ps-stone',(L/2,h/2,0),(L,h,.22),True)
    if L>35:
     for x in np.arange(2,L-1.5,3.7):
      for y in np.arange(4.2,58,2.65):
       F.box('ps-shadow',(x,y,-.15),(2.85,2.25,.06));F.box('ps-glass',(x,y,-.2),(2.55,2.05,.04));F.box('ps-frame',(x,y,-.26),(.055,2.05,.08))
       F.box('ps-frame',(x,y-.45,-.26),(2.55,.05,.08))
      F.box('ps-white',(x-1.7,31,-.30),(.28,58,.35))
     for yy in [2,57.7,59.5]:F.box('ps-white',(L/2,yy,-.32),(L,.45,.7))
     # Three raised clock/attic bays and steep grey caps, as in both aerials.
     for x in [3.7,L/2,L-3.7]:
      F.box('ps-white',(x,61.2,.5),(6.2,4.4,4))
      F.arch(x,-1.57,2.7,63.4,'ps-stone',.22,base=59.6)
      F.box('ps-glass',(x,61,-1.6),(2,2.2,.04))
      pts=[F.p(x-3.4,63.4,-1.6),F.p(x+3.4,63.4,-1.6),F.p(x+2,66,1),F.p(x-2,66,1)]
      B.upface('ps-roof',pts)
      B.upface('ps-roof',[F.p(x-3.4,63.4,2.7),F.p(x+3.4,63.4,2.7),F.p(x+2,66,1),F.p(x-2,66,1)])
      for side in [-1,1]:B.face('ps-roof',[F.p(x+side*3.4,63.4,-1.6),F.p(x+side*3.4,63.4,2.7),F.p(x+side*2,66,1)])
     F.text('PALACE STATION',(L/2,59,-.78),1.8,'ps-red')
    else:
     for yy in np.arange(3,59,2.65):F.box('ps-joint',(L/2,yy,-.15),(L,.055,.06))
     for yy in np.arange(5,57,2.65):F.box('ps-glass',(L/2,yy,-.16),(1.25,1.85,.04))
   else:
    F.box('ps-white',(L/2,h/2,0),(L,h,.22),True)
    F.box('ps-stone',(L/2,1,-.16),(L,2,.3))
    for yy in [2.4,8.4,10.5]:F.box('ps-trim',(L/2,yy,-.2),(L,.25,.4))
    if L>20:
     for x in np.arange(3,L-2,4.3):
      F.box('ps-glass',(x,4.3,-.16),(3.2,3.7,.05));F.box('ps-frame',(x,4.3,-.22),(.08,3.7,.09))
     for x in np.arange(.5,L,12):F.box('ps-stone',(x,5,-.30),(.8,10,.65))
  B.planar('ps-roof',p,h+.03,True)
  if garage:
   for y in np.arange(3,h,3):B.planar('ps-deck',p,y,True)
  else:
   for x in np.arange(p.bounds[0]+5,p.bounds[2]-3,17):
    for z in np.arange(p.bounds[1]+5,p.bounds[3]-3,16):
     if p.contains(box(x-2,z-2,x+2,z+2)):B.box('ps-service',(x,h+.65,z),(3,1.2,3));B.box('ps-shadow',(x,h+1.27,z),(2.7,.04,2.7))
 return dict(key=KEY,name='Palace Station exterior',center=[-200,0,-2960],bounds=[-400,-3067,-24,-2827],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
