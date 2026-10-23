"""Northern ARIA/Vdara garage. Earth2022 footprint/screens/roof openings.
Nine mapped levels;3.4m pitch and ramp direction are explicit estimates.
"""
from common import *
from forum_shops import facade_frame
from luxor_parking import soffit
KEY='ariaParking';IDS=['way/52175579'];PITCH=3.4;RAMPS=[(-570,709,-552,755),(-570,772,-552,831)]
def exterior(B):
 B.property=KEY+'-exterior';B.source='aria-north-garage';B.detail=0;p=footprint(IDS[0]);holes=unary_union([box(*r) for r in RAMPS]);top=.24+8*PITCH
 for level in range(9):
  y=.24+level*PITCH;floor=p if level==0 else p.difference(holes)
  B.planar('skg-deck',floor,y,True);B.shell(floor,max(.01,y-.24),y,'skg-slab',roof=False)
  if level:soffit(B,floor,y-.24)
 for x0,z0,x1,z1 in RAMPS:
  # Guard the rooftop openings while leaving the upper ramp mouth open.
  for x in [x0,x1]:B.box('skg-rail',(x,top+.48,(z0+z1)/2),(.2,.96,z1-z0),True)
  B.box('skg-rail',((x0+x1)/2,top+.48,z0),(x1-x0,.96,.2),True)
  for level in range(8):
   lo=.24+level*PITCH;hi=lo+PITCH
   B.upface('skg-deck',[(x0,lo,z0),(x1,lo,z0),(x1,hi,z1),(x0,hi,z1)],True)
   B.face('skg-slab',[(x0,lo-.24,z0),(x1,lo-.24,z0),(x1,hi-.24,z1),(x0,hi-.24,z1)])
   for x in [x0,x1]:B.face('skg-rail',[(x,lo,z0),(x,hi,z1),(x,hi+.9,z1),(x,lo+.9,z0)],True)
   B.upface('skg-line',[((x0+x1)/2-.05,lo+.02,z0),((x0+x1)/2+.05,lo+.02,z0),((x0+x1)/2+.05,hi+.02,z1),((x0+x1)/2-.05,hi+.02,z1)])
 for pp in parts(p):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   if L<.1:continue
   for level in range(1,9):F.box('skg-rail',(L/2,.24+level*PITCH+.45,-.06),(L,.9,.22),True)
   for x in np.arange(.25,L,.0+7.8):F.box('skg-slab',(x,top/2,0),(.48,top,.6),True)
   F.box('skg-rail',(L/2,top+1.05,0),(L,.18,.36))
 # Interior concrete columns and beam soffits, physically open through the bays.
 usable=p.buffer(-1).difference(holes.buffer(1))
 for x in np.arange(-603,-520,15):
  for z in np.arange(648,845,8):
   if usable.contains(Point(x,z)):B.box('skg-slab',(x,top/2,z),(.55,top,.55),True)
  for level in range(1,9):B.shell(box(x-.18,640,x+.18,848).intersection(usable),.24+level*PITCH-.5,.24+level*PITCH-.24,'skg-slab',roof=False)
 # The west elevation alternates tall opaque beige piers with open concrete bays.
 for z0,z1 in [(640,651),(664,683),(733,747),(790,809)]:
  B.box('wa-stone',(-612.25,top/2,(z0+z1)/2),(.65,top,z1-z0),True)
  for y in [10.4,20.6]:B.box('aria-trim',(-612.61,y,(z0+z1)/2),(.06,.12,z1-z0))
 # Recessed vertical bronze fins across lower west bays, not a solid blackout face.
 for z in np.arange(653,845,1.15):
  if any(a<z<b for a,b in [(664,683),(733,747),(790,809)]):continue
  B.box('aria-trim',(-612.2,6.6,z),(.12,12.5,.07))
 # Northwest/northeast stair and lift cores with slotted window panels.
 for x,z,w,d in [(-605,646,7,9),(-525,660,6,18)]:
  B.box('wa-stone',(x,(top+2.1)/2,z),(w,top+2.1,d),True)
  for y in np.arange(2,top,3.4):
   B.box('wa-glass',(x-w/2-.04,y,z),(.07,2.2,.85))
  B.box('wa-roof',(x,top+2.16,z),(w+.3,.14,d+.3))
 # Roof parking:double stalls, aisles around the two ramp cutouts.
 roof=p.buffer(-1.5).difference(holes.buffer(.4))
 for x in [-607,-588,-569,-550,-531]:
  for z in np.arange(650,840,2.7):
   B.planar('skg-line',box(x,z,x+5.3,z+.08).intersection(roof),top+.015)
  B.planar('skg-line',box(x+5.2,650,x+5.3,840).intersection(roof),top+.015)
 for x in [-597,-580,-541,-525]:
  for z in [668,704,763,808,839]:
   if roof.contains(Point(x,z)):
    B.box('aria-trim',(x,top+2.5,z),(.09,5,.09));B.box('aria-trim',(x,top+5.05,z),(.85,.14,.28))
 return dict(key=KEY,name='ARIA and Vdara northern garage',center=[-565,0,744],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
