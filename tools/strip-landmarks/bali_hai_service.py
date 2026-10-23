"""Bali Hai adjacent maintenance shed: survey footprint, satellite + February2025 street view."""
from common import *
from forum_shops import facade_frame
KEY='baliHaiService';ID='way/133904624';YAW=math.atan2(8.093,15.072)
def frame(B):return Frame(B,-69.6665,3804.6385,yaw=YAW,y=0)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/bali-hai-service';B.detail=0;F=frame(B);p=footprint(ID);w=17.106;d=38.485
 B.shell(p,.18,4.5,'bhs-green-metal-paint',roof=False)
 # Both roof slopes and triangular gables are actual geometry; simple consistent pitched collision.
 def ry(u):return 6.2-abs(u)/(w/2+.25)*1.7
 for side in [-1,1]:
  B.upface('bhs-roof-metal-paint',[F.p(0,6.2,-d/2-.25),F.p(side*(w/2+.25),4.5,-d/2-.25),F.p(side*(w/2+.25),4.5,d/2+.25),F.p(0,6.2,d/2+.25)],True)
 for z in [-d/2,d/2]:B.face('bhs-green-metal-paint',[F.p(-w/2,4.5,z),F.p(w/2,4.5,z),F.p(0,6.2,z)],True)
 F.box('bhs-trim-paint',(0,6.22,0),(.18,.12,d+.65))
 for side in [-1,1]:
  F.box('bhs-trim-paint',(side*(w/2+.25),4.5,0),(.18,.18,d+.65))
  for z in [-d/2,d/2]:F.tube('bhs-trim-paint',(0,6.23,z),(side*(w/2+.25),4.53,z),.065,6)
 # Four pairs of translucent rooflights and ridge extractors, laid flush to slope.
 for z in [-13.5,-4.5,4.5,13.5]:
  for side in [-1,1]:
   u=side*4.9
   for mat,du,dz,off in [('bhs-rooflight-frame-paint',.7,1.45,.04),('bhs-rooflight-paint',.59,1.32,.07)]:
    B.upface(mat,[F.p(uu,ry(uu)+off,zz) for uu,zz in [(u-du,z-dz),(u+du,z-dz),(u+du,z+dz),(u-du,z+dz)]])
  F.box('bhs-service-paint',(0,6.45,z),(1.05,.45,1.9));F.box('bhs-cap-paint',(0,6.7,z),(1.2,.10,2.1))
  for y in [6.32,6.43,6.54]:
   for side in [-1,1]:F.box('bhs-shadow-paint',(side*.53,y,z),(.025,.035,1.7))
 # Long east wall faces yard; photographed roller door plus plausible concealed service bays.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.015)
  G.box('bhs-base-concrete',(L/2,.35,-.045),(L,.34,.08))
  if nx>.7:
   for u in [L*.22,L*.56,L*.84]:
    G.box('bhs-doorframe-paint',(u,2.08,-.10),(3.4,3.85,.16));G.box('bhs-shutter-paint',(u,2.08,-.20),(3.12,3.59,.06))
    for yy in np.arange(.38,3.8,.18):G.box('bhs-shutter-joint-paint',(u,float(yy),-.24),(3.10,.018,.025))
    G.box('bhs-lamp-paint',(u,4.1,-.25),(.45,.16,.35))
   u=L*.08;G.box('bhs-doorframe-paint',(u,1.35,-.12),(1.08,2.4,.13));G.box('bhs-door-paint',(u,1.35,-.22),(.93,2.24,.05));G.box('bhs-handle-paint',(u+.32,1.25,-.26),(.04,.15,.04))
  elif L<20:
   G.box('bhs-vent-paint',(L/2,4.8,-.10),(1.6,.6,.10))
   for yy in np.arange(4.56,5.05,.08):G.box('bhs-shadow-paint',(L/2,float(yy),-.17),(1.5,.024,.03))
  for u in [.3,L-.3]:G.box('bhs-trim-paint',(u,2.4,-.06),(.12,4.2,.12))
  B.detail=1
  for u in np.arange(.12,L,.24):
   # Ribs omitted where they would intersect east roller shutters.
   if nx>.7 and (any(abs(u-L*k)<1.8 for k in [.22,.56,.84]) or abs(u-L*.08)<.6):continue
   G.box('bhs-rib-paint',(float(u),2.45,-.075),(.038,4.1,.065))
  B.detail=0
 # Corrugation is a filtered normal map, avoiding thin-rib shadow aliasing.
 # Paved service court, clipped from shed, with the photographed wall on the street side.
 yard=Polygon([(-92,3790),(-75,3764),(-13,3764),(-13,3818),(-41,3836),(-66,3838)]).difference(p)
 B.planar('bhs-yard-concrete',yard,.16,True)
 B.planar('bhs-yard-concrete',box(-13,3780,-5,3790),.16,True)
 W=Frame(B,0,0,y=0)
 for z0,z1 in [(3764,3780),(3790,3818)]:
  W.box('bhs-block-concrete',(-13,.98,(z0+z1)/2),(.3,1.64,z1-z0),True)
  for y in np.arange(.32,1.7,.22):W.box('bhs-block-joint-paint',(-12.83,float(y),(z0+z1)/2),(.022,.012,z1-z0))
 # Low yard bins and parked equipment storage, leaving an unobstructed central aisle.
 for i,z in enumerate([3770,3776,3804,3810]):
  W.box('bhs-container-paint' if i%2 else 'bhs-muted-blue-paint',(-20,1.05,z),(3.0,1.8,3.7),True)
  W.box('bhs-shadow-paint',(-20,1.97,z),(2.8,.04,3.5))
  for x in [-21.3,-18.7]:W.box('bhs-frame-paint',(x,1.08,z),(.10,1.8,3.8))
 for x,z in [(-43,3774),(-49,3774),(-55,3774),(-40,3827),(-46,3827)]:
  for yy in [.22,.38,.54]:W.box('bhs-pallet-paint',(x,yy,z),(1.6,.10,1.3))
  W.box('bhs-storage-paint',(x,.98,z),(1.4,.75,1.1))
 # Shared service surfaces stay local; no golf-course, road or interior regeneration.
 samples=[]
 for u in np.arange(-7.8,8,.9):
  for z in np.arange(-18.8,19,.9):samples.append(list(F.p(float(u),ry(u)+.55,float(z))))
 Path('build/city-exteriors/bali-hai-service-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Bali Hai adjacent service yard',center=[-59,0,3802],bounds=[-95,3762,-11,3840],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
