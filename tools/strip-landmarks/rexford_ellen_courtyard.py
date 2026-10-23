"""Rexford/Ellen courtyard: January2026 street facade, satellite plan; heights/access estimated."""
from common import *
from forum_shops import facade_frame
KEY='rexfordEllenCourtyard';IDS=['way/1236725808','way/1236725807'];YAW=-math.atan2(1.937,35.467)
def frame(B):return Frame(B,2046.903,-3859.736,YAW,y=0)
def local(F,x,z):return(F.co*(x-F.x)-F.si*(z-F.z),F.si*(x-F.x)+F.co*(z-F.z))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/rexford-ellen';B.detail=0;F=frame(B);ps=[footprint(i) for i in IDS];allp=unary_union(ps);samples=[]
 for index,p in enumerate(ps):
  edges=[];cuts=[];gals=[]
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,0);u,w=local(F,*[G.p(L/2,0,0)[i] for i in [0,2]])
   inner=10<u<25 and ((index==0 and w>9) or(index==1 and w<64))
   screen=L>30 and nx>.8
   if screen:
    at=L*.25;cuts.append(G.poly([(at-1.8,-.05),(at+1.8,-.05),(at+1.8,.65),(at-1.8,.65)]))
   if inner and L>5:gals.append(G.poly([(0,0),(L,0),(L,-1.4),(0,-1.4)]))
   edges.append((G,L,nx,nz,inner,screen))
  B.shell(p.difference(unary_union(cuts)),.18,6.38,'re-white-stucco',roof=False)
  roof=p.buffer(.62,join_style=2);B.shell(roof,6.38,6.55,'re-fascia-paint',roof=False);B.planar('re-roof-paint',roof,6.55,True);B.planar('re-soffit-paint',roof,6.38)
  for G,L,nx,nz,inner,screen in edges:
   if L<3:continue
   G.box('re-cream-paint',(L/2,6.03,-.025),(L,.65,.045))
   if inner:
    if L<5:continue
    for y in [.18,3.18]:
     for u in np.arange(1.4,L-1,3.7):
      door(G,float(u),y)
      if u+1.6<L-.7:window(G,float(u)+1.5,y+1.5,1.1,1.0)
   else:
    for u in np.arange(2.7,L-1.5,4.5):
     if screen and abs(u-L*.25)<2.9:continue
     window(G,float(u),1.42,1.65,.82);window(G,float(u),5.48,1.65,.62)
    if screen:
     at=L*.25
     # Recessed backing and genuinely perforated concrete block screen.
     G.box('re-shadow-paint',(at,3.0,.58),(3.4,5.6,.06))
     for ix in range(8):
      for iy in range(13):
       x=at-1.76+ix*.44;y=.2+iy*.44
       outer=box(x,y,x+.44,y+.44);hole=Polygon([(x+.11,y+.06),(x+.33,y+.06),(x+.38,y+.22),(x+.33,y+.38),(x+.11,y+.38),(x+.06,y+.22)])
       for t in triangles(outer.difference(hole)):
        B.face('re-screen-concrete',[G.p(xx,yy,-.09) for xx,yy in list(t.exterior.coords)[:-1]])
       for a,b in zip(list(hole.exterior.coords),list(hole.exterior.coords)[1:]):B.face('re-screen-concrete',[G.p(a[0],a[1],-.09),G.p(b[0],b[1],-.09),G.p(b[0],b[1],.08),G.p(a[0],a[1],.08)])
   if L>15:
    for u in [.5,L-.5]:G.tube('re-downpipe-paint',(u,.2,-.14),(u,6.4,-.14),.035,8)
  gal=unary_union(gals).difference(allp)
  B.shell(gal,2.98,3.18,'re-gallery-concrete',roof=False);B.planar('re-gallery-concrete',gal,3.18,True);B.planar('re-soffit-paint',gal,2.98)
  stairU=15.5 if index==0 else 13.8;topW=11.86 if index==0 else 61.02
  for poly in parts(gal):
   for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
    mid=Point((a[0]+b[0])/2,(a[1]+b[1])/2)
    if p.distance(mid)<.2:continue
    L=math.dist(a,b);runStart=None;runEnd=None
    for t0 in np.arange(0,L,.15):
     t1=min(L,float(t0)+.15);aa=(a[0]+(b[0]-a[0])*t0/L,a[1]+(b[1]-a[1])*t0/L);bb=(a[0]+(b[0]-a[0])*t1/L,a[1]+(b[1]-a[1])*t1/L);u,w=local(F,(aa[0]+bb[0])/2,(aa[1]+bb[1])/2)
     if abs(u-stairU)<.9 and abs(w-topW)<.3:
      if runStart is not None:rail(B,runStart,runEnd,3.18);runStart=None
      continue
     if runStart is None:runStart=aa
     runEnd=bb
    if runStart is not None:rail(B,runStart,runEnd,3.18)
  # Inferred working stair in the courtyard, independent of apartment interiors.
  startW=topW+(6 if index==0 else -6);q=F.p(stairU,0,startW);S=Frame(B,q[0],q[2],YAW+(math.pi if index==0 else 0),y=0);S.stairs(0,0,1.4,3,6,y=.18)
  # Roof-mounted individual mechanical units distributed over occupied wings only.
  for u in [5.8,28.5]:
   for w in ([4,13,22,30] if index==0 else [42,51,60,68]):
    q=F.p(u,0,w)
    if not p.buffer(-1).contains(Point(q[0],q[2])):continue
    F.box('re-curb-paint',(u,6.68,w),(1.8,.26,1.8));F.box('re-service-paint',(u,7.08,w),(1.5,.56,1.4));F.box('re-vent-paint',(u,7.38,w),(1.2,.03,1.15));F.tube('re-downpipe-paint',(u,6.6,w),(u+2.5,6.6,w),.035,6)
  for x in np.arange(p.bounds[0]+.6,p.bounds[2],1.6):
   for z in np.arange(p.bounds[1]+.6,p.bounds[3],1.6):
    if p.buffer(-.3).contains(Point(x,z)):samples.append([float(x),7.1,float(z)])
 # Narrow central pool and continuous pedestrian circulation linking both buildings.
 pool=F.poly([(14.6,30.8),(20.1,30.8),(20.1,43.1),(14.6,43.1)])
 site=F.poly([(-6,-2),(38,-2),(38,74),(-6,74)]).difference(allp)
 B.planar('re-paving-concrete',site.difference(pool),.18,True)
 B.shell(pool,-1.25,.18,'re-pool-tile',roof=False);B.planar('re-pool-tile',pool,-1.25,True);B.planar('re_pool',pool,.03)
 B.planar('re-coping-concrete',pool.buffer(.25).difference(pool),.21,True)
 # Pool safety boundary has a deliberate opening to the east access path.
 for a,b in [((13.8,30),(20.9,30)),((20.9,30),(20.9,35)),((20.9,38),(20.9,43.9)),((20.9,43.9),(13.8,43.9)),((13.8,43.9),(13.8,30))]:
  pa,pb=F.p(*[a[0],0,a[1]]),F.p(*[b[0],0,b[1]])
  rail(B,(pa[0],pa[2]),(pb[0],pb[2]),.18)
 for w in np.arange(2,72,2.8):F.box('re-line-paint',(-3,.20,float(w)),(5,.015,.07))
 # Quiet planting beds leave the central path and stair approach free.
 for lo,hi in [(20.5,27.8),(47,53.5)]:B.planar('re-gravel',F.poly([(16,lo),(19.6,lo),(19.6,hi),(16,hi)]),.20)
 # Remove hidden guard faces while retaining their collision.
 for k in list(B.groups):
  if B.groups[k]['material']=='re-collision':del B.groups[k]
 Path('build/city-exteriors/rexford-ellen-courtyard-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Rexford Ellen courtyard apartments',center=[2064,0,-3823],bounds=[2036,-3864,2088,-3780],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
def window(G,u,y,w,h):
 G.box('re-frame-paint',(u,y,-.07),(w+.14,h+.13,.13));G.box('re-glass',(u,y,-.15),(w,h,.04));G.box('re-frame-paint',(u,y,-.19),(.04,h,.035))
def door(G,u,y):
 G.box('re-frame-paint',(u,y+1.1,-.08),(1.0,2.2,.13));G.box('re-door-paint',(u,y+1.1,-.16),(.86,2.06,.04));G.box('re-metal-paint',(u+.3,y+1,-.20),(.035,.16,.04))
def rail(B,a,b,y):
 W=Frame(B,0,0,y=0);L=math.dist(a,b)
 for t in np.linspace(0,1,max(2,math.ceil(L/.15)+1)):W.box('re-rail-paint',(a[0]+(b[0]-a[0])*t,y+.53,a[1]+(b[1]-a[1])*t),(.025,1.06,.025))
 for h in [.08,1.06]:W.tube('re-rail-paint',(a[0],y+h,a[1]),(b[0],y+h,b[1]),.023,5)
 B.face('re-collision',[(a[0],y,a[1]),(b[0],y,b[1]),(b[0],y+1.06,b[1]),(a[0],y+1.06,a[1])],True)
