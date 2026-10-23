"""Stepped north frontage (unfinished St.Regis mass) from creator Oct9 aerial.
Approximate 62m current envelope; not the planned full-height condominium tower.
Original podium/interior retained. Exterior setbacks and grouped tall bays modeled.
"""
import math
import numpy as np
from shapely.geometry import box,Point
from common import footprint,parts,Frame

def frontage(B):
 B.source='venetian-north-frontage';B.detail=0
 site=footprint('relation/7770314')
 base=site.intersection(box(195,-814,266,-749.5)).buffer(-1.2).buffer(1.2,resolution=8)
 upper=base.buffer(-4.6,join_style=2)
 assert upper.area>1000
 B.shell(base,17.02,37,'palazzo-stone',roof=False,solid=True);B.planar('ivory',base,37.02)
 B.shell(upper,37.05,62,'palazzo-stone',roof=False,solid=True);B.planar('concrete',upper,62.02)
 # Tier-specific elevations make the photographed broad vertical windows legible.
 for shape,levels,cornices in [(base,[(1.4,6.2,False),(10.5,30.8,False),(32.0,35.3,True)],[(.8,.5,.4),(8.5,.55,.65),(31.6,.6,.7),(36.4,.55,1.15),(37.2,.28,1.45)]),(upper,[(39.5,43.5,False),(46,58.4,True)],[(38.1,.55,.6),(44.5,.75,.9),(60.2,.7,.85),(62,.55,1.15)])]:
  for p in parts(shape):
   coords=list(p.exterior.coords)
   for a,b in zip(coords,coords[1:]):
    L=math.dist(a,b)
    if L<1:continue
    ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
    if shape.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
    F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-nx,-nz),y=0)
    for y,th,d in cornices:F.box('ivory',(0,y,-d/2),(L,th,d))
    if L<3:continue
    count=max(1,round(L/5.8));step=L/count
    for j in range(count):
     x=-L/2+(j+.5)*step;w=min(3.45,step*.62)
     for lo,hi,arched in levels:
      F.box('darkglass',(x,(lo+hi)/2,-.09),(w,hi-lo,.11))
      for side in [-1,1]:F.box('ivory',(x+side*(w/2+.18),(lo+hi)/2,-.28),(.30,hi-lo+.45,.48))
      F.box('ivory',(x,lo-.19,-.33),(w+.68,.30,.68))
      if arched:F.arch(x,-.35,w+.4,hi+.25,'ivory',.16,lo)
      else:F.box('ivory',(x,hi+.14,-.35),(w+.68,.30,.68))
      # Long narrow bay glazing is subdivided finely, not a regular hotel grid.
      for dx in [-w/4,0,w/4]:F.box('champagne',(x+dx,(lo+hi)/2,-.18),(.06,hi-lo,.09))
      B.detail=1
      for yy in np.arange(lo+1.4,hi,1.4):F.box('champagne',(x,yy,-.19),(w,.05,.08))
      B.detail=0
     if shape==upper:
      F.path('ivory',[(x+.39*math.cos(t),60.85+.39*math.sin(t),-.40) for t in np.linspace(0,math.tau,17)],.10,6)
     else:
      F.box('venetian-burgundy',(x,6.35,-.72),(w+.25,.55,1.12))
    for x in [-L/2+.4,L/2-.4]:F.box('ivory',(x,(cornices[0][0]+cornices[-1][0])/2,-.36),(.55,cornices[-1][0]-cornices[0][0],.63))
 # Setback terrace balustrade and roof service parapet.
 for shape,y in [(base,37.45),(upper,62.3)]:
  for p in parts(shape.buffer(-.25)):
   q=list(p.exterior.coords)
   for a,b in zip(q,q[1:]):
    L=math.dist(a,b)
    if L<1:continue
    F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=y)
    F.box('ivory',(0,.65,0),(L,.18,.38))
    B.detail=1
    for x in np.arange(-L/2+.3,L/2,.65):F.lathe('ivory',x,0,[(0,.065),(.18,.11),(.40,.065),(.60,.09)],8)
    B.detail=0
 # Partially built roof: inset unfinished core and louvered mechanical housings.
 core=upper.buffer(-8)
 if not core.is_empty:B.shell(core,62.1,64.1,'concrete',roof=False,solid=False)
 B.source='venetian-podium'
