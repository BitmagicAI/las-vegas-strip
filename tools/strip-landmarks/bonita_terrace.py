"""Bonita Terrace paired wings, February2026 frontage and satellite courtyard."""
from common import *
from forum_shops import facade_frame
KEY='bonitaTerrace';IDS=['way/969288411','way/969288410'];YAW=-math.atan2(25.548,48.21)
def frame(B):return Frame(B,1638.545,-3282.2,YAW,y=0)
def local(F,x,z):return(F.co*(x-F.x)-F.si*(z-F.z),F.si*(x-F.x)+F.co*(z-F.z))
def rail(F,a,b,y,h=1.05):
 L=math.dist(a,b)
 for t in np.linspace(0,1,math.ceil(L/.18)+1):
  u=a[0]+(b[0]-a[0])*t;w=a[1]+(b[1]-a[1])*t;F.box('bt-rail-paint',(u,y+h/2,w),(.025,h,.025))
 for yy in [.12,h]:F.tube('bt-rail-paint',(a[0],y+yy,a[1]),(b[0],y+yy,b[1]),.03,7)
 F.b.face('bt-collision',[F.p(a[0],y,a[1]),F.p(b[0],y,b[1]),F.p(b[0],y+h,b[1]),F.p(a[0],y+h,a[1])],True)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/bonita-terrace';B.detail=0;F=frame(B);ps=[footprint(i) for i in IDS];samples=[]
 for idx,p in enumerate(ps):
  w0=idx*20.45;B.shell(p,.18,6.18,'bt-tan-stucco',roof=False)
  # Shallow shingled perimeter roof around a white flat membrane and unit equipment.
  outer=[(-.6,w0-.6),(55.17,w0-.6),(55.17,w0+9.7),(-.6,w0+9.7)]
  inner=[(.8,w0+.8),(53.77,w0+.8),(53.77,w0+8.3),(.8,w0+8.3)]
  for j in range(4):
   k=(j+1)%4
   B.upface('bt-roof-paint',[F.p(*[outer[j][0],6.18,outer[j][1]]),F.p(outer[k][0],6.18,outer[k][1]),F.p(inner[k][0],7.05,inner[k][1]),F.p(inner[j][0],7.05,inner[j][1])],True)
   F.tube('bt-fascia-paint',(outer[j][0],6.18,outer[j][1]),(outer[k][0],6.18,outer[k][1]),.055,8)
  B.planar('bt-membrane-paint',F.poly(inner),7.05,True)
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,0);u,w=local(F,*[G.p(L/2,0,0)[j] for j in [0,2]])
   court=(idx==0 and w>8)or(idx==1 and w<21.5)
   if L>20:
    for x in np.arange(2.6,L-1,4.45):
     for y in [.18,3.18]:
      if court:
       G.box('bt-frame-paint',(float(x),y+1.07,-.08),(.98,2.14,.12));G.box('bt-door-paint',(float(x),y+1.07,-.16),(.84,2,.05));G.box('bt-handle-paint',(float(x)+.3,y+1,-.21),(.035,.15,.035))
       window(G,float(x)+1.55,y+1.45,1.15,1.2)
      else:window(G,float(x),y+1.55,1.1,1.25)
    for x in [.8,L-.8]:G.tube('bt-drain-paint',(x,.18,-.12),(x,6.12,-.12),.035,8)
   else:
    # Street ends are mostly white blank panels, with subtle filled window rectangles.
    G.box('bt-white-paint',(L/2,3.1,-.035),(L-.25,5.7,.06))
    for x in [L*.25,L*.75]:
     for y in [1.6,4.7]:G.box('bt-infill-paint',(x,y,-.075),(1.25,1.4,.025))
   G.box('bt-plinth-paint',(L/2,.35,-.045),(L,.34,.08))
  # One rooftop unit per apartment bay and a corresponding small vent.
  for u in np.arange(3,53,4.45):
   w=w0+4.4;F.box('bt-curb-paint',(float(u),7.15,w),(1.35,.20,1.3));F.box('bt-service-paint',(float(u),7.57,w),(1.05,.64,1.1));F.lathe('bt-vent-paint',float(u),w,[(7.90,.31),(7.93,.31)],16)
   F.lathe('bt-service-paint',float(u)+1.25,w+1.9,[(7.05,.09),(7.6,.09),(7.66,.16)],10)
  for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.25):
   for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.25):
    if p.buffer(-.3).contains(Point(x,z)):samples.append([float(x),7.8,float(z)])
 # Continuous galleries and two west-end stairs. Their concealed location is inferred.
 for w in [9.85,19.7]:
  F.box('bt-gallery-concrete',(27.28,3.08,w),(54.56,.2,1.5),True)
  edge=w+(.75 if w<15 else -.75);rail(F,(0,edge),(54.56,edge),3.18)
  rail(F,(54.56,w-.75),(54.56,w+.75),3.18)
  q=F.p(-5.6,0,w);S=Frame(B,q[0],q[2],YAW+math.pi/2,y=0);S.stairs(0,0,1.5,3,5.6,y=.18)
  # Ground-to-gallery outer edge guards continue along each flight.
 # Site surfaces leave an actual recessed pool basin, not a duplicate water plane.
 pool=F.poly([(22,12.35),(39,12.35),(39,17.15),(22,17.15)]);spa=Point(F.p(13,0,14.75)[0],F.p(13,0,14.75)[2]).buffer(1.6,resolution=24)
 site=F.poly([(-7,-7),(56,-7),(56,36.5),(-7,36.5)]).difference(unary_union(ps))
 court=F.poly([(-6.5,9.1),(55,9.1),(55,20.45),(-6.5,20.45)])
 B.planar('bt-asphalt',site.difference(court),.15,True)
 B.planar('bt-court-concrete',court.difference(pool.union(spa)),.18,True)
 for basin in [pool,spa]:
  B.shell(basin,-1.2,.18,'bt-pool-tile',roof=False);B.planar('bt-pool-tile',basin,-1.2,True)
  B.planar('bt_pool',basin.buffer(-.03),.08)
  B.planar('bt-coping-paint',basin.buffer(.22).difference(basin),.21,True)
 # Pool fence with two 1.3m gaps on north/south walks, access kept clear.
 for w in [11.6,17.9]:
  for lo,hi in [(20.8,28.5),(29.9,40.2)]:rail(F,(lo,w),(hi,w),.18,1.15)
 for u in [20.8,40.2]:rail(F,(u,11.6),(u,17.9),.18,1.15)
 # Shade pavilion between spa and pool.
 for u in [17.3,19.2]:
  for w in [12.0,17.5]:F.box('bt-white-paint',(u,1.7,w),(.15,3,.15),True)
 F.box('bt-shade-paint',(18.25,3.22,14.75),(2.45,.12,6.1))
 for w in np.arange(11.8,17.8,.38):F.box('bt-white-paint',(18.25,3.33,float(w)),(2.45,.08,.10))
 # Front garden and sign; foliage uses shared CC0 tree assets at export.
 garden=F.poly([(42,11.2),(53.6,11.2),(53.6,18.3),(42,18.3)])
 walk=F.poly([(41.7,12.6),(54,12.6),(54,14.0),(41.7,14.0)])
 B.planar('bt-soil-paint',garden.difference(walk),.22)
 B.planar('bt-court-concrete',walk,.23)
 for w in [10.9,18.6]:rail(F,(42,w),(54.3,w),.18,1.15)
 for w0,w1 in [(9.2,12.5),(14.2,20.3)]:rail(F,(54.3,w0),(54.3,w1),.18,1.2)
 F.box('bt-sign-paint',(53.8,3.7,11),(1.8,1.1,.16));F.tube('bt-rail-paint',(53.8,.18,11),(53.8,3.7,11),.065,8)
 # Parking side rows, wheelstops and understated perimeter curb.
 for w in [-4.2,33.7]:
  for u in np.arange(1,53,2.8):
   F.box('bt-line-paint',(float(u),.17,w),(.07,.015,4.8));F.box('bt-wheelstop-concrete',(float(u)+1.4,.26,w+(1.8 if w<0 else -1.8)),(1.7,.20,.15),True)
 B.groups={k:g for k,g in B.groups.items() if g['material']!='bt-collision'}
 Path('build/city-exteriors/bonita-terrace-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Bonita Terrace apartments',center=[1655,0,-3256],bounds=[1615,-3290,1694,-3221],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
def window(G,u,y,w,h):
 G.box('bt-frame-paint',(u,y,-.08),(w,h,.1));G.box('bt-glass',(u,y,-.15),(w-.1,h-.1,.04));G.box('bt-frame-paint',(u,y,-.19),(.035,h,.03));G.box('bt-sill-paint',(u,y-h/2-.035,-.14),(w+.1,.07,.22))
