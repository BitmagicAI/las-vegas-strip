"""Flamingo thin L-shaped tower wings from mapped footprints, Earth2022 elevations.
Existing casino and lotus marquee retained. GO Pool changed2025; garden fidelity
is not represented by this tower-only pass.
"""
from common import *
from forum_shops import facade_frame
KEY='flamingoExterior';IDS=['way/115766957','way/115766962','way/115766969']
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;B.source='tower/flamingo'
 shapes=unary_union([footprint(i) for i in IDS])
 for poly in parts(shapes):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<.1:continue
   F,L,_,_=facade_frame(B,a,b,poly,.03);h=79.5;lo=12.5
   F.box('fl-white',(L/2,(h+lo)/2,0),(L,h-lo,.16),True)
   if L>26:
    # White end/core piers, broad dark rose glazing, individual room mullions.
    F.box('fl-glass',(L/2,(h+lo)/2,-.11),(L-7,h-lo-4,.04))
    for y in np.arange(lo+1.7,h-5.5,2.7):
     F.box('fl-spandrel',(L/2,y,-.17),(L-7,.68,.06))
     F.box('fl-white',(L/2,y-.50,-.25),(L-7,.16,.25))
     for x in np.arange(4.2,L-4,3.15):
      F.box('fl-curtain' if int(x/3.15)%4==0 else 'fl-glass',(x,y+1.1,-.19),(2.75,1.7,.04))
    for x in np.arange(3.5,L-3,3.15):F.box('fl-frame',(x,(h+lo-2)/2,-.25),(.09,h-lo-4,.15))
    for x in np.arange(3.5,L-3,12.6):F.box('fl-white',(x,(h+lo-2)/2,-.3),(.35,h-lo-4,.45))
    F.box('fl-white',(L/2,h-3,-.28),(L,1.3,.5))
    F.text('Flamingo',(L/2,h-2.5,-.59),2.1,'fl-letter')
   else:
    # Service ends are intentionally mostly white, with a narrow stair glazing slot.
    if L>10:F.box('fl-glass',(L*.57,45,-.16),(1.1,51,.05))
   F.box('fl-white',(L/2,h+.2,0),(L,.4,.6))
   # Open rooftop mechanical screen: not another solid floor or giant box.
   F.box('fl-screen',(L/2,81.4,1.0),(L,3.0,.12))
   for y in [80.2,81.2,82.2]:F.box('fl-frame',(L/2,y,.91),(L,.12,.18))
   for x in np.arange(.3,L,4.5):F.box('fl-white',(x,81.4,.84),(.15,3,.28))
  B.planar('fl-roof',poly,79.52,True)
  for x in np.arange(poly.bounds[0]+4,poly.bounds[2]-3,12):
   for z in np.arange(poly.bounds[1]+4,poly.bounds[3]-3,12):
    if poly.contains(box(x-1.5,z-1.5,x+1.5,z+1.5)):B.box('fl-service',(x,80.3,z),(3,1.5,3));B.box('fl-shadow',(x,81.07,z),(2.6,.04,2.6))
 from flamingo_podium_detail import exterior as podium
 podium(B)
 return dict(key=KEY,name='Flamingo mapped hotel wings',center=[160,0,-50],bounds=[24,-158,272,72],building='flamingo',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=['flamingo'],views={})
