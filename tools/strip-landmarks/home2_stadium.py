"""Home2 Stadium: original measured-footprint shell; photo-supported, inferred public plan."""
from common import *
KEY='home2-stadium';IDS=['way/790044913'];YAW=-math.atan2(30.624,25.216)
def frame(B):return Frame(B,-824.745,1779.52,YAW,y=0)
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=frame(B);p=footprint(IDS[0]);entry=F.p(67.46,.24,7.8)
 doors=[dict(p=entry,yaw=YAW+math.pi/2,width=2.8,height=2.9,name='Home2 south lobby entrance',venue=KEY)]
 B.shell(p,.02,17.55,'h2-white-stucco',openings=doors,roof=False);B.planar('h2-roof',p,17.55)
 # Offset facade construction keeps trim/glass away from the collision shell.
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  L=math.dist(a,b)
  if L<.5:continue
  G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  q=G.p(L/2,0,-.2);sgn=-1 if not p.covers(Point(q[0],q[2])) else 1
  q=G.p(L/2,0,0);dx=q[0]-F.x;dz=q[2]-F.z;lx=F.co*dx-F.si*dz;lz=F.si*dx+F.co*dz
  sign_end=(lx<.1 or lx>61) and L<24
  # Stone at the end bays; dark vertical cladding at the long ground floors.
  ground='h2-stone' if sign_end else 'h2-charcoal-paint'
  n=max(1,round(L/3.7));pitch=L/n
  for i in range(n):
   u=(i+.5)*pitch;qp=G.p(u,0,0)
   nearentry=math.dist(qp[::2],entry[::2])<2.2
   qx=F.co*(qp[0]-F.x)-F.si*(qp[2]-F.z);qz=F.si*(qp[0]-F.x)+F.co*(qp[2]-F.z)
   grayhere=(qx<7.1 and qz>10.8) or (qx>54.0 and qz>13.1)
   if not nearentry:G.box('h2-stone' if grayhere else ground,(u,1.77,sgn*.06),(pitch-.02,3.5,.08))
   for f in range(4):
    y=5.15+f*3.08
    if grayhere:G.box('h2-gray-paint',(u,y,sgn*.18),(pitch,3.08,.28))
    elif L>24:G.box('h2-ochre-paint',(u,y,sgn*.065),(pitch-.03,2.66,.08))
    # Long narrow glazing with a visibly separate lower transom.
    if L>2.8 and not grayhere:
     w=min(1.38,pitch-.7)
     G.box('h2-frame-paint',(u,y,sgn*.16),(w+.14,2.58,.16))
     G.box('h2-glass',(u,y+.15,sgn*.27),(w,2.13,.05))
     G.box('h2-transom-glass',(u,y-1.07,sgn*.27),(w,.27,.05))
     G.box('h2-frame-paint',(u,y-.86,sgn*.31),(w+.02,.055,.055))
     G.box('h2-sill-paint',(u,y-1.31,sgn*.28),(w+.2,.08,.32))
    if L>24 and not grayhere:
     for dy in [-.8,0,.8]:G.box('h2-panel-joint',(u,y+dy,sgn*.117),(pitch-.12,.012,.016))
   if L>2.8 and not nearentry and not grayhere:
    G.box('h2-frame-paint',(u,1.8,sgn*.16),(1.5,2.65,.14));G.box('h2-glass',(u,1.95,sgn*.26),(1.36,2.2,.05));G.box('h2-transom-glass',(u,.70,sgn*.26),(1.36,.27,.05))
   if not nearentry and L>24:
    for du in np.arange(-pitch/2+.10,pitch/2,.20):G.box('h2-panel-joint',(u+float(du),1.77,sgn*.12),(.012,3.45,.016))
   if not grayhere:
    for y in [3.67,6.77,9.85,12.93,16.01,17.25]:G.box('h2-white-stucco',(u,y,sgn*.19),(pitch+.02,.38 if y<17 else .65,.23))
  if not sign_end:
   for u in [.48,L-.48]:
    qv=G.p(u,0,0);qx=F.co*(qv[0]-F.x)-F.si*(qv[2]-F.z);qz=F.si*(qv[0]-F.x)+F.co*(qv[2]-F.z)
    if not ((qx<7.1 and qz>10.8) or (qx>54 and qz>13.1)):G.box('h2-white-stucco',(u,10.48,sgn*.20),(.92,13.15,.26))
  G.box('h2-roof-metal',(L/2,17.64,0),(L+.12,.14,.48))
 # Gray end stair/sign volumes, lime returns and shallow aqua crown, as seen from both courts.
 for x,z,w,d in [(3.5,16.3,7,10.6),(57.7,17.5,7.2,8.9)]:
  F.box('h2-gray-paint',(x,10.85,z),(w,14.3,d))
  F.box('h2-lime-paint',(x-w/2-.18,10.85,z-d/2+.25),(.30,14.3,.50))
  F.box('h2-roof-metal',(x,18.22,z),(w+.2,.18,d+.2))
  F.box('h2-aqua-paint',(x,18.85,z),(w-1.2,1.15,d-1.1))
  for yy in np.arange(4.5,17.8,1.4):
   F.box('h2-panel-joint',(x,float(yy),z+d/2+.02),(w,.014,.018))
  F.text('HOME',(x-.65,16.5,z+d/2+.60),1.18,'h2-letter',back=True)
  F.box('h2-lime-paint',(x+2.10,16.5,z+d/2+.57),(1.22,1.65,.10));F.text('2',(x+2.10,16.5,z+d/2+.65),1.4,'h2-letter',back=True)
  F.text('SUITES BY HILTON',(x,15.55,z+d/2+.62),.25,'h2-letter',back=True)
 for x in [7.1,53.9]:F.box('h2-lime-paint',(x,10.85,22.43),(.5,14.3,.10))
 N=Frame(B,*F.p(0,0,16.3)[::2],YAW-math.pi/2,y=0)
 N.box('h2-gray-paint',(0,10.85,.36),(10.6,14.3,.20));N.text('HOME2',(0,16.4,.51),1.2,'h2-letter',back=True);N.text('SUITES BY HILTON',(0,15.5,.51),.25,'h2-letter',back=True)
 # Southeast end sign faces the arrival court as well as Dean Martin.
 S=Frame(B,*F.p(61.31,0,17.6)[::2],YAW+math.pi/2,y=0)
 S.box('h2-gray-paint',(0,10.8,.30),(8.8,14.4,.25))
 S.box('h2-lime-paint',(4.1,10.8,.45),(.45,14.4,.18))
 S.text('HOME2',(0,16.4,.60),.97,'h2-letter',back=True);S.text('SUITES BY HILTON',(0,15.6,.60),.22,'h2-letter',back=True)
 # Southeast entrance canopy from March 2020 Street View. No invented north entrance.
 E=Frame(B,*F.p(67.46,0,7.8)[::2],YAW+math.pi/2,y=0)
 E.box('h2-ochre-paint',(0,3.7,2.0),(9.9,.58,4.4));E.box('h2-soffit',(0,3.37,2),(9.6,.08,4.1))
 for u in [-4.5,4.5]:E.box('h2-stone',(u,1.8,3.6),(.55,3.6,.55),True)
 for u in [-1.49,1.49]:E.box('h2-frame-paint',(u,1.75,.05),(.11,3.0,.18))
 E.box('h2-frame-paint',(0,3.28,.05),(3.1,.12,.18))
 # Small landing is bounded within the observed canopy, not a rewrite of the shared drive.
 E.box('h2-paving',(0,.12,2.0),(9.5,.24,4.5),True)
 # Roof services: original generic mechanical housings inside parapet.
 for x in [12,24,38,51]:
  F.box('h2-metal',(x,18.0,10),(2.1,.9,1.6));F.box('h2-vent',(x,18.47,10),(1.8,.06,1.35))
  for z in np.arange(9.4,10.65,.16):F.box('h2-roof-metal',(x,18.51,float(z)),(1.8,.025,.045))
 from home2_pool import add_pool
 pool_routes=add_pool(B,F)
 room=F.poly([(46,3),(67.46,3),(67.46,13.25),(61.31,13.25),(61.31,19),(46,19)])
 B.planar('h2-floor',room,.24,True)
 B.property=KEY+'-interior';B.source='public/'+KEY
 B.shell(room,.24,3.38,'h2-interior',openings=doors,roof=False);B.planar('h2-ceiling',room,3.37)
 # Public-room arrangement is inferred; furniture character follows Hilton lobby photos.
 F.box('h2-wood',(59.7,.83,5.0),(4.3,1.18,.75),True);F.box('h2-counter',(59.7,1.45,5),(4.45,.10,.9))
 F.box('h2-screen',(59.1,1.72,5),(.62,.40,.06))
 F.box('h2-lime-paint',(59.7,.9,5.41),(3.6,.85,.04));F.text('WELCOME',(59.7,1.05,5.46),.25,'h2-letter',back=True)
 # Long banquette, mixed chairs and wood tables; preserve central circulation.
 F.box('h2-seat-fabric',(48.0,.66,11.0),(.84,.36,10),True);F.box('h2-seat-fabric',(47.63,1.12,11),(.17,1.05,10),True)
 for z in [7,9.5,12,14.5]:
  F.box('h2-blue-fabric',(47.95,1.0,z),(.23,.42,.62))
  F.box('h2-wood',(49.3,.99,z),(1.25,.09,.82),True);F.lathe('h2-metal',49.3,z,[(.24,.30),(.30,.30),(.31,.045),(.94,.045)],16)
  F.box('h2-green-fabric',(50.65,.69,z),(.57,.14,.58),True);F.box('h2-green-fabric',(50.93,1.04,z),(.10,.68,.60))
  for dx in [-.23,.23]:
   for dz in [-.22,.22]:F.tube('h2-metal',(50.65+dx,.24,z+dz),(50.65+dx,.64,z+dz),.024,6)
 # Breakfast serving cabinetry and communal table.
 F.box('h2-wood',(55.2,.78,17.9),(8.5,1.06,.88),True);F.box('h2-counter',(55.2,1.35,17.9),(8.65,.1,.98))
 for x in [52.2,54.1,57.3]:F.box('h2-metal',(x,1.75,17.9),(.65,.70,.58));F.box('h2-screen',(x,1.80,17.57),(.48,.42,.035))
 F.box('h2-wood',(56.0,1.0,13.7),(4,.10,1.15),True)
 for x in [54.5,57.5]:F.box('h2-metal',(x,.62,13.7),(.11,.75,.80),True)
 for x in [54.7,56,57.3]:
  for z in [12.7,14.7]:F.box('h2-chair-wood',(x,.66,z),(.58,.15,.58),True);F.box('h2-chair-wood',(x,1.01,z+(.24 if z>14 else -.24)),(.58,.65,.09))
 # Business desks and green cabinet at the back of the public room.
 F.box('h2-wood',(51.2,1.0,4.1),(6.1,.1,.75),True)
 for x in [49.3,52.8]:
  F.box('h2-screen',(x,1.44,4.12),(.65,.4,.05));F.box('h2-metal',(x,1.16,4.12),(.08,.2,.08));F.box('h2-metal',(x,1.07,4.44),(.5,.035,.18))
 F.box('h2-lime-paint',(46.45,1.52,5.2),(.6,2.56,2.6),True)
 for y in np.arange(.35,2.7,.14):F.box('h2-green-fabric',(46.78,float(y),5.2),(.035,.035,2.4))
 # Refrigerator/market built into the reception-side wall.
 F.box('h2-wood',(63.8,1.57,3.65),(2.6,2.66,.8),True)
 for x in [63.15,64.45]:
  F.box('h2-transom-glass',(x,1.6,4.08),(1.12,2.20,.055))
  for y in [.65,1.2,1.75,2.3]:
   F.box('h2-metal',(x,y,4.13),(1.05,.04,.04))
   for dx in [-.36,-.12,.12,.36]:F.box('h2-green-fabric',(x+dx,y+.15,4.15),(.10,.25,.08))
  F.box('h2-metal',(x+.42,1.55,4.21),(.035,.7,.04))
 for x in [54.7,56,57.3]:
  for z in [12.7,14.7]:
   for dx in [-.23,.23]:
    for dz in [-.22,.22]:F.tube('h2-metal',(x+dx,.24,z+dz),(x+dx,.60,z+dz),.024,6)
 for x,z in [(49.3,8),(49.3,12),(56,13.7)]:
  F.tube('h2-metal',(x,3.37,z),(x,2.85,z),.018,6)
  ring=[(x+.42*math.cos(a),2.67,z+.42*math.sin(a)) for a in np.linspace(0,math.tau,7)]
  F.path('h2-gold',ring,.035,6)
  for q in ring[:-1]:F.tube('h2-gold',q,(x,2.94,z),.025,6)
 from home2_public import add_details
 add_details(B,F)
 for x,z in [(51,10),(59,9),(54,16)]:F.light(x,3.05,z,power=22,range=12)
 routes=[dict(name='Arrival to reception',points=[F.p(x,.24,z) for x,z in [(70.5,7.8),(65,7.8),(60,7.8),(57,7.8)]]),dict(name='Public lounge and breakfast',points=[F.p(x,.24,z) for x,z in [(57,7.8),(52,7.8),(52,11),(52,16),(59.5,16),(59.5,10),(57,10)]]),dict(name='Business desk approach',points=[F.p(x,.24,z) for x,z in [(57,7.8),(53,7.8),(53,5.8),(49,5.8)]])]
 routes.extend(pool_routes)
 return dict(key=KEY,name='Home2 Suites Stadium District',center=[-813.7,0,1812.1],bounds=[-842,1769,-779,1845],structural=True,exteriorOnly=False,portals=doors,zones=[dict(origin=F.p(46,.24,3),yaw=YAW,width=21.46,depth=16,height=3.13)],lights=B.lights,routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
