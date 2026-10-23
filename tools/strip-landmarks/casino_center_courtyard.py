"""Casino Center courtyard apartments: two mapped wings and exterior circulation."""
from common import *
from forum_shops import facade_frame
KEY='casinoCenterCourtyard';IDS=['way/364846572','way/364846571'];YAW=-math.atan2(2.104,40.962)
def frame(B):return Frame(B,1837.868,-4107.689,yaw=YAW,y=0)
def rail(B,G,L,y,w,skip=None):
 for u in np.arange(.05,L,.15):
  if skip and skip(float(u)):continue
  G.box('ccc-white-paint',(float(u),y+.55,w),(.024,1.08,.024))
 for u in np.arange(0,L,.2):
  if skip and skip(float(u)):continue
  for h in [.08,1.1]:G.box('ccc-white-paint',(float(u)+.1,y+h,w),(.2,.045,.04))
 # Segmented guard collision leaves a true stair opening.
 for u in np.arange(0,L,.5):
  if skip and skip(float(u)+.25):continue
  B.face('ccc-collision',[G.p(float(u),y,w),G.p(min(L,float(u)+.5),y,w),G.p(min(L,float(u)+.5),y+1.1,w),G.p(float(u),y+1.1,w)],True)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/casino-center-courtyard';B.detail=0;F=frame(B);ps=[footprint(i) for i in IDS];allp=unary_union(ps)
 for index,p in enumerate(ps):
  B.shell(p,.15,5.9,'ccc-gray-stucco',roof=False);B.planar('ccc-roof-paint',p.buffer(.18,join_style=2),5.98)
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,.025)
   gallery=(index==1 and nz>.7) or (index==0 and (nz<-.7 or nx<-.7))
   G.box('ccc-roof-trim-paint',(L/2,5.95,-.09),(L,.25,.24))
   if L<3 or (index==1 and nx<-.7):continue
   count=max(1,round(L/4.2));bay=L/count
   for floor in range(2):
    y=.15+floor*2.85
    for j in range(count):
     at=bay*(j+.5);G.box('ccc-frame-paint',(at-.4,y+1.4,-.08),(1.45,1.5,.12));G.box('ccc-glass',(at-.4,y+1.4,-.16),(1.32,1.38,.04));G.box('ccc-frame-paint',(at-.4,y+1.4,-.20),(.035,1.38,.04))
     if gallery:
      G.box('ccc-frame-paint',(at+bay*.28,y+1.12,-.08),(.95,2.18,.12));G.box('ccc-door-paint',(at+bay*.28,y+1.12,-.18),(.83,2.06,.05));G.box('ccc-handle-paint',(at+bay*.28+.3,y+1.05,-.22),(.035,.17,.04))
      G.box('ccc-ac-paint',(at-.4,y+.43,-.17),(.83,.4,.22))
    if gallery:
     G.box('ccc-gallery-concrete',(L/2,y-.1,-1),(L,.2,2.0),True)
     if floor:
      def skip(u):
       q=G.p(u,0,-1.85);du=math.cos(YAW)*(q[0]-1837.868)-math.sin(YAW)*(q[2]+4107.689);dw=math.sin(YAW)*(q[0]-1837.868)+math.cos(YAW)*(q[2]+4107.689)
       return (index==0 and 17<du<20 and 34<dw<36.5) or (index==1 and 19<du<21 and 1<dw<2.5)
      rail(B,G,L,y,-1.85,skip)
      for u in np.arange(.15,L,4.2):G.box('ccc-post-paint',(float(u),1.5,-1.8),(.12,2.7,.12),True)
  x,z=p.representative_point().x,p.representative_point().y;W=Frame(B,0,0,y=0)
  for dz in [-3,3]:
   if p.buffer(-1).contains(Point(x,z+dz)):W.box('ccc-service-paint',(x,6.35,z+dz),(1.4,.65,1.1))
 # Western office facade on the north bar has a projecting gray mansard and central entrance.
 G=Frame(B,1837.868,-4107.689,yaw=YAW+math.pi/2,y=0);L=12.42
 G.box('ccc-office-stucco',(L/2,2.22,-.1),(L,4.1,.16))
 for w,y in [(-.15,5.9),(-1.05,3.75)]:G.box('ccc-trim-paint',(L/2,y,w),(L,.09,.09))
 B.upface('ccc-mansard-paint',[G.p(0,5.9,-.15),G.p(L,5.9,-.15),G.p(L,3.75,-1.05),G.p(0,3.75,-1.05)])
 for u in np.arange(.2,L,.55):G.tube('ccc-trim-paint',(float(u),5.92,-.15),(float(u),3.77,-1.05),.015,4)
 G.box('ccc-frame-paint',(L/2,1.4,-.23),(1.85,2.5,.12));G.box('ccc-glass',(L/2,1.4,-.31),(1.68,2.34,.04));G.box('ccc-frame-paint',(L/2,1.4,-.35),(.045,2.34,.04));G.text('LEASING OFFICE',(L/2,3.2,-.22),.25,'ccc-dark-letter')
 # Shared courtyard and recessed pool, clipped around both mapped wings.
 court=F.poly([(-1,0),(41,0),(41,47),(-1,47)]).difference(allp)
 pool=F.poly([(5,8),(15,8),(15,17),(5,17)])
 B.planar('ccc-court-concrete',court.difference(pool),.15,True)
 B.shell(pool,-1.3,.15,'ccc-pool-tile',roof=False);B.planar('ccc-pool-floor',pool,-1.3,True);B.planar('ccc_pool',pool,.02)
 B.planar('ccc-coping-concrete',pool.buffer(.3).difference(pool),.2,True)
 for a,b in [((3,6),(17,6)),((17,6),(17,19)),((17,19),(3,19)),((3,19),(3,14)),((3,11),(3,6))]:
  pa,pb=F.p(a[0],0,a[1]),F.p(b[0],0,b[1]);G=Frame(B,pa[0],pa[2],yaw=-math.atan2(pb[2]-pa[2],pb[0]-pa[0]),y=0);rail(B,G,math.dist(a,b),.15,0)
 # Street boundary is a block wall with vehicle gate and a walking opening.
 for w0,w1 in [(0,22),(29,47)]:F.box('ccc-boundary-stucco',(-.9,1.15,(w0+w1)/2),(.22,2,w1-w0),True)
 for w in [22,29]:F.box('ccc-post-paint',(-.9,1.25,w),(.45,2.25,.45),True)
 # Gate panel parked open inside, preserving an accessible entry route.
 F.box('ccc-gate-paint',(.5,1.1,21.8),(3,.08,.08));F.box('ccc-gate-paint',(2,1.1,21.8),(.08,1.8,.08))
 # Exterior stair visible in courtyard references: proportions estimated, working rise and landing.
 q=F.p(12,0,33.1);S=Frame(B,q[0],q[2],yaw=YAW+math.pi/2,y=0);S.stairs(0,0,1.5,2.85,6,y=.15)
 F.box('ccc-gallery-concrete',(19,2.90,34.6),(2.0,.2,4.8),True)
 for w in [32.25]:F.box('ccc-white-paint',(19,3.55,w),(2.0,1.1,.06),True)
 F.box('ccc-white-paint',(20,3.55,33.65),(.06,1.1,2.8),True)
 # North wing has a second stair across the courtyard, independent of the south gallery.
 q=F.p(20,0,8);S=Frame(B,q[0],q[2],yaw=YAW+math.pi,y=0);S.stairs(0,0,1.5,2.85,6,y=.15)
 F.box('ccc-gallery-concrete',(20,2.9,1.4),(2.0,.2,1.3),True)
 for g in B.groups.values():
  if g['material']=='stone':g['material']='ccc-gallery-concrete'
  if g['material']=='steel':g['material']='ccc-white-paint'
 B.groups={k:g for k,g in B.groups.items() if g['material']!='ccc-collision'}
 samples=[]
 for u in np.arange(1,28,1.5):
  for w in np.arange(22,32,1.5):
   q=F.p(float(u),.15,float(w))
   if court.contains(Point(q[0],q[2])) and not allp.buffer(.5).contains(Point(q[0],q[2])):samples.append(q)
 Path('build/city-exteriors/casino-center-courtyard-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Casino Center courtyard studios',center=[1858,0,-4085],bounds=[1830,-4122,1882,-4055],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
