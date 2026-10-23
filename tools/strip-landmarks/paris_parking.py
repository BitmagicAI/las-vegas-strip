"""Paris parking: Earth2022 rounded bays, stair towers and pale decorative panels."""
from common import *
from forum_shops import facade_frame
from luxor_parking import soffit
KEY='parisParking';IDS=['way/33974142'];LEVELS=[.24,6.24,9.24,12.24,15.24,18.24,21.24,24.24,27.24]
RAMP=(428,431,447,451)
def exterior(B):
 B.property=KEY+'-exterior';B.source='paris-parking';B.detail=0;p=footprint(IDS[0]);top=LEVELS[-1];hole=box(*RAMP)
 for i,y in enumerate(LEVELS):
  deck=p if not i else p.difference(hole.union(box(428,411,437,451)) if i==1 else hole);B.planar('skg-deck',deck,y,True);B.shell(deck,max(.01,y-.23),y,'skg-slab',roof=False)
  if i:soffit(B,deck,y-.23)
 # Roof slot faces north; ground ramp extends beyond it for the taller storey.
 rises=list(zip(LEVELS[1:],LEVELS[2:]))
 for y0,y1 in rises:
  x0,z0,x1,z1=RAMP
  B.upface('skg-deck',[(x0,y1,z0),(x1,y1,z0),(x1,y0,z1),(x0,y0,z1)],True)
  B.face('skg-slab',[(x0,y1-.23,z0),(x1,y1-.23,z0),(x1,y0-.23,z1),(x0,y0-.23,z1)])
  for x in [x0,x1]:B.face('paris-stone',[(x,y1-.23,z0),(x,y0-.23,z1),(x,y0+.85,z1),(x,y1+.85,z0)],True)
  B.upface('skg-line',[(437.45,y1+.015,z0),(437.55,y1+.015,z0),(437.55,y0+.015,z1),(437.45,y0+.015,z1)])
 # Ground's tall storey needs a longer rise, continuing north beyond the upper slot.
 B.upface('skg-deck',[(428,6.24,411),(437,6.24,411),(437,.24,451),(428,.24,451)],True)
 B.face('skg-slab',[(428,6.01,411),(437,6.01,411),(437,.01,451),(428,.01,451)])
 for x in [428,437]:B.face('paris-stone',[(x,6.01,411),(x,.01,451),(x,1.04,451),(x,7.04,411)],True)
 for pp in parts(p):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   if L<3:continue
   n=max(1,round(L/5.8));pitch=L/n;holes=[]
   for y in LEVELS[1:-1]:
    for i in range(n):
     cx=(i+.5)*pitch;w=pitch-.75;holes.append(box(cx-w/2+.36,y+1.04,cx+w/2-.36,y+2.38).buffer(.36,resolution=5))
   upper=box(0,6.24,L,top+.65).difference(unary_union(holes))
   for poly in parts(upper):
    for tri in triangles(poly):B.face('paris-stone',[F.p(x,y,-.08) for x,y in list(tri.exterior.coords)[:-1]],True)
   # Real open arches at vehicle entries, avoiding fake dark painted doorways.
   gatecenters=[]
   if nx>.7:
    for z in [365,420,477,489]:
     pt=Point(465,z)
     if LineString([a,b]).distance(pt)<2:gatecenters.append(LineString([a,b]).project(pt))
   elif nz>.7:gatecenters=[L*.3,L*.72]
   base=box(0,.24,L,6.24)
   for cx in gatecenters:
    arch=box(cx-3,.2,cx+3,2.55).union(Point(cx,2.55).buffer(3,resolution=12).intersection(box(cx-3,2.55,cx+3,6)))
    base=base.difference(arch);F.arch(cx,-.18,6,5.55,'ivory',.14,base=.24)
   for poly in parts(base):
    for tri in triangles(poly):B.face('paris-stone',[F.p(x,y,0) for x,y in list(tri.exterior.coords)[:-1]],True)
   F.box('ivory',(L/2,6.1,-.22),(L,.3,.36));F.box('ivory',(L/2,top+.6,-.22),(L,.22,.36))
 # Tall lift core on east elevation; glass/fret panels occupy distinct bays.
 for z in [451]:
  B.box('paris-stone',(465.5,15,z),(3.2,30,6.4),True);B.box('ivory',(465.5,30.1,z),(3.6,.3,6.8))
 for z in [425,485]:
  F=Frame(B,466,z,-math.pi/2,y=0);F.box('pg-glass',(0,16.9,-.1),(10,20,.15))
  for yy in np.arange(7.3,26.8,1.4):
   for x in np.arange(-4.5,4.7,1.5):F.path('ivory',[(x,yy,-.25),(x+.35,yy+.7,-.25),(x,yy+1.4,-.25)],.04,5)
 # Exposed switchback stair cages on the east side, estimated landings.
 for z in [341,392]:
  for i,y in enumerate(LEVELS[1:]):
   B.box('skg-slab',(467,y-.12,z),(3.4,.24,5.5),True)
   for zz in [z-2.65,z+2.65]:B.box('st-grey',(467,y+.48,zz),(3.3,.9,.06))
   if i<len(LEVELS)-2:
    F=Frame(B,467,z,0,y=0);F.stairs(-.75 if i%2==0 else .75,-2.2,1.2,3,4.4,y=y)
  for xx in [465.5,468.5]:
   for zz in [z-2.6,z+2.6]:B.box('st-grey',(xx,top/2,zz),(.12,top,.12))
 # Northern rooftop plant row, retained at mapped north edge.
 for x in np.arange(387,460,11):
  B.box('skg-slab',(x,top+.85,336),(9,1.7,5))
  for xx in [x-2.3,x+2.3]:
   disk=Point(xx,336).buffer(1.9,resolution=16);B.shell(disk,top+1.7,top+2.05,'st-grey',roof=False);B.planar('darkglass',disk,top+2.05)
 usable=p.buffer(-1).difference(hole.buffer(.7))
 for x in np.arange(382,460,8):
  for z in np.arange(345,505,17):
   if usable.contains(Point(x,z)):B.box('skg-slab',(x,top/2,z),(.45,top,.45),True)
 roof=usable.difference(box(380,330,465,342))
 for x in np.arange(378,459,17):
  for z in np.arange(344,505,2.7):B.planar('skg-line',box(x,z,x+5,z+.08).intersection(roof),top+.014)
 for x in [390,417,452]:
  for z in [360,398,468,498]:
   B.box('st-grey',(x,top+2.4,z),(.09,4.8,.09));B.box('st-grey',(x,top+4.83,z),(.6,.14,.3))
 return dict(key=KEY,name='Paris self parking',center=[420,0,420],bounds=list(p.buffer(4).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
