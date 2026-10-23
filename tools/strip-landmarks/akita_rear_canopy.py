"""Akita rear parking shelter, December2022 Street View and mapped plan.
Open timber frame/corrugated metal; 3.15m roof estimated from parked vehicles.
"""
from common import *
KEY='akitaRearCanopy';IDS=['way/457939127']
def exterior(B):
 B.property=KEY+'-exterior';B.source='akita-rear-canopy';B.detail=0
 p=footprint(IDS[0]);x0,z0,x1,z1=p.bounds;W=Frame(B,0,0,y=0)
 def roof(x):return 3.15+.24*(x-x0)/(x1-x0)
 # Ribbed sheet roof clipped to mapped outline, visible underside and thin fascia.
 for t in triangles(p):
  q=list(t.exterior.coords)[:-1];B.upface('arc-roof-paint',[(x,roof(x),z)for x,z in q],True)
  B.face('arc-soffit-paint',[(x,roof(x)-.055,z)for x,z in q][::-1],True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  B.face('arc-edge-paint',[(a[0],roof(a[0])-.14,a[1]),(b[0],roof(b[0])-.14,b[1]),(b[0],roof(b[0]),b[1]),(a[0],roof(a[0]),a[1])])
 for z in np.arange(z0+.12,z1,.28):
  seg=p.intersection(LineString([(x0-1,z),(x1+1,z)]))
  if seg.is_empty or seg.geom_type!='LineString':continue
  a,b=list(seg.coords)[0],list(seg.coords)[-1]
  W.path('arc-edge-paint',[(a[0],roof(a[0])+.012,a[1]),(b[0],roof(b[0])+.012,b[1])],.016,4)
 # Two timber support lines with knee braces, continuous beams and rafters.
 for x in [x0+.6,x1-.6]:
  top=roof(x)-.2
  W.box('arc-timber',(x,top,(z0+z1)/2),(.18,.26,z1-z0))
  for z in np.linspace(z0+.7,z1-.7,6):
   W.box('arc-timber',(x,(top+.18)/2,z),(.18,top-.18,.18),True)
   W.box('arc-foot-paint',(x,.26,z),(.27,.16,.27),True)
   for d in [-1,1]:W.path('arc-timber',[(x,top-.55,z),(x,top-.13,z+d*.55)],.075,4)
   for y in [.36,top-.45]:W.tube('arc-bolt-paint',(x-.105,y,z),(x+.105,y,z),.025,6)
 for z in np.arange(z0+.5,z1,.75):
  W.path('arc-timber',[(x0+.3,roof(x0+.3)-.11,z),(x1-.3,roof(x1-.3)-.11,z)],.055,4)
 # Reference shows one pale corrugated shipping container at northern end.
 cx=(x0+x1)/2;cz=z0+1.45
 W.box('arc-container-paint',(cx,1.49,cz),(6.06,2.59,2.44),True)
 for x in np.arange(cx-2.95,cx+3,.16):
  for z in [cz-1.24,cz+1.24]:W.box('arc-rib-paint',(x,1.49,z),(.05,2.48,.035))
 for x in [cx-3.04,cx+3.04]:
  for z in [cz-.57,cz+.57]:
   W.box('arc-door-paint',(x,1.48,z),(.035,2.4,1.12))
   W.tube('arc-bolt-paint',(x, .36,z),(x,2.62,z),.025,7)
 for x in [cx-2.98,cx+2.98]:
  for z in [cz-1.22,cz+1.22]:W.box('arc-edge-paint',(x,1.49,z),(.12,2.59,.12))
 # Preserve existing lot, add only footprint support to close gaps under the shelter.
 B.planar('arc-asphalt',p,.18,True)
 # Fill only uncovered parking apron; retain every existing city pavement triangle.
 apron=box(112,2815,167,2908);occupied=[p.buffer(.02)]
 for g in json.loads(Path('build/geographic-strip/city-meshes.json').read_text()):
  if not g['faces']:continue
  q=np.asarray(g['vertices'])[np.asarray(g['faces'])];xs=q[:,:,0];zs=q[:,:,2];ys=q[:,:,1]
  m=(xs.max(1)>112)&(xs.min(1)<167)&(zs.max(1)>2815)&(zs.min(1)<2908)&(ys.max(1)<.5)&(ys.min(1)>-.1)
  for t in q[m]:
   poly=Polygon(t[:,[0,2]])
   if poly.area>.001:occupied.append(poly.intersection(apron).buffer(.02))
 apron=apron.difference(unary_union(occupied));B.planar('arc-asphalt',apron,.02,True)
 # West/east parking stalls stop short of existing travel lanes.
 for x0l,x1l in [(114,121),(141,148)]:
  for zz in np.arange(2850,2889,2.65):
   stripe=box(x0l,zz,x1l,zz+.09).intersection(apron)
   if not stripe.is_empty:B.planar('arc-line-paint',stripe,.035)

 samples=[[float(x),roof(x)+.3,float(z)]for x in np.arange(x0,x1,.7)for z in np.arange(z0,z1,.7)if p.buffer(-.1).contains(Point(x,z))]
 routes=[[[cx,.18,z0+3],[cx,.18,z1-.8]],[[x0+.9,.18,z0+9],[x1-.9,.18,z0+9]],[[x0+.9,.18,z0+20],[x1-.9,.18,z0+20]]]
 samples += [[145,.8,z]for z in range(2848,2890,2)]
 routes.append([[145,.02,2850],[145,.02,2888]])
 Path('build/city-exteriors/akita-rear-canopy-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/akita-rear-canopy-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Akita rear parking canopy',center=[cx,0,(z0+z1)/2],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
