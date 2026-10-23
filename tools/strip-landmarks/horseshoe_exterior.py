"""Mapped Horseshoe and Versailles wings; Earth2022 and BWA2024 remodel reference.
Roof, mullion and frontage dimensions are photographic estimates, not survey claims.
"""
from common import *
from forum_shops import facade_frame
from horseshoe_frontage import frontage,RETAIL
KEY='horseshoeExterior';IDS=['way/27897921','way/27897922','way/116867081']
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 for k,ident in enumerate(IDS[:2]):
  poly=footprint(ident);lo=12.5 if k==0 else 15;top=75 if k==0 else 80
  B.source='tower/horseshoe' if k==0 else 'tower/horseshoe-east'
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,_,_=facade_frame(B,a,b,poly,.03)
   if L<.1:continue
   F.box('hs-stone',(L/2,(lo+top)/2,0),(L,top-lo,.16),True)
   if L>30:
    F.box('hs-glass',(L/2,(lo+top-2)/2,-.13),(L-4,top-lo-2,.04))
    for yy in np.arange(lo+2,top-2,2.65):
     F.box('hs-spandrel',(L/2,yy,-.18),(L-4,.7,.04))
     F.box('hs-frame',(L/2,yy-.4,-.23),(L-4,.13,.14))
    for xx in np.arange(2,L-1,3.2):F.box('hs-white',(xx,(lo+top-2)/2,-.3),(.22,top-lo-2,.35))
    for xx in np.arange(2,L-1,12.8):F.box('hs-stone',(xx,(lo+top)/2,-.42),(.55,top-lo,.6))
    for yy in [lo+.4,top-1.1,top]:F.box('hs-white',(L/2,yy,-.35),(L,.45,.6))
   elif 7<L<28:
    # Broad stone end cores with recessed vertical window strip.
    F.box('hs-glass',(L*.5,(lo+top-3)/2,-.16),(1.4,top-lo-3,.05))
    for yy in np.arange(lo+1,top-1,3):F.box('hs-joint',(L/2,yy,-.12),(L,.05,.06))
    if k==1 and L>15:
     for j,c in enumerate('HORSESHOE'):F.text(c,(L*.72,top-5-j*2,-.3),1.3,'hs-letter')
   F.box('hs-stone',(L/2,top+.1,0),(L,.2,.55))
  if k==0:
   # Join the mansard at shared offset vertices, with upward-facing normals.
   inner=poly.buffer(-2,join_style=2).exterior
   for a,b in zip(ps,ps[1:]):
    ia=inner.interpolate(inner.project(Point(a)));ib=inner.interpolate(inner.project(Point(b)))
    B.upface('hs-blue',[(a[0],75,a[1]),(b[0],75,b[1]),(ib.x,80,ib.y),(ia.x,80,ia.y)],True)
    L=math.dist(a,b)
    for t in np.linspace(0,1,max(2,round(L/2.8))):B.tube('hs-roof-seam',(a[0]+(b[0]-a[0])*t,75.015,a[1]+(b[1]-a[1])*t),(ia.x+(ib.x-ia.x)*t,80.015,ia.y+(ib.y-ia.y)*t),.025,4)
  B.planar('hs-roof',poly.buffer(-2,join_style=2) if k==0 else poly,80.02,True)
  for x in np.arange(poly.bounds[0]+5,poly.bounds[2]-4,15):
   for z in np.arange(poly.bounds[1]+5,poly.bounds[3]-4,12):
    if poly.contains(box(x-1.6,z-1.6,x+1.6,z+1.6)):
     B.box('hs-service',(x,80.65,z),(3,1.2,3));B.box('hs-shadow',(x,81.27,z),(2.7,.03,2.7))
 # Parent casino footprint is15m, not another81m hotel. Retain existing public
 # interior area to the west; detail mapped outer walls and independent roof.
 B.source='horseshoe/casino';poly=footprint(IDS[2]);ps=list(poly.exterior.coords)
 for a,b in zip(ps,ps[1:]):
  F,L,_,_=facade_frame(B,a,b,poly,.08)
  if L<.1:continue
  # Do not cover shared tower-facing edges with a second skin.
  mid=Point((a[0]+b[0])/2,(a[1]+b[1])/2)
  if footprint(IDS[1]).buffer(.25).contains(mid):continue
  F.box('hs-stone',(L/2,7.5,0),(L,15,.16),True)
  for y in [1.2,5.8,12.4,14.6]:F.box('hs-white',(L/2,y,-.18),(L,.25,.25))
  for x in np.arange(2,L-2,5.2):
   F.box('hs-shadow',(x,4.2,-.13),(3.4,5.8,.04));F.box('hs-glass',(x,4.3,-.18),(3.1,5.3,.04));F.box('hs-frame',(x,4.3,-.24),(.07,5.3,.08))
  for x in np.arange(.3,L,10.4):F.box('hs-white',(x,7.5,-.35),(.4,15,.5))
 roof=poly.difference(unary_union([footprint(i) for i in IDS[:2]]));B.planar('hs-roof',roof,15.02,True)
 for p in parts(roof):
  for x in np.arange(p.bounds[0]+5,p.bounds[2]-4,24):
   for z in np.arange(p.bounds[1]+5,p.bounds[3]-4,23):
    if p.contains(box(x-2,z-2,x+2,z+2)):B.box('hs-service',(x,15.7,z),(4,1.3,3));B.box('hs-shadow',(x,16.37,z),(3.6,.04,2.5))
 frontage(B)
 versailles_south_frontage(B)
 return dict(key=KEY,name='Horseshoe and Versailles exterior',center=[300,0,270],bounds=[35,171,551,378],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=['horseshoe','horseshoe-east'],views={})


def versailles_south_frontage(B):
 # April2025 Street View BO9-qojhxfSBa1YIItci5Q: two rectangular tiers,
 # cream bands and quiet frames. Bay widths/heights are photographic estimates.
 # Existing public shell and collision remain behind this decorative replacement.
 B.source='podium/versailles-south-frontage';B.detail=0
 x0,x1=85.27,206.58;z=302.35
 B.box('hs-stone',((x0+x1)/2,6.27,z),(x1-x0,12.24,.18))
 for y,h,depth in [(.5,.55,.28),(5.55,.48,.32),(6.1,.12,.22),(10.8,.55,.38),(11.6,.16,.3),(12.25,.3,.4)]:
  B.box('hs-white',((x0+x1)/2,y,z+.15),(x1-x0,h,depth))
 bays=27;pitch=(x1-x0)/bays
 for i in range(bays):
  x=x0+(i+.5)*pitch
  for y,h,w in [(2.8,3.5,pitch-1.1),(8.25,2.9,pitch-.95)]:
   B.box('hs-frame',(x,y,z+.15),(w+.16,h+.16,.12))
   B.box('hs-glass',(x,y,z+.23),(w,h,.025))
   for xx in [x-w/2,x+w/2]:B.box('hs-stone',(xx,y,z+.29),(.12,h+.22,.16))
   B.box('hs-white',(x,y-h/2-.09,z+.3),(w+.25,.16,.25))
   B.box('hs-frame',(x,y,z+.26),(.045,h,.04))
