"""Mapped Bellagio self parking: independently fitted circulation levels."""
from common import *
from road_splines import smooth_grade
from ramp_barriers import barrier
GARAGE=footprint('way/25718288');LEVELS=[.135,3.535,6.935,10.335]
ENTRIES=[(-205.312,0),(-214.943,0),(-257.982,1),(-304.861,2),(-357.144,3)]
ROAD=box(-378,564,-210,581)
def grade(x):
 knots=[(-378,.135),(-370,.135),(-366,10.335),(-357,10.335),(-349,10.335),(-313,6.935),(-305,6.935),(-297,6.935),(-266,3.535),(-258,3.535),(-250,3.535),(-222,.135),(-210,.135)]
 # West return descends around the end, authored separately; no cliff in road.
 knots=knots[3:]
 return smooth_grade(x,knots)
def build(b,routes):
 b.property='bellagioBlock-exterior';b.source='parking-structure';b.detail=0
 b.planar('lake-paving',box(-377,488.9,-191.9,581).difference(GARAGE),.02,True)
 hole=box(-350,516,-308,524)
 for level,y in enumerate(LEVELS):
  p=GARAGE if level==0 else GARAGE.difference(hole)
  b.shell(p,y-.32,y,'concrete',roof=False,solid=True,interior=(footprint('relation/1599958').buffer(.4),14));b.planar('concrete',p,y,True);b.planar('concrete',p,y-.32)
  # Open-sided concrete parking structure: real openings between piers and bands.
  openings=[dict(p=[x,y,563.3],width=9,height=3,yaw=0) for x,k in ENTRIES if k==level]
  if level in [0,1]:openings.append(dict(p=[-192.5,y,505.758 if level==0 else 510.656],width=8,height=3,yaw=math.pi/2))
  b.shell(GARAGE,y,y+1.05,'lake-cream',openings=openings,roof=False,solid=True,interior=(footprint('relation/1599958').buffer(.4),14))
  if level<3:
   b.shell(GARAGE,y+2.75,y+3.08,'lake-cream',roof=False,solid=True,interior=(footprint('relation/1599958').buffer(.4),14))
   for x in np.arange(-366,-199,12):
    for z in [491,513,537,561]:
     if hole.buffer(1).covers(Point(x,z)) or any(abs(x-ex)<5 and z>550 for ex,k in ENTRIES):continue
     Frame(b,x,z,y=y).box('lake-cream',(0,1.55,0),(.65,3.1,.65),True)
  b.source='parking-markings';b.detail=1
  for z in [498,530,544]:
   for x in np.arange(-362,-209,2.7):
    if not GARAGE.buffer(-3).covers(Point(x,z)) or hole.buffer(3).covers(Point(x,z)):continue
    b.box('white',(x,y+.014,z),(.075,.02,5.2))
  for x in [-230,-276,-320]:
   Frame(b,x,550,y=y+.025).text('EXIT',(0,0,0),1,'white')
  # Simple parked sedans are batched decor, kept outside the driving aisles.
  for i,x in enumerate(np.arange(-352,-220,16)):
   z=532 if i%2 else 498
   if hole.buffer(5).covers(Point(x,z)):continue
   f=Frame(b,x,z,y=y);f.box(['silver','blue','charcoal'][i%3],(0,.68,0),(1.8,1,4.3),True);f.box('darkglass',(0,1.32,.1),(1.55,.5,2.25))
   for xx in [-.88,.88]:
    for zz in [-1.35,1.35]:f.box('blackiron',(xx,.35,zz),(.2,.55,.65))
  b.source='parking-structure';b.detail=0
 # Internal ramp stack; open slab slots above the ramp preserve headroom.
 for level in range(3):
  y=LEVELS[level];top=LEVELS[level+1]
  ramp_points=[]
  for x in np.linspace(-350,-310,81):ramp_points.append((float(x),smooth_grade(x,[(-350,y),(-310,top)])))
  for (a,ya),(c,yc) in zip(ramp_points,ramp_points[1:]):
   b.upface('concrete',[(a,ya,516),(c,yc,516),(c,yc,524),(a,ya,524)],True)
   b.face('concrete',[(a,ya-.28,524),(c,yc-.28,524),(c,yc-.28,516),(a,ya-.28,516)])
   for z in [516,524]:barrier(b,(a,ya,z),(c,yc,z))
  # Landing crosses the slab slot at the top; lower ramp entry is west of slot.
  Frame(b,-308,520,y=top).box('concrete',(0,-.16,0),(4.2,.32,8),True)
  routes.append(dict(name=f'Garage internal ramp {level+1}',vehicle=True,points=[[-354,y,520]]+[[x,h,520] for x,h in ramp_points]+[[-303,top,520]]))
 # Side access rises along facade, with a flat landing at each floor entrance.
 b.source='parking-access';b.detail=0
 xs=sorted(set(list(np.arange(-365,-210,.75))+[x for x,k in ENTRIES]+[-349,-313,-297,-266,-250,-222,-210]))
 for a,c in zip(xs,xs[1:]):
  ya,yc=grade(a),grade(c)
  b.upface('charcoal',[(a,ya,567),(c,yc,567),(c,yc,577),(a,ya,577)],True)
  for z in [567,577]:
   b.face('lake-stone',[(a,.02,z),(c,.02,z),(c,yc,z),(a,ya,z)],True)
   # Keep full-width openings to all four entrance links.
   if z==577 or not any(abs((a+c)/2-x)<5 for x,k in ENTRIES):
    barrier(b,(a,ya,z),(c,yc,z))
 for x,k in ENTRIES:
  y=LEVELS[k];f=Frame(b,x,565,y=y);f.box('charcoal',(0,-.15,0),(9,.3,5.1),True)
  for dx in [-4.8,4.8]:f.box('lake-cream',(dx,1.5,-1.5),(.5,3,.5),True)
  f.box('blue',(0,3,-1.5),(8,.6,.25));f.text('P '+str(k+1),(0,2.83,-1.67),.45,'white')
  routes.append(dict(name=f'Garage entrance P{k+1}',vehicle=True,points=[[x,y,572],[x,y,565],[x,y,558],[x,y,551],[x-7,y,551]]))
 # Western turning head stays at rooftop grade; guard across dead-end prevents falls.
 Frame(b,-365,572,y=LEVELS[-1]).box('lake-cream',(-.25,.5,0),(.5,1,10),True)
 routes.append(dict(name='Garage ascending access road',vehicle=True,points=[[x,grade(x),572] for x in np.arange(-211,-360,-2)]))
 # Entrance guidance and rhythm on the long side, preserving open parking slots.
 b.source='parking-detail';b.detail=1
 # Do not leave decorative facade piers in door mouths.
 # Above-floor lights are emissive geometry, no per-bay PointLights.
 for y in LEVELS[:-1]:
  for x in np.arange(-355,-210,18):b.box('warm',(x,y+2.94,550),(3,.05,.12))
 for z,k in [(505.758,0),(510.656,1)]:
  y=LEVELS[k];routes.append(dict(name=f'Garage east entrance P{k+1}',vehicle=True,points=[[-192.5,y,z],[-198,y,z],[-209,y,z]]))
 return dict(osmId='way/25718288',footprint=list(GARAGE.exterior.coords),levels=LEVELS,entries=ENTRIES,estimatedElevations=True)
