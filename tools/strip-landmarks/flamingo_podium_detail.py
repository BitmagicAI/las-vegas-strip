"""Surveyed Flamingo podium with Earth2022 envelope and 2025 Burger frontage.
Heights are estimates except mapped23m north block. Public interiors retained.
"""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
IDS=['way/116761428','way/310585854','way/116761035','way/115767903']
class Access:
 def wall(self,a,b,lo,hi):
  line=LineString([a,b]);L=line.length;r=box(0,lo,L,hi)
  # Existing public entrance and south lobby must remain open through the shell.
  for x,z,w in [(34,-47,20),(140,62,18),(220,62,12)]:
   q=Point(x,z)
   if line.distance(q)<7:
    s=line.project(q);r=r.difference(box(s-w/2,0,s+w/2,8.5))
  return [[(line.interpolate(x).x,y,line.interpolate(x).y) for x,y in list(t.exterior.coords)[:-1]] for pp in parts(r) for t in triangles(pp)]

def petal(B,x,z,base=10,scale=1):
 """Radial ribbon panels, separate from building walls and physical circulation."""
 F=Frame(B,x,z,math.pi/2,y=0)
 for side in [-1,1]:
  for k in range(3):
   points=[]
   for t in np.linspace(0,1,33):
    c=np.array([side*(2+(10-k*2)*t),base+scale*(1+8*t+2*math.sin(math.pi*t)+k*.6),0.5*math.sin(math.pi*t)])
    w=math.sin(math.pi*t)*(1.4-.2*k)*scale
    points.append([F.p(*(c+np.array([0,w,0]))),F.p(*(c-np.array([0,w,0])))])
   for a,b in zip(points,points[1:]):B.face('fl-petal-pink',[a[0],a[1],b[1],b[0]])
   for i in [0,1]:B.path('fl-petal-cream',[q[i] for q in points],.07,6)
   for pair in points[2:-2:2]:B.tube('fl-petal-gold',*pair,.025,4)
 # Slender central flame, rising above the horizontal petals.
 for t0,t1 in zip(np.linspace(0,1,33),np.linspace(0,1,33)[1:]):
  def pair(t):
   w=2.2*math.sin(math.pi*t)**.7;cx=1.2*math.sin(math.pi*t)
   return [F.p(cx-w,base+12*scale*t,.05),F.p(cx+w,base+12*scale*t,.05)]
  a,b=pair(t0),pair(t1);B.face('fl-petal-pink',[a[0],a[1],b[1],b[0]])
 for side in [-1,1]:F.path('fl-petal-cream',[(1.2*math.sin(math.pi*t)+side*2.2*math.sin(math.pi*t)**.7,base+12*scale*t,.05) for t in np.linspace(0,1,33)],.07,6)

def exterior(B):
 B.property='flamingoExterior-exterior';B.source='flamingo-podium';B.detail=0
 records=[dict(BYID[i],shape=footprint(i),base=.24,height=h) for i,h in zip(IDS,[12.8,12.8,23])]
 # Towers occlude podium roofs but their existing GLB remains unchanged.
 towerids=['way/115766957','way/115766962','way/115766969']
 records.extend(dict(BYID[i],shape=footprint(i),base=12.5,height=79.5) for i in towerids)
 S=BuildingSurfaces(records);access=Access()
 for r in records[:3]:
  p=r['shape'];h=r['height'];ident=r['id']
  for poly in parts(p):
   cc=list(poly.exterior.coords)
   for a,b in zip(cc,cc[1:]):
    wall=S.wall(ident,a,b,.24,h,access)
    for t in wall:B.face('fl-stucco',t,True)
    if not wall:continue
    line=LineString([a,b]);L=line.length;F,_,nx,nz=facade_frame(B,a,b,poly,0)
    # Clip every decorative patch to exposed wall ownership, including door holes.
    mask=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in wall])
    def patch(mat,x0,y0,x1,y1,d=.12):
     for q in parts(mask.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(line.interpolate(x).x+nx*d,y,line.interpolate(x).y+nz*d) for x,y in list(t.exterior.coords)[:-1]])
    public=nx<-.7 or nz<-.7 or nz>.7
    for y in [1,h-.9,h-.3]:patch('fl-white',0,y,L,y+.18,.18)
    if public:
     for x in np.arange(1.1,L-1,4):
      patch('fl-shop-glass',x,.65,min(x+3.4,L-.3),min(7,h-2),.16)
      for xx in [x,x+1.7,x+3.4]:patch('fl-shop-frame',xx,.6,xx+.065,min(7.1,h-2),.20)
     for y in [3.2,6.9]:patch('fl-shop-frame',0,y,L,y+.075,.21)
    if h>20:
     for x in np.arange(1.2,L-2,7):patch('fl-panel-joint',x,9,x+.035,h-.8,.14)
     for y in [9,15,20]:patch('fl-panel-joint',0,y,L,y+.035,.14)
    elif not public:
     for x in np.arange(4,L-3,9):patch('fl-service-paint',x,.4,x+3.4,4.5,.15)
   roof=S.roof(ident,poly,h)
   B.planar('fl-membrane-paint',roof,h+.025,True)
   safe=roof.buffer(-3)
   # Cluster mechanical units around service runs, leaving broad clear roof fields.
   for ix,x in enumerate(np.arange(poly.bounds[0]+4,poly.bounds[2]-3,12)):
    for iz,z in enumerate(np.arange(poly.bounds[1]+4,poly.bounds[3]-3,16)):
     if (ix+2*iz)%7 not in (0,1):continue
     if not safe.contains(box(x-1.5,z-2,x+1.5,z+2)):continue
     B.box('fl-service-paint',(x,h+.65,z),(3,1.25,4))
     for dz in [-1,1]:B.lathe('fl-shop-frame',(x,z+dz),[(h+1.3,.65),(h+1.38,.65),(h+1.38,.025)],16)
 # Strip-facing renovated Burger patio and tall glazed restaurant frontage.
 B.source='flamingo-burger-front'
 F=Frame(B,28.6,-119,math.pi/2,y=0)
 F.box('fl-shop-glass',(0,8.5,0),(46,15,.12))
 for x in np.arange(-23,24,3.8):F.box('fl-shop-frame',(x,8.5,-.14),(.10,15.1,.18))
 for y in [3.8,7.2,11,15.8]:F.box('fl-shop-frame',(0,y,-.15),(46,.12,.18))
 for x in [-23,23]:F.box('fl-shop-frame',(x,11,-.35),(1.3,22,.6));F.box('fl-white',(x,22.2,-.3),(1.7,.4,.7))
 for side in [-1,1]:
  F.box('fl-shop-frame',(side*12,4.1,-4),(20,.4,6))
  F.text('GORDON RAMSAY BURGER',(side*12,3.85,-7.08),.55,'fl-white')
  for x in [side*3,side*21]:F.box('fl-shop-frame',(x,2,-6.5),(.18,4,.18),True)
 F.box('fl-patio-paving',(0,.2,-4),(46,.18,7),True)
 for x in np.arange(-22,23,2):
  F.box('fl-shop-frame',(x,.85,-7.2),(.045,1.3,.045))
  F.box('fl-shop-glass',(x+1,.9,-7.2),(1.94,1.1,.04))
 F.box('fl-shop-frame',(0,1.52,-7.2),(46,.045,.045))
 for x in [-19,-14,-9,9,14,19]:
  for z in [-3,-5.7]:
   F.box('fl-table-wood',(x,.95,z),(1.05,.09,.75));F.box('fl-shop-frame',(x,.55,z),(.10,.7,.10))
   for dx in [-.8,.8]:
    F.box('fl-chair-fabric',(x+dx,.53,z),(.48,.10,.5));F.box('fl-chair-fabric',(x+dx,.88,z+.23),(.48,.6,.07))
    for xx in [-.18,.18]:F.box('fl-shop-frame',(x+dx+xx,.3,z),(.04,.45,.35))
 F.box('fl-sign-dark',(0,4.9,-4.1),(2.1,8.6,2.1),True)
 F.text('BURGER',(0,6.2,-5.18),.48,'fl-white');F.text('GORDON',(0,5.3,-5.18),.36,'fl-white');F.text('RAMSAY',(0,4.7,-5.18),.36,'fl-white')
 petal(B,22.6,-119,9.5,.9)
 # Smaller independent lotus entrance canopy (not a resort-width stretched balloon).
 B.source='flamingo-entry-canopy'
 F=Frame(B,31,-12,math.pi/2,y=0)
 F.box('fl-petal-cream',(0,5.1,0),(35,.45,7))
 for x in [-16,16]:
  F.box('fl-petal-cream',(x,3,0),(1.3,6,1.3),True)
  for y in [5.5,6,6.5]:F.box('fl-petal-cream',(x,y,0),(2.5-(y-5.5)*.5,.3,2.5-(y-5.5)*.5))
 F.text('Flamingo',(0,5.8,-3.6),1.6,'fl-letter')
 petal(B,27,-12,6,.42)
 # Preserve the actual main public entrance at z=-47 with a clear approach.
 B.planar('fl-patio-paving',box(26,-57,46,-37),.18,True)
 # South lobby extension to retained interior floor.
 B.planar('fl-patio-paving',box(130,43,150,63),.18,True)
 # South arrival canopy: open curved drive-under roof, with circular roof light.
 B.source='flamingo-south-canopy'
 p=footprint('way/115767903');oculus=Point(156,73).buffer(2.4,resolution=32);roof=p.difference(oculus)
 B.shell(roof,6.0,6.5,'fl-stucco',roof=False)
 B.planar('fl-membrane-paint',roof,6.5,True)
 for poly in parts(roof):
  for t in triangles(poly):B.face('fl-white',[(x,6,z) for x,z in reversed(list(t.exterior.coords)[:-1])],True)
 for x,z in [(137,70),(147,81),(166,81),(178,70)]:
  B.box('fl-stucco',(x,3.1,z),(.75,6.2,.75),True)
  B.box('fl-white',(x,.4,z),(1.1,.8,1.1))
 B.planar('fl-patio-paving',p,.18,True)
 # Ribbon tips close to one point: omit zero-area triangulation at the tips.
 for g in B.groups.values():
  if not g['source'].startswith('flamingo-'):continue
  v=np.asarray(g['vertices']);g['faces']=[f for f in g['faces'] if np.linalg.norm(np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]]))>1e-10]
 return IDS
