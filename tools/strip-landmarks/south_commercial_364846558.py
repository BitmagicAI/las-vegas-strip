"""South Strip unbranded commercial block: Feb2025 Street View and satellite.
Mapped plan retained. Roof/elevation heights and concealed service details estimated.
"""
from common import *
from forum_shops import facade_frame
KEY='southCommercial558';ID='way/364846558'
def exterior(B):
 B.property=KEY+'-exterior';B.source='south-commercial-558';B.detail=0
 p=footprint(ID);B.shell(p,.18,4.6,'s558-tan-brick-paint',roof=False);B.planar('s558-membrane-paint',p,4.58,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,p,.025)
  F.box('s558-coping-paint',(L/2,4.62,-.07),(L,.16,.24));F.box('s558-brown-paint',(L/2,.82,-.08),(L,1.25,.12))
  for y in np.arange(.4,4.5,.23):F.box('s558-mortar-paint',(L/2,y,-.12),(L,.012,.02))
  if nx>.8 and L>20:
   # Street photo: four deep pale masonry piers, recessed dark lower panels,
   # broad cream upper fascia and low standing-seam hip roof.
   for u in np.linspace(2.1,L-2.1,5):
    F.box('s558-shadow-paint',(u,1.32,-.16),(3.25,1.72,.06));F.box('s558-glass',(u,1.35,-.2),(2.95,1.5,.035))
   F.box('s558-cream-paint',(L/2,3.25,-.24),(L-1,2,.38))
   for u in np.linspace(.6,L-.6,6):
    F.box('s558-tan-brick-paint',(u,2.02,-.52),(.55,3.68,.75),True)
    F.box('s558-coping-paint',(u,3.89,-.54),(.66,.12,.84))
   for u in np.arange(1,L-1,2.3):F.box('s558-mortar-paint',(u,3.28,-.441),(.016,1.84,.012))
  elif nz<-.8 and L>20:
   for u in np.arange(2,L-2,3.6):
    F.box('s558-frame-paint',(u,2,-.13),(2.8,2.7,.1));F.box('s558-glass',(u,2,-.19),(2.65,2.5,.04))
    F.box('s558-frame-paint',(u,2,-.23),(.055,2.5,.08))
   F.box('s558-brown-paint',(L/2,3.6,-1),(6,.23,2.2))
   for u in [L/2-2.7,L/2+2.7]:F.box('s558-tan-brick-paint',(u,1.8,-1.6),(.4,3.25,.4),True)
   F.box('s558-frame-paint',(L/2,1.5,-.25),(1.8,2.6,.12));F.box('s558-glass',(L/2,1.5,-.33),(1.65,2.4,.03))
  elif L>8:
   F.box('s558-door-paint',(L*.65,1.4,-.16),(1.05,2.4,.12));F.box('s558-vent-paint',(L*.25,3.2,-.15),(1.5,.7,.12))
   for y in np.arange(2.9,3.5,.09):F.box('s558-shadow-paint',(L*.25,y,-.22),(1.4,.025,.02))
 # Hip roof follows the observed rotated east rectangle, not the whole L footprint.
 F=Frame(B,-46.55,3417.7,yaw=-.0472,y=0);w=27.5;d=24.6;e=4.95;rise=2.25
 corners=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)];ridge=[(-(w-d)/2,e+rise,0),((w-d)/2,e+rise,0)]
 faces=[[(corners[0][0],e,corners[0][1]),(corners[1][0],e,corners[1][1]),ridge[1],ridge[0]],[(corners[1][0],e,corners[1][1]),(corners[2][0],e,corners[2][1]),ridge[1]],[(corners[2][0],e,corners[2][1]),(corners[3][0],e,corners[3][1]),ridge[0],ridge[1]],[(corners[3][0],e,corners[3][1]),(corners[0][0],e,corners[0][1]),ridge[0]]]
 for face in faces:B.upface('s558-roof-metal-paint',[F.p(*q)for q in face],True)
 for a,b in zip(corners,corners[1:]+corners[:1]):
  F.tube('s558-roof-rib-paint',(a[0],e,a[1]),(b[0],e,b[1]),.07,6)
 # Parallel standing seams clipped at hip-plane transitions. Near detail only.
 B.detail=1
 for u in np.arange(-w/2+.35,w/2,.7):
  vv=max(0,d/2-(w/2-abs(u)));cuts=sorted(set([-d/2,-vv,vv,d/2]))
  def yy(v):return e+rise*max(0,min((w/2-abs(u))/(d/2),(d/2-abs(v))/(d/2)))+.035
  for va,vb in zip(cuts,cuts[1:]):
   if vb-va>.01:F.tube('s558-roof-rib-paint',(float(u),yy(va),va),(float(u),yy(vb),vb),.025,4)
 B.detail=0
 # Inferred equipment on the flat service roof, constrained to the mapped footprint.
 W=Frame(B,0,0,y=0)
 for x,z in [(-65,3419),(-65,3424),(-54,3434),(-45,3434)]:
  if p.buffer(-1.2).contains(Point(x,z)):
   W.box('s558-service-paint',(x,5.15,z),(2.6,1.1,2));W.box('s558-vent-paint',(x,5.72,z),(2.2,.04,1.6))
 # Boundary approach walls and path match the dry roadside yard; no building in the yard.
 site=box(-74,3393,-4,3442).difference(p);path=box(-72,3393,-30,3396).union(box(-32,3393,-29,3410)).difference(p)
 B.planar('s558-gravel',site.difference(path),.12,True);B.planar('s558-paving-concrete',path,.18,True)
 for a,b in [((-31,3395),(-5,3395)),((-5,3395),(-5,3400)),((-41,3439),(-7,3439))]:
  x,z=a;xx,zz=b;L=math.dist(a,b);G=Frame(B,x,z,yaw=-math.atan2(zz-z,xx-x),y=0)
  G.box('s558-tan-brick-paint',(L/2,1.1,0),(L,2.05,.35),True);G.box('s558-coping-paint',(L/2,2.16,0),(L,.12,.44))
  for y in np.arange(.3,2.1,.24):G.box('s558-mortar-paint',(L/2,y,-.185),(L,.012,.015))
 return dict(key=KEY,name='South Strip commercial building',center=[-52,0,3418],bounds=[-75,3392,-3,3443],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
