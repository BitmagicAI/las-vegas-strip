"""Mandalay parking: mapped plan, Earth2022 open tiers and two roof ramps.
Elevations and ramp endpoint positions are visual estimates, not measured plans.
"""
from common import *
from forum_shops import facade_frame
KEY='mandalayParking';IDS=['way/111394032']
RAMPS=[(-562,2620,-534,2639),(-451,2693,-385,2712)]
def exterior(B):
 B.property=KEY+'-exterior';B.source='mandalay-parking';B.detail=0
 p=footprint(IDS[0]);holes=unary_union([box(*r) for r in RAMPS]);pitch=3.;top=.24+5*pitch
 for level in range(6):
  y=.24+level*pitch;deck=p if level==0 else p.difference(holes)
  B.planar('skg-deck',deck,y,True);B.shell(deck,max(.01,y-.23),y,'skg-slab',roof=False)
  if level>0:
   for pp in parts(deck):
    for tri in triangles(pp):
     pts=[(x,y-.23,z) for x,z in list(tri.exterior.coords)[:-1]]
     if np.cross(np.subtract(pts[1],pts[0]),np.subtract(pts[2],pts[0]))[1]>0:pts.reverse()
     B.face('skg-slab',pts)

 # Continuous ramps in the two observed roof slots. All decks are cut at these slots.
 for x0,z0,x1,z1 in RAMPS:
  for level in range(5):
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
   for level in range(1,6):F.box('st-white',(L/2,.24+level*pitch+.4,-.08),(L,.8,.24),True)
   for x in np.linspace(.23,max(.23,L-.23),max(2,round(L/8)+1)):
    F.box('st-white',(x,top/2,0),(.5,top,.65),True)
   F.box('st-white',(L/2,top+.91,-.08),(L,.18,.32))
   # Southwest service annex has a deeper fascia and opaque service walls.
   if (a[1]+b[1])/2>2740:
    F.box('mandalay-stone',(L/2,1.4,0),(L,2.8,.3),True)
 # Interior columns and transverse beams are visible through the open elevations.
 usable=p.buffer(-1).difference(holes.buffer(.6))
 for x in np.arange(-613,-376,8):
  for z in np.arange(2612,2762,17):
   if usable.contains(Point(x,z)):
    B.box('skg-slab',(x,top/2,z),(.48,top,.48),True)
  for level in range(1,6):
   beam=box(x-.18,2603,x+.18,2768).intersection(usable)
   B.shell(beam,.24+level*pitch-.48,.24+level*pitch-.23,'skg-slab',roof=False)
 # Tall central billboard/lift panel on the freeway elevation.
 F=Frame(B,-622.35,2666,math.pi/2,y=0)
 F.box('st-white',(0,7.8,0),(22,15.6,.5),True)
 for x in [-5.2,5.2]:F.box('darkglass',(x,10,-.28),(8.8,5.3,.08))
 F.text('MANDALAY BAY',(0,4.5,-.31),.85,'mandalay-bronze')
 # Stair headhouses on the roof, positioned at the observed perimeter breaks.
 for x,z in [(-618,2726),(-530,2726),(-450,2726),(-618,2606),(-534,2606),(-376,2646)]:
  B.box('mandalay-stone',(x,top+1.1,z),(3.6,2.2,3.6),True)
  B.box('st-white',(x,top+2.25,z),(4,.16,4))
  B.box('st-grey',(x,top+1.05,z-1.83),(1,2,.06))
 # Stall paint is clipped to the deck; no stripes crossing a ramp opening.
 roof=p.buffer(-1).difference(holes.buffer(.3))
 for z in np.arange(2607,2760,17):
  for x in np.arange(-613,-379,2.7):
   B.planar('skg-line',box(x,z,x+.08,z+5).intersection(roof),top+.014)
   B.planar('skg-line',box(x,z+5,x+2.7,z+5.08).intersection(roof),top+.014)
 # Slender pole housings only, retaining the game's fixed light pool.
 for x in [-598,-546,-494,-442,-390]:
  for z in [2646,2679,2719]:
   if not roof.contains(Point(x,z)):continue
   B.box('st-grey',(x,top+2.7,z),(.1,5.4,.1))
   B.box('st-grey',(x,top+5.42,z),(.85,.14,.32))
 return dict(key=KEY,name='Mandalay Bay self parking',center=[-500,0,2680],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
