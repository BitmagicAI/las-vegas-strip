"""2601 Westwood source-only first pass; no shared city installer.
Main facade: November 2021 Street View; plan: owner's 2023 brochure.
Height and roof pitch estimated. Public interior pending corroboration.
"""
from common import *
KEY='westwood-2601'
COLORS={'w26-cream-stucco':'d5c9a5','w26-salmon-stucco':'b77568','w26-trim-paint':'eee5ce','w26-glass':'354345','w26-frame-paint':'9c9f93','w26-vent-paint':'9d9476','w26-roof-tile':'a56f51','w26-roof':'a9a69a','w26-canopy-paint':'9c5752','w26-paving-concrete':'918878','w26-grey-stucco':'777b76','w26-grey-panel':'656b69','w26-pool-tile':'b8cec6','w26_pool':'488a91','w26-ochre-stucco':'bca05d','w26-pylon-paint':'c0c9c7','w26-pylon-inset':'536e83','w26-sign-screen':'18232b','w26-soil':'675542','c525-bark':'80705a','c525-collision':'80705a','c525-palm-stem':'706a38','c525-palm-leaf':'4c6335','c525-palm-light':'6d783c'}
def roof_skirt(B,p,eave,ridge,inset):
 outer=p.buffer(.4,join_style=2);inner=p.buffer(-inset,join_style=2)
 oc=list(outer.exterior.coords)[:-1];ic=list(inner.exterior.coords)[:-1]
 # Match inset corners so neighbouring hips share exact edges, without crossed ribs.
 inside=[min(ic,key=lambda q:math.dist(c,q)) for c in oc]
 B.planar('w26-roof',inner,ridge)
 for i,a in enumerate(oc):
  b=oc[(i+1)%len(oc)];c=inside[(i+1)%len(oc)];d=inside[i]
  B.face('w26-roof-tile',[(a[0],eave,a[1]),(b[0],eave,b[1]),(c[0],ridge,c[1]),(d[0],ridge,d[1])])
  for t in np.linspace(.01,.99,max(2,int(math.dist(a,b)/.26))):
   B.tube('w26-roof-tile',(a[0]+(b[0]-a[0])*t,eave+.025,a[1]+(b[1]-a[1])*t),(d[0]+(c[0]-d[0])*t,ridge+.025,d[1]+(c[1]-d[1])*t),.065,6)
def build(B):
 B.property=KEY+'-exterior';B.source='commercial/'+KEY;B.detail=0
 p=footprint('way/1018431840')
 # Reference dimension 236 x 41 ft overrides the coarse Microsoft footprint.
 # Centre and heading remain mapped; the narrower bar is a documented correction.
 coords=list(p.exterior.coords)
 a,b=max(zip(coords,coords[1:]),key=lambda ab:math.dist(*ab))
 dx,dz=b[0]-a[0],b[1]-a[1];yaw=math.atan2(-dz,dx)
 if math.cos(yaw)<0:yaw+=math.pi
 co,si=math.cos(yaw),math.sin(yaw)
 us=[x*co-z*si for x,z in coords];vs=[x*si+z*co for x,z in coords]
 u=(min(us)+max(us))/2;v=(min(vs)+max(vs))/2
 center=Point(u*co+v*si,-u*si+v*co)
 width=236*.3048;depth=41*.3048
 F=Frame(B,center.x,center.y,yaw,y=0)
 p=F.poly([(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)])
 B.shell(p,0,9.6,'w26-cream-stucco',roof=False)
 roof_skirt(B,p,9.65,10.23,1.3)
 # Cream facade with three-storey salmon arch panels and paired guest windows.
 # Front faces Westwood (positive local z); unseen rear repetition is inferred.
 for side in [-1,1]:
  z=side*(depth/2+.08)
  F.box('w26-trim-paint',(0,9.55,z),(width+.8,.18,.55))
  for bay in range(8):
   u=(bay-3.5)*width/8
   if side==1:
    F.box('w26-salmon-stucco',(u,4.25,z),(2.15,8.1,.10))
    # Rounded crown formed as an original planar fan, with projecting trim.
    points=[F.p(u,8.3,z+side*.07)]+[F.p(u+1.075*math.cos(t),8.3+1.075*math.sin(t),z+side*.07) for t in np.linspace(0,math.pi,17)]
    for j in range(1,len(points)-1):B.face('w26-salmon-stucco',[points[0],points[j],points[j+1]])
    F.arch(u,z+side*.16,2.4,9.5,'w26-trim-paint',.10,base=.15)
   for offset in [-2.5,2.5]:
    x=u+offset
    if abs(x)>width/2-1:continue
    for floor in range(3):
     y=1.55+floor*3.03
     # Entry canopy masks the central ground-floor bays in the reference.
     if side==1 and floor==0 and abs(x)<3.3:continue
     F.box('w26-frame-paint',(x,y,z+side*.10),(1.92,1.45,.12))
     F.box('w26-glass',(x,y,z+side*.18),(1.78,1.31,.045))
     F.box('w26-frame-paint',(x,y,z+side*.23),(.055,1.35,.04))
     F.box('w26-vent-paint',(x,y-1.02,z+side*.14),(1.2,.46,.12))
     for row in range(4):F.box('w26-frame-paint',(x,y-1.19+row*.10,z+side*.22),(1.15,.025,.04))
 # North end observed in February 2020 Street View (ba0gpHmaaTcW7rlwo1ugzg).
 # Ochre blockwork, narrow stair glazing, small windows and service equipment.
 # Positions/dimensions estimated; do not mirror this evidence onto unseen south end.
 end=F.p(width/2,0,0); E=Frame(B,end[0],end[2],yaw+math.pi/2,y=0)
 E.box('w26-ochre-stucco',(0,4.8,.035),(depth,9.6,.065))
 # Shallow joints give the observed masonry coursing without separate block meshes.
 for row in range(31):
  yy=.15+row*.30
  E.box('w26-vent-paint',(0,yy,.075),(depth,.012,.012))
  for xx in np.arange(-depth/2+.30+(row%2)*.30,depth/2,.60):
   E.box('w26-vent-paint',(xx,yy+.15,.075),(.012,.29,.012))
 # Tall stair-window strip toward the street, with floor-level transoms.
 E.box('w26-trim-paint',(-depth*.32,6.3,.13),(.78,5.85,.15))
 E.box('w26-glass',(-depth*.32,6.3,.22),(.60,5.63,.04))
 for yy in [3.55,6.4,9.05]:E.box('w26-frame-paint',(-depth*.32,yy,.26),(.64,.06,.04))
 for yy in [4.65,7.7]:
  E.box('w26-trim-paint',(-.2,yy,.12),(1.55,1.35,.13))
  E.box('w26-glass',(-.2,yy,.21),(1.35,1.16,.04))
  E.box('w26-frame-paint',(-.2,yy,.25),(.05,1.16,.04))
 E.box('w26-frame-paint',(-.2,1.25,.13),(1.8,2.5,.15))
 E.box('w26-trim-paint',(-.2,1.25,.22),(1.65,2.35,.04))
 E.box('w26-frame-paint',(-.2,1.25,.26),(.05,2.35,.04))
 E.box('w26-paving-concrete',(-.2,.12,.65),(2.6,.24,1.2),True)
 # Freestanding screened utility cabinet and protective posts visible at this end.
 E.box('w26-frame-paint',(0,.85,3.0),(2.0,1.7,1.25),True)
 for xx in np.linspace(-.94,.94,19):E.box('w26-trim-paint',(xx,.85,3.65),(.045,1.5,.045))
 E.box('w26-trim-paint',(0,1.73,3.0),(2.12,.08,1.36))
 for xx in [-1.4,1.4]:
  for zz in [2.0,4.0]:E.box('w26-trim-paint',(xx,.65,zz),(.09,1.3,.09),True)
 # Main arrival canopy, supports and closed glazing (interior not yet authored).
 z=depth/2
 F.box('w26-frame-paint',(0,1.55,z+.16),(4.2,3.1,.12),True)
 F.box('w26-glass',(0,1.55,z+.25),(4.0,2.95,.06))
 for x in [-2,0,2]:F.box('w26-frame-paint',(x,1.55,z+.3),(.075,3.05,.08))
 F.box('w26-canopy-paint',(0,3.65,z+2.2),(6.3,.60,4.4))
 F.box('w26-trim-paint',(0,3.65,z+4.43),(4.5,.48,.05))
 F.text('2601',(0,3.65,z+4.48),.3,'w26-frame-paint',back=True)
 for x in [-2.8,2.8]:F.box('w26-cream-stucco',(x,1.65,z+3.9),(.18,3.3,.18),True)
 # Arrival ramp and low side walls: dimensions inferred from the street image.
 # Route follows the broad centre, not decorative planter edges.
 ramp=[F.p(-2.35,.05,z+13),F.p(2.35,.05,z+13),F.p(2.35,.20,z+.3),F.p(-2.35,.20,z+.3)]
 B.upface('w26-paving-concrete',ramp,True)
 for x in [-2.6,2.6]:
  F.box('w26-ochre-stucco',(x,.48,z+7),( .35,.95,11.7),True)
  F.box('w26-trim-paint',(x,.98,z+7),(.46,.10,11.85))
 # Front downpipes and clipped brackets visible beside the central bays.
 for x in [-9.0,9.0]:
  F.tube('w26-ochre-stucco',(x,.22,z+.3),(x,9.35,z+.3),.055,8)
  for yy in [1,3.6,6.6,8.9]:F.box('w26-frame-paint',(x,yy,z+.26),(.18,.045,.13))
 # Existing two-legged roadside pylon: owner brochure specifies 100 ft height,
 # 40 x 30 ft north/south display faces. Placement is estimated from the aerial.
 # Use a dark screen instead of reproducing a third-party advertisement.
 sign_x=width/2+3.0;sign_z=-depth/2-3.0
 Q=Frame(B,*[F.p(sign_x,0,sign_z)[i] for i in [0,2]],yaw+math.pi/2,y=0)
 h=100*.3048;face_w=40*.3048;face_h=30*.3048
 for xx in [-3.4,3.4]:
  Q.box('w26-pylon-paint',(xx,(h-face_h)/2,0),(1.45,h-face_h,1.5),True)
  Q.box('w26-pylon-inset',(xx,(h-face_h)/2,-.77),(.60,h-face_h-2,.05))
  Q.box('w26-pylon-inset',(xx,(h-face_h)/2,.77),(.60,h-face_h-2,.05))
  Q.box('w26-paving-concrete',(xx,.12,0),(2.1,.24,2.1),True)
 for yy in [3.1,12.2,20.5]:Q.box('w26-pylon-paint',(0,yy,0),(7.7,.45,1.25),True)
 Q.box('w26-pylon-paint',(0,h-face_h/2,0),(face_w,face_h,1.5),True)
 for side in [-1,1]:
  Q.box('w26-sign-screen',(0,h-face_h/2,side*.79),(face_w-.38,face_h-.38,.06))
 sign_bounds=Q.poly([(-face_w/2,-1.1),(face_w/2,-1.1),(face_w/2,1.1),(-face_w/2,1.1)])
 # Existing irregular pool, positioned from the brochure site plan; no proposed bar.
 court=F.poly([(-35,z-.05),(-7,z-.05),(-7,z+17),(-27,z+22),(-35,z+22)])
 pool=F.poly([(-29,z+5),(-22,z+5),(-21,z+6),(-24,z+12),(-24,z+19),(-27,z+20),(-30,z+19),(-30,z+6)])
 B.planar('w26-paving-concrete',court.difference(pool.buffer(.28)),.12,True)
 B.planar('w26-pool-tile',pool.buffer(.28).difference(pool),.15,True)
 B.planar('w26-pool-tile',pool,-1.35,True)
 B.shell(pool,-1.35,.15,'w26-pool-tile',roof=False)
 B.planar('w26_pool',pool,.02)
 # Close the court perimeter, leaving a 1.5 m gate opening on its street edge.
 court_ring=[(-35,z-.05),(-7,z-.05),(-7,z+17),(-27,z+22),(-35,z+22),(-35,z-.05)]
 for edge,(a,b) in enumerate(zip(court_ring, court_ring[1:])):
  if edge==0:continue  # Hotel elevation bounds the rear of the court.
  pa,pb=F.p(a[0],0,a[1]),F.p(b[0],0,b[1]);dx,dz=pb[0]-pa[0],pb[2]-pa[2]
  length=math.hypot(dx,dz);G=Frame(B,(pa[0]+pb[0])/2,(pa[2]+pb[2])/2,math.atan2(-dz,dx),y=0)
  spans=[(-length/2,length/2)] if edge!=2 else [(-length/2,-.75),(.75,length/2)]
  for lo,hi in spans:
   G.box('w26-ochre-stucco',((lo+hi)/2,1.05,0),(hi-lo,2.1,.3),True)
   G.box('w26-trim-paint',((lo+hi)/2,2.14,0),(hi-lo,.16,.42))
   count=max(1,int((hi-lo)/2.8))
   for j in range(count):
    x=lo+(j+.5)*(hi-lo)/count
    G.box('w26-salmon-stucco',(x,.81,-.17),(1.75,1.6,.035))
    points=[G.p(x,1.55,-.20)]+[G.p(x+.875*math.cos(t),1.55+.45*math.sin(t),-.20) for t in np.linspace(0,math.pi,13)]
    for k in range(1,len(points)-1):B.face('w26-salmon-stucco',[points[0],points[k],points[k+1]])
  if edge==2:
   for x in [-.82,.82]:G.box('w26-trim-paint',(x,1.12,0),(.18,2.24,.4),True)
   # Gate shown open: decorative leaf beside the opening, never across the route.
   G.box('w26-frame-paint',(1.65,1.05,-.27),(1.5,1.95,.05))
 # Fan palms visible at the court and front facade in the November 2021 view.
 # Reuse the project's original palm geometry, not a downloaded street-view mesh.
 # Exact positions/heights are estimates; leave the ramp and hotel-edge route clear.
 from courtyard_525 import palm
 for x,zz,height in [(-33,z+19,6.8),(-33,z+8,7.4),(-9,z+14.5,6.2),(17,z+3,7.6),(30,z+3,7.0)]:
  F.lathe('w26-paving-concrete',x,zz,[(0,.95),(.20,.95),(.20,.80)],20)
  F.lathe('w26-soil',x,zz,[(.20,.79),(.22,.79)],20)
  palm(B,F,x,zz,height)
 # Separate south building: grey three-storey arched facade observed in Nov 2021.
 # Keep mapped footprint; unseen elevations repeat observed bays as an inference.
 # Roof plant is omitted until supported by a reference.
 annex=footprint('way/276428208')
 B.shell(annex,0,9.25,'w26-grey-stucco',roof=False);roof_skirt(B,annex,9.4,10.1,1.7)
 from shapely.geometry.polygon import orient
 ring=list(orient(annex,sign=1).exterior.coords)
 for a,b in zip(ring,ring[1:]):
  length=math.dist(a,b);G=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  G.box('w26-trim-paint',(0,9.3,-.10),(length+.35,.16,.55))
  count=max(2,round(length/8));step=length/count
  for bay in range(count):
   x=(bay-(count-1)/2)*step
   G.box('w26-grey-panel',(x,4,-.06),(1.9,7.9,.08));G.arch(x,-.16,2.1,9.15,'w26-trim-paint',.085,base=.15)
   for offset in [-2,2]:
    if abs(x+offset)>length/2-1:continue
    for floor in range(3):
     y=1.45+3*floor
     G.box('w26-trim-paint',(x+offset,y,-.10),(1.5,1.35,.10))
     G.box('w26-glass',(x+offset,y,-.18),(1.37,1.22,.045))
     G.box('w26-frame-paint',(x+offset,y,-.22),(.055,1.22,.045))
 bounds=unary_union([p,court,annex,sign_bounds]).bounds
 routes=[dict(name='Main arrival ramp',points=[F.p(0,.12,z+12),F.p(0,.22,z+1)])]
 return dict(key=KEY,name='2601 Westwood — source study',center=[center.x,4,center.y],bounds=list(bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,sourceOnly=True,remaining=['Installed pool gate and wall verification','Additional annex elevations','Public interior','Optimization and installed validation'])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
