"""Guardian Angel Cathedral: mapped plan + Earth2022 / PRWilliams exterior photos.
Roof23m and spire31m are proportion estimates, not surveyed dimensions.
Original geometric mural study, not a reproduction or imported Piczek photograph.
"""
from common import *
from venetian_pool_garden import gardens
from forum_shops import facade_frame
from sahara_retail import equipment
KEY='guardianAngel';IDS=['way/564120640','way/1177746897','way/331347841','way/688540494'];Z=-1616.5;FRONT=831.;REAR=878.;RIDGE=23.;EAVE=.65

def exterior(B):
 B.property=KEY+'-exterior';B.source='guardian-cathedral';B.detail=0
 p=footprint(IDS[0]);base=box(FRONT,Z-12.6,REAR,Z+12.6)
 B.planar('ga-paving',p.union(base),.24,True)
 # Main roof carries six projecting triangular window bays on each side.
 # Folded planes meet at a continuous ridge. No overlapping simple A-frame below them.
 for side in [-1,1]:
  z=Z+side*12.6
  for a,b in [(FRONT,836.5)]+[(836.5+i*6.9,836.5+(i+1)*6.9) for i in range(6)]:
   b=min(b,REAR);mid=(a+b)/2
   if a==FRONT:
    B.upface('ga-roof',[(a,RIDGE,Z),(b,RIDGE,Z),(b,EAVE,z),(a,EAVE,z)],True)
   else:
    tip=(mid,11.2,z);r0=(a,RIDGE,Z);r1=(b,RIDGE,Z);e0=(a,EAVE,z);e1=(b,EAVE,z)
    for tri in [(r0,r1,tip),(r0,tip,e0),(r1,e1,tip)]:B.upface('ga-roof',list(tri),True)
    # Dark recessed triangular stained glass; concrete jambs and mullions.
    zz=z-side*.16
    pts=[(a+.32,1,zz),(b-.32,1,zz),(mid,10.65,zz)]
    if side<0:pts.reverse()
    B.face('ga-glass',pts,True)
    for pa,pb in [((a,EAVE,z),(mid,11.2,z)),((mid,11.2,z),(b,EAVE,z))]:B.tube('ga-concrete',pa,pb,.16,6)
    for y in np.arange(1.6,10.5,1.3):
     hw=(b-a)/2*(11.2-y)/(11.2-EAVE)-.22
     if hw>0:B.tube('ga-frame',(mid-hw,y,z+side*.03),(mid+hw,y,z+side*.03),.035,4)
    for dx in [-1.3,0,1.3]:
     top=10.7-abs(dx)*3
     B.tube('ga-frame',(mid+dx,1,z+side*.035),(mid+dx,top,z+side*.035),.035,4)
   # Standing seams track the actual folded roof triangles, barycentric lines.
   faces=[[(a,RIDGE,Z),(b,RIDGE,Z),((a+b)/2,11.2,z)],[(a,RIDGE,Z),((a+b)/2,11.2,z),(a,EAVE,z)],[(b,RIDGE,Z),(b,EAVE,z),((a+b)/2,11.2,z)]] if a!=FRONT else []
   for tri in faces:
    v=np.array(tri,float)
    for t in np.arange(.12,.95,.13):
     q=v[0]*(1-t)+v[1]*t;r=v[0]*(1-t)+v[2]*t;q[1]+=.025;r[1]+=.025
     B.tube('ga-seam',q,r,.024,4)
 B.tube('ga-seam',(FRONT,RIDGE+.04,Z),(REAR,RIDGE+.04,Z),.1,6)
 # West entrance is recessed under a thick concrete triangular fascia.
 for x in [FRONT,REAR]:
  for side in [-1,1]:
   B.face('ga-concrete',[(x,.24,Z+side*12.6),(x,RIDGE,Z),(x+.32,RIDGE,Z),(x+.32,.24,Z+side*12.6)],True)
   B.tube('ga-concrete',(x,.24,Z+side*12.6),(x,RIDGE,Z),.18,6)
 B.face('ga-concrete',[(REAR,.24,Z-12.6),(REAR,.24,Z+12.6),(REAR,RIDGE,Z)],True)
 # Entry wall has a real 4m doorway opening and sheltered threshold.
 for z in [Z-7.1,Z+7.1]:B.box('ga-concrete',(FRONT+1.25,1.86,z),(.3,3.24,10.2),True)
 B.face('ga-mosaic-blue',[(FRONT+1.1,3.48,Z-10.8),(FRONT+1.1,3.48,Z+10.8),(FRONT+1.1,22.1,Z)],True)
 for i in range(14):
  z=Z-10.5+i*1.6
  if abs(z-Z)<2.2:continue
  B.face('ga-mosaic-gold',[(FRONT+1.08,.28,z),(FRONT+1.08,1.8,z+.8),(FRONT+1.08,3.4,z),(FRONT+1.08,1.8,z-.8)])
 # Original angular figurative mosaic approximation. Kept distinct from reference artwork.
 mosaic_layer=0
 def mosaic(coords,mat):
  nonlocal mosaic_layer
  mosaic_layer+=1
  B.face(mat,[(FRONT+1.075-mosaic_layer*.006,y,Z+z) for z,y in coords])
 mosaic([(-4,7),(0,17.8),(4,7),(1,10),(0,8),(-1,10)],'ga-mosaic-gold')
 mosaic([(-1.3,11),(-.7,17),(0,18.4),(.8,17),(1.4,11),(.15,12)],'ga-mosaic-cream')
 for s in [-1,1]:
  mosaic([(s*.7,16.2),(s*3.3,12.5),(s*1.2,13.7)],'ga-mosaic-slate')
  mosaic([(s*2.1,8),(s*2.3,11.8),(s*3,10.6),(s*3.4,7.2)],'ga-mosaic-rust')
 mosaic([(-.6,5),(0,9),(.65,8),(1.2,4.6)],'ga-mosaic-slate')
 for z in [-1.,1.]:B.box('ga-door',(FRONT+2.6,1.6,Z+z),(.12,2.7,1.96),True)
 for z in [-.12,.12]:B.tube('ga-frame',(FRONT+2.51,1.1,Z+z),(FRONT+2.51,1.85,Z+z),.03,6)
 B.box('ga-concrete',(FRONT+2.8,3.4,Z),(3.5,.2,4.1),True)
 # Side annexes follow the octagonal/irregular mapped outlines outside the nave.
 annex=p.difference(base).intersection(unary_union([box(833,Z-24,878,Z-12.6),box(833,Z+12.6,878,Z+24),box(878,Z-24,889,Z+24)]))
 B.shell(annex,.24,4.6,'ga-concrete',roof=False);B.planar('ga-flat-roof',annex,4.6,True)
 for pp in parts(annex):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):B.tube('ga-concrete',(a[0],4.72,a[1]),(b[0],4.72,b[1]),.13,6)
 # Tall narrow side-chapel lights, inset in the opaque portions visible in references.
 for x,z in [(838.7,Z-17.3),(868,Z-17.3),(840,Z+17),(867.5,Z+17)]:
  side=-1 if z<Z else 1
  for dx in [-.9,0,.9]:
   B.box('ga-glass',(x+dx,2.55,z+side*.4),(.43,2.8,.06))
 # Three-legged concrete campanile; clear openings below the taper.
 cx,cz=820.5,Z-14.3
 foot=[(cx-2.1,.24,cz-2.1),(cx+2.5,.24,cz),(cx-2.1,.24,cz+2.1)]
 crown=(cx,28.5,cz)
 for i,a in enumerate(foot):
  b=foot[(i+1)%3];m=((a[0]+b[0])/2,8.8,(a[2]+b[2])/2)
  # Each outer triangle is carved with an arched triangular opening, leaving two taper legs.
  aa=(a[0]+(cx-a[0])*.18,.24,a[2]+(cz-a[2])*.18);bb=(b[0]+(cx-b[0])*.18,.24,b[2]+(cz-b[2])*.18)
  for tri in [(a,crown,m),(crown,b,m),(a,m,aa),(b,bb,m)]:B.face('ga-concrete',tri,True)
 B.box('ga-concrete',(cx,29.9,cz),(.23,3.2,.23),True);B.box('ga-concrete',(cx,30.35,cz),(1.8,.22,.23))
 # Arrival forecourt and surrounding desert beds; stop short of retained street pavement.
 site=Polygon([(813,Z-20),(884,Z-21),(889,Z+18),(836,Z+22),(817,Z+14)]).union(box(813,Z-2.2,834,Z+2.2))
 walk=site.difference(p.union(base)).difference(Point(cx,cz).buffer(3.4))
 B.planar('ga-paving',walk,.18,True)
 B.planar('ga-gravel',Point(cx,cz).buffer(3.4),.2)
 for z in [Z-9,Z+9]:B.planar('ga-rose-paving',box(813,z-.4,831,z+.4).intersection(site),.191)
 for x in [818,824]:B.planar('ga-rose-paving',box(x-.35,Z-19,x+.35,Z+16).intersection(site),.192)
 beds=[]
 for x in [840,853,866,878]:
  for z in [Z-18,Z+17]:
   q=Point(x,z).buffer(1.6);beds.append(q);B.planar('ga-gravel',q,.20)
 gardens(B,site,p.buffer(.5),lambda q:q,.18,points=[(840,Z-18),(853,Z-18),(878,Z-18),(840,Z+17),(853,Z+17),(878,Z+17),(825,Z+11)],crown_clearance=0)
 B.detail=0
 # Cathedral office/hall: mapped two-storey stepped plan, west glazing and roof lattice.
 B.source='guardian-office';office=footprint(IDS[2]);sky=box(920,-1587,948,-1565).intersection(office)
 B.shell(office,.24,8.6,'ga-concrete',roof=False);B.planar('ga-flat-roof',office.difference(sky),8.6,True)
 B.planar('ga-glass',sky,8.1,True)
 for x in np.arange(920,949,2.4):
  for pp in parts(box(x-.12,-1587,x+.12,-1564).intersection(sky)):B.shell(pp,8.5,9.1,'ga-concrete')
 for z in np.arange(-1587,-1563,2.4):
  for pp in parts(box(920,z-.12,948,z+.12).intersection(sky)):B.shell(pp,8.5,9.1,'ga-concrete')
 for pp in parts(office):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   F,L,_,_=facade_frame(B,a,b,pp,0)
   if L<3:continue
   F.box('ga-concrete',(L/2,8.7,-.12),(L,.28,.35))
   for u in np.arange(2,L-1,4.6):
    for y in [2,5.9]:
     F.box('ga-glass',(u,y,-.06),(2.3,2.55,.08))
     for dx in [-1.17,0,1.17]:F.box('ga-frame',(u+dx,y,-.12),(.07,2.67,.11))
     F.box('ga-concrete',(u,y-1.33,-.2),(2.5,.12,.4))
   F.box('ga-concrete',(L/2,4.15,-.12),(L,.27,.25))
 for x,z in [(925,-1607),(930,-1597),(943,-1589),(952,-1577),(927,-1590),(938,-1571)]:
  if office.contains(Point(x,z)) and not sky.contains(Point(x,z)):B.box('ga-frame',(x,9.05,z),(2.3,.9,1.8));B.box('ga-concrete',(x,9.53,z),(2.45,.1,1.9))
 # West office entrance under the roof lattice: two-storey glazing and recessed doors.
 # Door is a closed exterior skin; no invented public indoor circulation.
 for z in np.arange(-1584,-1565,2.4):
  for y in [2.1,6.05]:
   B.box('ga-glass',(920.13,y,z),(.08,3.35,2.27))
   B.box('ga-frame',(920.07,y,z-1.17),(.12,3.5,.08))
 for z in [-1573.6,-1572.4]:
  B.box('ga-door',(920.04,1.65,z),(.1,2.8,1.14),True)
  B.box('ga-glass',(919.975,1.85,z),(.04,2.1,.94))
  B.tube('ga-frame',(919.93,1.2,z+.35),(919.93,1.9,z+.35),.025,6)
 B.planar('ga-paving',box(914,-1585,920.7,-1567).difference(office),.18,True)
 B.box('ga-concrete',(918.9,3.5,-1573),(3,.2,4.6),True)
 # Open carport, roof and columns only; no solid building extrusion.
 B.source='guardian-carport';car=footprint(IDS[3]);B.planar('ga-flat-roof',car,3.3,True)
 B.planar('ga-asphalt',car,.08,True)
 for pp in parts(car):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):B.tube('ga-concrete',(a[0],3.3,a[1]),(b[0],3.3,b[1]),.1,6)
 for x in [961.6,971.1]:
  for z in np.arange(-1619,-1598,5):B.box('ga-frame',(x,1.65,z),(.18,3.3,.18),True)
 return dict(key=KEY,name='Guardian Angel Cathedral exterior',center=[855,0,Z],bounds=list(site.union(office).union(car).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
