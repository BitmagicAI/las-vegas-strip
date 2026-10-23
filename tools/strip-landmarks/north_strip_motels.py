"""Surviving North Strip courts and convenience stores, Earth2022.
El Mirador footprint is obsolete and deliberately has no replacement building.
"""
from common import *
from forum_shops import facade_frame
from sahara_retail import equipment,glazing
KEY='northStripMotels'
IDS=['relation/6138874','way/364840693','relation/6138875','way/364840690','way/364840692','way/276427161','way/276426491','way/364845133','way/364845132','way/364845135','relation/10307602']
def hip(B,p,y,rise):
 outer=p.buffer(.5,join_style=2);inner=p.buffer(-2.5,join_style=2)
 if inner.is_empty:B.planar('nm-tile-roof',outer,y,True);return
 B.planar('nm-tile-roof',inner,y+rise,True)
 # Inset perimeter produces continuous eaves around mapped courtyard wings.
 for pp in parts(outer):
  for ring in [pp.exterior,*pp.interiors]:
   cc=list(ring.coords)
   for a,b in zip(cc,cc[1:]):
    c=inner.boundary.interpolate(inner.boundary.project(Point(a)));d=inner.boundary.interpolate(inner.boundary.project(Point(b)))
    B.upface('nm-tile-roof',[(a[0],y,a[1]),(b[0],y,b[1]),(d.x,y+rise,d.y),(c.x,y+rise,c.y)],True)
    B.tube('nm-eaves',(a[0],y,a[1]),(b[0],y,b[1]),.08,6)
def court_facade(B,p,h,levels=1,mat='nm-cream',gallery=False):
 B.shell(p,.24,h,mat,roof=False);B.planar('st-roof',p,h,True);B.planar('tile',p,.24,True)
 for pp in parts(p):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   if L<3:continue
   F.box('nm-eaves',(L/2,h,-.18),(L,.22,.55))
   for x in np.arange(2,L-1,4.4):
    for fl in range(levels):
     y=.24+fl*3
     F.box('nm-door',(x-.95,y+1.25,-.1),(.86,2.5,.1))
     F.box('nm-cream',(x-.95,y+2.52,-.18),(1.03,.1,.19))
     F.box('darkglass',(x+.72,y+1.55,-.1),(1.55,1.3,.08))
     F.box('nm-sill',(x+.72,y+.82,-.24),(1.8,.18,.42))
     F.box('st-grey',(x+.72,y+.49,-.13),(1.3,.4,.22))
     for u in np.arange(x+.18,x+1.3,.16):F.box('nm-shadow',(u,y+.49,-.25),(.035,.3,.03))
   if gallery and L>8:
    # A continuous gallery slab and rail in front of the upper room bays.
    F.box('nm-cream',(L/2,3.12,-.85),(L,.24,1.7),True)
    for x in np.arange(.3,L,2.2):
     F.box('nm-rail',(x,3.82,-1.62),(.06,1.3,.06))
     F.box('nm-rail',(x,1.7,-1.5),(.12,2.9,.12),True)
    for y in [3.3,4.45]:F.box('nm-rail',(L/2,y,-1.62),(L,.06,.06))
    for x in np.arange(.15,L,.22):F.box('nm-rail',(x,3.83,-1.62),(.025,1.1,.025))
    if L>22:
     # Two-way access from the exterior court at long-wing ends.
     F.stairs(2,-6.3,1.6,3.24,5.4,y=0)
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;ps=[footprint(i) for i in IDS]
 for idx,p in enumerate(ps):
  B.source='north-retail/'+IDS[idx]
  if idx==3:continue # Earth vacant parcel; do not resurrect El Mirador.
  if idx==0:
   for pp in parts(p):
    casino=pp.centroid.x>1500;h=6.2 if casino else 3.7
    if not casino: court_facade(B,pp,h,1)
    else:
     # Casino walls are largely opaque stucco, not motel room bays.
     B.shell(pp,.24,h,'nm-cream',roof=False)
     B.planar('st-roof',pp,h,True)
     B.planar('tile',pp,.24,True)
     cc=list(pp.exterior.coords)
     for a,b in zip(cc,cc[1:]):
      F,L,nx,nz=facade_frame(B,a,b,pp,0)
      F.box('nm-eaves',(L/2,h,-.15),(L,.22,.4))
      F.box('nm-sand',(L/2,.7,-.06),(L,.8,.13))
      if nz>.7 and L>5:
       glazing(F,L/2,3.6)
       F.box('nm-red',(L/2,3.4,-1.05),(4.6,.28,2.1),True)
       for x in [L/2-2.05,L/2+2.05]:F.box('nm-cream',(x,1.6,-1.8),(.2,3.2,.2),True)
      elif nx>.5 and L>2:
       F.box('darkglass',(L/2,2.2,-.08),(L*.72,2.8,.1))
    if casino:
     B.shell(pp,h,h+.6,'nm-cream',roof=False,solid=False)
     for x,z in [(1501,-3364),(1520,-3357)]:
      B.box('nm-cream',(x,6.9,z),(3,1.4,3))
      for a,b in [((-1.8,-1.8),(1.8,-1.8)),((1.8,-1.8),(1.8,1.8)),((1.8,1.8),(-1.8,1.8)),((-1.8,1.8),(-1.8,-1.8))]:B.face('nm-grey-roof',[(x+a[0],7.6,z+a[1]),(x+b[0],7.6,z+b[1]),(x,11.2,z)])
     F=Frame(B,1527,-3358,math.pi/2,y=0);F.text('AZTEC INN',(0,4.7,-.25),.85,'nm-red')
    equipment(B,pp,h)
  elif idx==1:
   court_facade(B,p,6.3,2,'nm-cream',True);hip(B,p,6.35,1.5)
   # Pool only in the photographed southern court, with solid paving/coping.
   pool=Point(1552,-3264).buffer(4,16).union(Point(1555,-3261).buffer(3,16)).difference(p.buffer(2))
   B.planar('nm_pool',pool,.46);B.planar('tile',pool.buffer(1).difference(pool),.58,True)
   B.shell(pool.buffer(1),.24,.58,'nm-cream',roof=False,solid=True)
  elif idx==2:
   court_facade(B,p,3.8,1,'nm-cream');equipment(B,p,3.8)
   for pp in parts(p):
    cc=list(pp.exterior.coords)
    for a,b in zip(cc,cc[1:]):
     F,L,nx,nz=facade_frame(B,a,b,pp,0)
     if L>2:F.box('nm-red',(L/2,3.65,-.1),(L,.32,.25))
  elif idx==4:
   # Tagged Circle K polygon is the pump canopy in Earth, not an occupied box.
   B.planar('st-roof',p,4.8,True);B.planar('nm-cream',p,4.48,True)
   for pp in parts(p):
    cc=list(pp.exterior.coords)
    for a,b in zip(cc,cc[1:]):
     F,L,nx,nz=facade_frame(B,a,b,pp,0);F.box('nm-red',(L/2,4.64,0),(L,.32,.15))
   for x,z in [(1450,-3250),(1460,-3251),(1450,-3260),(1460,-3261)]:B.box('nm-cream',(x,2.24,z),(.35,4.48,.35),True)
  else:
   h={5:4.2,6:4.5,7:4.2,8:5,9:3.4,10:5.5}[idx]
   mat='nm-sand' if idx==5 else 'nm-cream'
   B.shell(p,.24,h,mat,roof=False);B.planar('st-roof',p,h,True);B.planar('tile',p,.24,True);equipment(B,p,h)
   for pp in parts(p):
    cc=list(pp.exterior.coords)
    for a,b in zip(cc,cc[1:]):
     F,L,nx,nz=facade_frame(B,a,b,pp,0)
     if L<1:continue
     F.box('nm-eaves',(L/2,h,-.1),(L,.25,.35))
     front=nx>.3 or nz>.6
     if idx in [9,10]:
      for x in np.arange(1.5,L-1,3.4):
       F.box('nm-door',(x,1.4,-.08),(.95,2.3,.08));F.box('darkglass',(x+1.1,1.7,-.07),(.85,1.05,.07))
     elif front:
      for x in np.arange(1.5,L-1,3):glazing(F,x,2.6)
      if idx==5:
       for y in [3.3,3.65,4.2]:F.box('nm-red',(L/2,y,-.2),(L,.15,.35))
       if L>10:F.text('CIRCLE K',(L/2,3.45,-.44),.7,'nm-red')
      elif idx==6 and L>10:F.text('TATTOO',(L/2,3.45,-.3),.75,'nm-shadow')
      elif idx==7:
       for y,m in [(3.3,'nm-green'),(3.5,'nm-orange'),(3.7,'nm-red')]:F.box(m,(L/2,y,-.21),(L,.18,.14))
       if L>10:F.text('7 ELEVEN',(L/2,2.9,-.33),.5,'white')
  # No new dynamic lights or interior loads: all facade geometry is batched.
 return dict(key=KEY,name='North Strip motel courts and shops',center=[1510,0,-3270],bounds=list(unary_union(ps).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
