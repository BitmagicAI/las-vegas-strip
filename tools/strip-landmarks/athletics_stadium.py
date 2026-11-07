"""Construction exterior: October structure with November 2026 equipment study.

Mapped outline bounds the work; bowl section and arch positions are photographic
estimates. No finished 2028 shell, glazing, seats or field are invented.
"""
from common import *
KEY='athleticsStadium';IDS=['way/1468590525']

def beam(B,mat,a,b,width=.35,depth=.7):
 # Three rectangular prisms form an I-section. Shared batches, no tiny colliders.
 a=np.array(a,float);b=np.array(b,float);d=b-a;d/=np.linalg.norm(d)
 ref=np.array([0,1,0]) if abs(d[1])<.95 else np.array([1,0,0])
 u=np.cross(d,ref);u/=np.linalg.norm(u);v=np.cross(d,u)
 for lo,hi,w in [(-depth/2,-depth/2+.08,width),(depth/2-.08,depth/2,width),(-depth/2+.08,depth/2-.08,.08)]:
  vs=[tuple(p+u*x+v*y) for p in [a,b] for x,y in [(-w/2,lo),(w/2,lo),(w/2,hi),(-w/2,hi)]]
  for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:B.face(mat,[vs[i] for i in f])

def construction_crane(B,F,x,z,reach,height):
 """Original static crawler crane; inferred proportions, no branded mesh reuse.

 Positioned between existing arch planes, inside the nonpublic field. This is a
 reversible November snapshot, not a surveyed equipment layout or moving crane.
 """
 B.source='stadium-construction-equipment'
 C=Frame(B,*[F.p(x,0,z)[i] for i in [0,2]],F.yaw,y=.08)
 red='stadium-crane-red-paint';dark='stadium-equipment-dark-paint'
 for side in [-1,1]:
  C.box(dark,(0,.65,side*2.5),(9,1.3,1.3))
  for xx in np.linspace(-4,4,17):C.box('stadium-steel',(xx,1.34,side*2.5),(.12,.12,1.35))
 C.box(dark,(0,1.7,0),(5,.8,4))
 C.box(red,(-1.5,2.9,0),(5,1.6,3.6))
 C.box(dark,(-4.1,2.9,0),(1.8,1.9,4.5))
 C.box(red,(1.2,3,2.2),(2.2,2.2,1.7))
 C.box('stadium-equipment-glass',(1.2,3.35,3.065),(1.8,1.25,.025))
 # Four longitudinal chords with alternating diagonals on all four faces.
 start=np.array([1.,3.6,0]);end=np.array([reach,height,0]);axis=end-start;axis/=np.linalg.norm(axis)
 u=np.array([0.,0.,1.]);v=np.cross(axis,u)
 corners=[u*a+v*b for a,b in [(-1.2,-1.2),(1.2,-1.2),(1.2,1.2),(-1.2,1.2)]]
 stations=np.linspace(start,end,19)
 for j,(a,b) in enumerate(zip(stations,stations[1:])):
  for k in range(4):
   kk=(k+1)%4
   C.tube(red,tuple(a+corners[k]),tuple(b+corners[k]),.12,6)
   C.tube(red,tuple(a+corners[k]),tuple(a+corners[kk]),.075,6)
   ca,cb=(k,kk) if j%2==0 else (kk,k)
   C.tube(red,tuple(a+corners[ca]),tuple(b+corners[cb]),.065,6)
 for k in range(4):C.tube(red,tuple(end+corners[k]),tuple(end+corners[(k+1)%4]),.075,6)
 # Rear mast and pendant cables; hanging block stays clear of the ground.
 for side in [-1,1]:
  C.tube(red,(-3,3.6,side*1.3),(-5,15,side*.7),.13,6)
  C.tube(dark,(-5,15,side*.7),tuple(end+u*side*.7),.035,5)
  C.tube(dark,tuple(end+u*side*.3),(reach,9,side*.3),.035,5)
 C.box(dark,(reach,8.6,0),(.8,1.1,.8))
 C.path(dark,[(reach,8.1,0),(reach,7.5,0),(reach+.5,7.3,0),(reach+.8,7.7,0)],.10,6)

def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 p=footprint(IDS[0]);F=Frame(B,250.45,1875.52,math.pi/4,y=0)
 def point(r,a,y):return F.p(r*math.cos(a),y,r*.94*math.sin(a))
 def ring(r0,r1,y,a0,a1,solid=False):
  angles=np.linspace(a0,a1,max(2,math.ceil((a1-a0)*r1/5))+1)
  for a,b in zip(angles,angles[1:]):B.upface('stadium-concrete',[point(r0,a,y),point(r1,a,y),point(r1,b,y),point(r0,b,y)],solid)
 def arc_beam(r,y,a0,a1):
  aa=np.linspace(a0,a1,49)
  for a,b in zip(aa,aa[1:]):beam(B,'stadium-steel',point(r,a,y),point(r,b,y),.4,.8)
 B.source='stadium-site'
 # The former Tropicana parcel has no mapped landscape surface. Fill its bare
 # construction ground, subtracting the existing public street/sidewalk masks.
 from shapely.geometry import shape as read_shape
 layers=json.loads(Path('build/geographic-strip/surface-layers.geojson').read_text())['features']
 public=unary_union([read_shape(f['geometry']) for f in layers if f['properties']['kind'] in ['road','sidewalk']])
 site=box(48,1705,435,2120).difference(public.buffer(.05))
 for poly in parts(site):
  for tri in triangles(poly):
   if tri.area>1e-8:B.upface('stadium-soil',[(x,.08,z) for x,z in list(tri.exterior.coords)[:-1]],True)
 # Perimeter hoarding has real posts and a continuous collision boundary.
 boundary=p.buffer(12,join_style=2)
 B.shell(boundary,.14,2.55,'stadium-hoarding',roof=False,solid=True)
 for poly in parts(boundary):
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   line=LineString([a,b])
   for t in np.arange(0,line.length,3):
    q=line.interpolate(t);B.box('stadium-steel',(q.x,1.4,q.y),(.12,2.8,.12))
 # Horseshoe seating faces the Strip (local -Z / world northwest).
 a0,a1=math.radians(-30),math.radians(210)
 B.source='stadium-concrete-bowl'
 tiers=[(60,87,1.2,13.8,30),(91,108,18,27,20),(111,128,31,41,22)]
 for r0,r1,y0,y1,steps in tiers:
  for i in range(steps):
   r=r0+(r1-r0)*i/steps;rr=r0+(r1-r0)*(i+1)/steps;y=y0+(y1-y0)*i/steps;yy=y0+(y1-y0)*(i+1)/steps
   # Radial aisle gaps make the construction bowl's sections legible.
   for k in range(16):
    aa=a0+(a1-a0)*k/16+.009;bb=a0+(a1-a0)*(k+1)/16-.009
    ring(r,rr,yy,aa,bb)
    for a,b in zip(np.linspace(aa,bb,5),np.linspace(aa,bb,5)[1:]):B.face('stadium-concrete',[point(r,a,y),point(r,b,y),point(r,b,yy),point(r,a,yy)])
  ring(r1,r1+5,y1,a0,a1)
 # Exposed floor plates and columns; no opaque completed facade above level 1.
 B.source='stadium-outer-frame'
 for y in [8,16,24,32]:
  ring(128,136,y,a0,a1)
  arc_beam(135,y,a0,a1)
 for a in np.linspace(a0,a1,49):
  for r in [119,135]:beam(B,'stadium-steel',point(r,a,.3),point(r,a,42),.5,.85)
  for y in [8,16,24,32,40]:beam(B,'stadium-steel',point(111,a,y),point(135,a,y),.4,.8)
 # Lower concrete cores, leaving broad loading openings between piers.
 for a in np.linspace(a0,a1,49):
  x,y,z=point(135,a,3.8);B.box('stadium-concrete',(x,y,z),(2,7.3,1.1),True,F.yaw-a)
 # Partly completed outfield concourse, substantially lower than seating sides.
 ring(108,132,9,a1,math.tau+a0)
 for a in np.linspace(a1,math.tau+a0,13):beam(B,'stadium-steel',point(126,a,.2),point(126,a,12),.5,.8)
 # Three installed lattice arches. 88.4m maximum above field is engineer-reported;
 # chord placement/section and intermediate rise remain photo estimates.
 B.source='stadium-roof-arches'
 arches=[(-52,105,71),(0,113,88.4),(52,103,79)]
 for z,half,top in arches:
  def pt(x,side,lower=False):return F.p(x,27+(top-27)*max(0,1-(x/half)**2)-(5 if lower else 0),z+side*1.3)
  xs=np.linspace(-half,half,33)
  for side in [-1,1]:
   for a,b in zip(xs,xs[1:]):
    beam(B,'stadium-arch-paint',pt(a,side),pt(b,side),.6,.9)
    beam(B,'stadium-arch-paint',pt(a,side,True),pt(b,side,True),.6,.9)
    beam(B,'stadium-arch-paint',pt(a,side,True),pt(b,side),.3,.45)
   for x in xs:beam(B,'stadium-arch-paint',pt(x,side),pt(x,side,True),.3,.5)
  for x in xs:
   for lower in [False,True]:beam(B,'stadium-arch-paint',pt(x,-1,lower),pt(x,1,lower),.3,.45)
  # Green temporary shoring under the arch; same six tower layout in references.
  B.source='stadium-shoring'
  for x in [-46,46]:
   height=pt(x,0,True)[1]-.5
   for xx,zz in [(-2.6,-2.6),(2.6,-2.6),(2.6,2.6),(-2.6,2.6)]:F.tube('stadium-shoring-paint',(x+xx,.3,z+zz),(x+xx,height,z+zz),.22,8)
   for y in np.arange(.5,height-3.9,4):
    for a,b in [((-2.6,-2.6),(2.6,-2.6)),((2.6,-2.6),(2.6,2.6)),((2.6,2.6),(-2.6,2.6)),((-2.6,2.6),(-2.6,-2.6))]:
     F.tube('stadium-shoring-paint',(x+a[0],y,z+a[1]),(x+b[0],y+4,z+b[1]),.1,6)
     F.tube('stadium-shoring-paint',(x+a[0],y,z+a[1]),(x+b[0],y,z+b[1]),.12,6)
   F.box('stadium-steel',(x,height,z),(6,.45,6))
  B.source='stadium-roof-arches'
 # Inferred parked lifting equipment in the field, clear of the arch/shoring planes.
 construction_crane(B,F,-20,-26,30,65)
 construction_crane(B,F,18,26,-27,59)
 return dict(key=KEY,name='Athletics stadium construction',center=[250.45,0,1875.52],bounds=list(boundary.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
