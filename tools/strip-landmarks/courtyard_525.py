"""Courtyard525: mapped U-plan, four levels, recessed outer bays and open courtyard galleries."""
from common import *
from forum_shops import facade_frame
KEY='courtyard525'
YAW=-math.atan2(6.189,65.647)
def palm(B,F,u,w,h):
 q=F.p(u,0,w);P=Frame(B,q[0],q[2],y=0)
 P.lathe('c525-bark',0,0,[(.15,.28),(h*.55,.20),(h,.15)],12)
 P.box('c525-collision',(0,h/2,0),(.35,h,.35),True)
 for j in range(38):
  a=j*2.399963;co,si=math.cos(a),math.sin(a);t=(j*.41421356)%1
  tilt=math.radians(70-100*t);r=.45+.2*((j*.414)%1);yy=h+.3*(1-t)
  c=(co*r,yy,si*r);P.path('c525-palm-stem',[(0,h,0),c],.018,5)
  for k in range(12):
   pts=[]
   for n in range(3):
    theta=-1.25+(k+n*.5)*2.5/12;length=1.4*(1 if n==1 else .84)
    radial=math.cos(theta)*length;tang=math.sin(theta)*length
    pts.append(P.p(c[0]+co*radial*math.cos(tilt)-si*tang,c[1]+radial*math.sin(tilt)-.13*(n==1),c[2]+si*radial*math.cos(tilt)+co*tang))
   mat='c525-palm-leaf' if j%3 else 'c525-palm-light'
   B.face(mat,[P.p(*c),pts[0],pts[1]]);B.face(mat,[P.p(*c),pts[1],pts[2]])
 for j in range(14):
  a=j*math.tau/14;co,si=math.cos(a),math.sin(a)
  B.face('c525-bark',[P.p(co*.2,h,si*.2),P.p(co*.5-si*.1,h-1,si*.5+co*.1),P.p(co*.5+si*.1,h-1.2,si*.5-co*.1)])
def railing(G,L,y,w=0,height=1.05):
 for u in np.arange(0,L+.01,.14):G.box('c525-metal-paint',(float(u),y+height/2,w),(.024,height,.024))
 for yy in [y+.08,y+height]:G.box('c525-metal-paint',(L/2,yy,w),(L,.045,.045))
 G.b.face('c525-collision',[G.p(0,y,w),G.p(L,y,w),G.p(L,y+height,w),G.p(0,y+height,w)],True)
def window(G,u,y,w=0,width=1.8,height=1.15):
 G.box('c525-frame-paint',(u,y,w-.06),(width+.14,height+.14,.15));G.box('c525-glass',(u,y,w-.15),(width,height,.035));G.box('c525-frame-paint',(u,y,w-.18),(.045,height,.035))
def door(G,u,y,w=0):
 G.box('c525-frame-paint',(u,y+1.06,w-.07),(1.02,2.12,.14));G.box('c525-door-paint',(u,y+1.03,w-.16),(.88,2.03,.045));G.box('c525-metal-paint',(u+.3,y+1,w-.2),(.035,.16,.03))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/apartments';B.detail=0
 F=Frame(B,1865.601,-3536.598,yaw=YAW,y=0);p=footprint('way/1236725773')
 def local(x,z):dx=x-F.x;dz=z-F.z;return (F.co*dx-F.si*dz,F.si*dx+F.co*dz)
 edges=[];cuts=[]
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.0);u,w=local((a[0]+b[0])/2,(a[1]+b[1])/2)
  inner=(nz>.7 and w<-35 and u<70) or (nz<-.7 and w>-22 and u<65) or (nx<-.7 and u>55)
  bays=[]
  if not inner and L>20:
   for at in np.arange(4,L-3,5.6):
    at=float(at);bays.append(at);cuts.append(G.poly([(at-1.8,-.1),(at+1.8,-.1),(at+1.8,2.1),(at-1.8,2.1)]))
  inner=inner or (55<u<65 and -43<w<-14)
  edges.append((G,L,nx,nz,inner,bays))
 shell=p.difference(unary_union(cuts))
 openings=[dict(p=F.p(56.43,.15+i*2.85,-24.5),yaw=YAW+math.pi/2,width=1.7,height=2.3) for i in range(4)]
 B.shell(shell,.15,11.62,'c525-ivory-stucco',roof=False,openings=openings)
 B.planar('c525-roof-paint',p,11.65,True)
 for G,L,nx,nz,inner,bays in edges:
  G.box('c525-coping-paint',(L/2,11.79,0),(L,.28,.26))
  if L<2:continue
  if inner:
   # The gallery is external to the apartment shell, with continuous floors and steel guards.
   for floor in range(4):
    y=.15+floor*2.85;G.box('c525-gallery-concrete',(L/2,y-.1,-1),(L,.2,2.0),True)
    if floor:railing(G,L,y,-1.92)
    for at in ([] if nx<-.7 else np.arange(1.6,L-1,4.7)):
     door(G,float(at)-.6,y);window(G,float(at)+1,y+1.5,width=1.45)
    for at in np.arange(.15,L,4.7):G.box('c525-metal-paint',(float(at),y+1.35,-1.9),(.075,2.7,.075))
   G.box('c525-soffit-paint',(L/2,11.57,-1),(L,.16,2.2))
   mx,mw=local(G.p(L/2,0,0)[0],G.p(L/2,0,0)[2])
   if nx<-.7 and mx<60:
    # Existing projected lift/stair core: blank dark surface, mint vertical glazed/tiled strip.
    q=F.p(56.43,0,-24.5);doorU=(q[0]-G.x)*G.co-(q[2]-G.z)*G.si
    for u0,u1 in [(0,max(0,doorU-.95)),(min(L,doorU+.95),L)]:
     if u1>u0:G.box('c525-core-paint',((u0+u1)/2,6.1,-.045),(u1-u0,12.1,.075))
    G.box('c525-mint-paint',(.7,6.1,-.1),(1.35,12.1,.12))
   elif nx<-.7:
    for floor in range(4):
     y=.15+floor*2.85
     for at in np.arange(1.6,L-1,4):window(G,float(at),y+1.45,width=2.4,height=1.7)
     if floor:G.box('c525-blue-paint',(L/2,y+.55,-1.93),(L,1.1,.12),True)
  elif bays:
   for floor in range(4):
    y=.15+floor*2.85
    for at in bays:
     G.box('c525-balcony-concrete',(at,y-.10,1),(3.6,.2,2.2),True)
     window(G,at,y+1.4,2.08,2.55,1.9)
     if floor:G.box('c525-white-stucco',(at,y+.55,-.07),(3.6,1.1,.18),True)
     else:
      R=Frame(B,*[G.p(at-1.8,0,0)[i] for i in [0,2]],yaw=G.yaw,y=0);railing(R,3.6,y,-.08)
    for j in range(len(bays)-1):
     at=(bays[j]+bays[j+1])/2;G.box('c525-terracotta-paint',(at,y+1.32,-.045),(1.98,2.7,.07))
   # One dark tiled core breaks the repeated street-facing balcony rhythm.
   if L>45:
    G.box('c525-charcoal-paint',(1.6,5.9,-.06),(3.1,11.4,.1))
    for yy in np.arange(.3,11.6,.22):G.box('c525-tile-joint-paint',(1.6,float(yy),-.12),(3.1,.008,.018))
    for xx in np.arange(.1,3.1,.22):G.box('c525-tile-joint-paint',(float(xx),5.9,-.12),(.008,11.4,.018))
  else:
   for floor in range(4):
    y=.15+floor*2.85
    for at in np.arange(1.6,L-1,3.2):window(G,float(at),y+1.5,width=1.5)
 # Inferred internal stair flights fit inside the mapped projecting core; exterior envelope unchanged.
 for floor in range(4):
  y=.15+floor*2.85
  F.box('c525-gallery-concrete',(59,y-.1,-24.6),(5.4,.2,1.8),True)
  if floor<3:
   q=F.p(58,0,-25.5);S=Frame(B,q[0],q[2],yaw=YAW+math.pi,y=0);S.stairs(0,0,1.35,1.425,2.9,y=y)
   F.box('c525-gallery-concrete',(59,y+1.425-.1,-29.1),(4,.2,1.4),True)
   q=F.p(60,0,-28.4);S=Frame(B,q[0],q[2],yaw=YAW,y=0);S.stairs(0,0,1.35,1.425,2.9,y=y+1.425)
 for g in B.groups.values():
  if g['material']=='stone':g['material']='c525-gallery-concrete'
  if g['material']=='steel':g['material']='c525-metal-paint'
 # Court floor and pool: a true recessed basin, not water laid over a solid courtyard.
 court=F.poly([(15,-42),(65,-42),(65,-14),(0,-14),(0,-21),(15,-21)])
 pool=F.poly([(30,-35),(50,-35),(50,-25),(30,-25)])
 court=court.difference(p)
 B.planar('c525-court-concrete',court.difference(pool),.15,True)
 B.shell(pool,-1.5,.12,'c525-pool-tile',roof=False);B.planar('c525-pool-floor',pool,-1.5,True);B.planar('c525_pool',pool,.02)
 B.planar('c525-coping-stone',pool.buffer(.35).difference(pool),.19,True)
 for u in [30.5,49.5]:
  for w in [-34.4,-25.6]:F.path('c525-metal-paint',[(u,-.5,w),(u,.9,w),(u+.4,1.05,w),(u+.8,.9,w),(u+.8,.15,w)],.034,10)
 for a,b in [((27,-38),(52,-38)),((52,-38),(52,-22)),((52,-22),(27,-22)),((27,-22),(27,-29)),((27,-32),(27,-38))]:
  pa,pb=F.p(a[0],0,a[1]),F.p(b[0],0,b[1]);G=Frame(B,pa[0],pa[2],yaw=-math.atan2(pb[2]-pa[2],pb[0]-pa[0]),y=0);railing(G,math.dist(a,b),.15,0,1.5)
 # Loungers and tables observed around the pool, in shared batches.
 B.detail=1
 for u in np.arange(31,51,3.3):
  F.box('c525-seat-fabric',(float(u),.48,-36.8),(.62,.07,1.45));F.box('c525-seat-fabric',(float(u),.77,-37.45),(.62,.65,.07))
  for dx in [-.26,.26]:F.tube('c525-metal-paint',(float(u)+dx,.15,-37.3),(float(u)+dx,.48,-36.3),.025,6)
 B.detail=0
 # West leasing office: separate small building in official gallery; flat roof, cantilevered shade and terracotta core.
 office=F.poly([(17,-34),(23,-34),(23,-27),(17,-27)]);B.shell(office,.15,3.3,'c525-white-stucco',roof=False);B.planar('c525-roof-paint',office,3.4)
 F.box('c525-terracotta-paint',(22.5,2.1,-30.5),(1.1,4.2,7.2),True)
 for a,b in zip(list(office.exterior.coords),list(office.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,office,.02)
  if nx<-.7:door(G,L*.7,.15);window(G,L*.28,1.7,width=2);G.box('c525-coping-paint',(L/2,3.18,-.65),(L,.22,1.3))
  else:window(G,L*.45,1.65,width=2.3)
 # Thin gravel border on the south street face seen in February2026 imagery.
 B.planar('c525-gravel',F.poly([(0,.2),(65,.2),(65,3),(0,3)]),.11,True)
 # Ground court approaches join the existing west parking area; preserve original roads.
 B.planar('c525-asphalt',F.poly([(-9,-42),(15,-42),(15,-21),(-9,-21)]),.11,True)
 for w in [-39,-35,-31,-27]:F.box('c525-line-paint',(5,.12,w),(5,.01,.08))
 for u,w in [(25,-40),(25,-19),(59,-40)]:
  F.lathe('c525-planter-stone',u,w,[(.15,.65),(.7,.6)],12)
 # Roof services modestly sized from roof imagery, not a continuous equipment block.
 for u,w in [(24,-50),(42,-50),(62,-50),(12,-6),(32,-6),(52,-6),(79,-22),(79,-40)]:
  F.box('c525-service-paint',(u,12.02,w),(1.4,.72,1.1));F.box('c525-metal-paint',(u,12.39,w),(1.2,.025,.9))
 for u,w,h in [(25,-40,12),(25,-19,11),(59,-40,13),(8,2,10),(28,2,12),(47,2,11)]:palm(B,F,u,w,h)
 # Current branding kept on the outer south wall, without residential personal information.
 G=max([e for e in edges if e[3]>.7 and not e[4]],key=lambda e:e[1])[0]
 G.text('COURTYARD 525',(5.0,10.65,-.18),.46,'c525-dark-letter')
 B.groups={k:g for k,g in B.groups.items() if g['material']!='c525-collision'}
 samples=[]
 for u in np.arange(1,64,1.5):
  for w in [-20,-16,-40]:
   q=F.p(float(u),.15,w)
   if court.contains(Point(q[0],q[2])) and not office.buffer(.7).contains(Point(q[0],q[2])) and min(math.hypot(u-a,w-b) for a,b in [(25,-40),(25,-19),(59,-40)])>1:samples.append(q)
 for G,L,nx,nz,inner,bays in edges:
  if inner:
   for floor in range(1,4):
    for at in np.arange(.8,L-.6,1.5):samples.append(G.p(float(at),.15+floor*2.85,-1))
 Path('build/city-exteriors/courtyard-525-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Courtyard525 Apartments',center=[1919,0,-3558],bounds=[1854,-3595,1958,-3527],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
