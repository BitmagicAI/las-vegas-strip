"""Original Hampton exterior and photo-supported public rooms; dimensions inferred."""
from common import *
KEY='hampton-tropicana';IDS=['way/431504492','way/431504500'];YAW=-math.atan2(.777,.630)
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=Frame(B,-938.025,1787.902,YAW,y=0);p=footprint(IDS[0])
 doors=[dict(p=F.p(28,.32,0),yaw=F.yaw,width=3.2,height=3.05,name='Public lobby entrance',venue=KEY)]
 B.shell(p,.02,19.4,'ht-stucco',openings=doors,roof=False);B.planar('ht-roof',p,19.15)
 B.shell(p.buffer(.025,join_style=2),.02,3.6,'ht-brick',openings=doors,roof=False,solid=False)
 # Every long elevation receives recessed glazed bays, dark spandrels and projecting cornices.
 coords=list(p.exterior.coords)
 # Ring orientation: negative signed area here means exterior is on the local -z side.
 for a,b in zip(coords,coords[1:]):
  L=math.dist(a,b)
  if L<2.5:continue
  G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  mid=G.p(L/2,0,-.15);outside=not p.covers(Point(mid[0],mid[2]));sgn=-1 if outside else 1
  for yy,hh,dep in [(3.65,.22,.24),(16.5,.16,.17),(19.45,.28,.65),(19.72,.10,.86)]:G.box('ht-cream',(L/2,yy,0),(L+.03,hh,dep))
  bays=max(1,round(L/3.4));pitch=L/bays
  for i in range(bays):
   x=(i+.5)*pitch
   for floor in range(5):
    y=5.0+floor*2.88
    G.box('ht-recess',(x,y+.2,sgn*.055),(min(1.95,pitch-.35),2.48,.10))
    G.box('ht-glass',(x,y+.48,sgn*.12),(min(1.80,pitch-.48),1.78,.035))
    G.box('ht-spandrel',(x,y-.96,sgn*.13),(min(1.80,pitch-.48),1.08,.035))
    for xx in [x-.88,x,x+.88]:G.box('ht-metal',(xx,y+.48,sgn*.16),(.045,1.8,.045))
    G.box('ht-sill',(x,y-.43,sgn*.18),(1.98,.09,.18))
   # Low-level windows leave the real lobby doorway clear.
   q=G.p(x,0,0)
   if math.dist((q[0],q[2]),(doors[0]['p'][0],doors[0]['p'][2]))>3:
    G.box('ht-cream',(x,1.95,sgn*.075),(2.12,2.05,.16));G.box('ht-glass',(x,1.95,sgn*.17),(1.86,1.80,.04))
  # Relief joints, no coplanar decorative surfaces.
  for x in np.arange(.2,L,3.4):G.box('ht-joint',(x,11.7,sgn*.03),(.025,15.4,.025))
 def hip(G,x,z,w,d,base,rise):
  a=[(x-w/2,z-d/2),(x+w/2,z-d/2),(x+w/2,z+d/2),(x-w/2,z+d/2)]
  ridge=max(0,(d-w)/2)
  if d>w:
   r1=(x,z-ridge);r2=(x,z+ridge)
   faces=[[a[0],a[1],r1],[a[1],a[2],r2,r1],[a[2],a[3],r2],[a[3],a[0],r1,r2]]
  else:
   rr=max(0,(w-d)/2);r1=(x-rr,z);r2=(x+rr,z)
   faces=[[a[0],a[1],r2,r1],[a[1],a[2],r2],[a[2],a[3],r1,r2],[a[3],a[0],r1]]
  for face in faces:B.face('ht-green',[G.p(xx,base+(rise if (xx,zz) in [r1,r2] else 0),zz) for xx,zz in face])
 # Raised central sign pavilion and paired end pavilions on the arrival facade.
 for x,ww,h in [(5.5,8.0,20.1),(28,8.0,21.0),(50.5,8.0,20.1)]:
  F.box('ht-stucco-rose',(x,(h+3.7)/2,-.20),(ww,h-3.7,.35))
  for xx in [x-ww/2,x+ww/2]:F.box('ht-cream',(xx,(h+3.7)/2,-.43),(.25,h-3.7,.22))
  F.box('ht-cream',(x,h+.10,-.2),(ww+.7,.28,1.0));F.box('ht-cream',(x,h+.34,-.2),(ww+1.0,.12,1.3))
  hip(F,x,2.3,ww+1.2,6.2,h+.42,1.2)
  if x!=28:
   for floor in range(5):
    yy=5.5+floor*2.88
    for xx in [x-1.9,x+1.9]:
     F.box('ht-recess',(xx,yy,-.43),(1.8,2.2,.12));F.box('ht-glass',(xx,yy+.2,-.51),(1.62,1.58,.035));F.box('ht-spandrel',(xx,yy-.80,-.52),(1.62,.30,.035))
  else:
   # Paired window strips flank the central sign panel in the official facade photo.
   for xx in [x-3.0,x+3.0]:
    for floor in range(5):
     yy=5.5+floor*2.88
     F.box('ht-recess',(xx,yy,-.43),(1.0,2.70,.12));F.box('ht-glass',(xx,yy+.2,-.51),(.88,1.58,.035));F.box('ht-spandrel',(xx,yy-.92,-.52),(.88,.60,.035))
     F.box('ht-metal',(xx,yy+.2,-.55),(.035,1.58,.035))
   F.text('Hampton',(x,18.3,-.45),1.12,'ht-red');F.text('Inn',(x,17.0,-.45),1.05,'ht-red')
   B.arc('ht-cream',F.p(x,13.4,-.47),.68,yaw=F.yaw,thick=.09,n=24)
 # Entrance canopy, cream cornice, green hip roof and open drive beneath.
 F.box('ht-cream',(28.2,4.25,-12.4),(10.0,.48,15.0));F.box('ht-sill',(28.2,4.56,-12.4),(10.5,.14,15.5))
 hip(F,28.2,-12.4,10.6,15.6,4.65,2.35)
 F.box('ht-cream',(28,4.25,-2.5),(6.5,.48,5.5))
 for x in [24.0,32.4]:
  for z in [-18.7,-6.1]:
   F.box('ht-stone',(x,1.96,z),(.78,3.95,.78),True);F.box('ht-cream',(x,3.95,z),(1.2,.35,1.2));F.box('ht-stone',(x,.42,z),(1.2,.84,1.2),True)
 F.text('Welcome',(28.2,4.22,-19.94),.46,'ht-metal')
 # Supported entry apron and real doorway aperture, with side glazing.
 F.box('ht-paving',(28,.20,-10.1),(6,.24,20.2),True)
 for x in [26.35,29.65]:F.box('ht-metal',(x,1.90,-.09),(.10,3.2,.20))
 F.box('ht-metal',(28,3.51,-.09),(3.4,.10,.20))
 for x in [24.3,31.7]:F.box('ht-glass',(x,1.95,-.14),(2.6,2.55,.05))
 # Courtyard pool/deck bounded by the mapped wings; pool shape inferred from official image7.
 deck=F.poly([(19.1,36),(37,36),(37,70.5),(19.1,70.5)])
 # Smooth asymmetrical kidney outline, inferred from Hilton outdoor-pool photograph.
 controls=np.array([(25.0,43),(29.9,43.5),(32.0,47),(30.7,51),(31.8,57),(29.3,61),(25.6,61.4),(23.7,58.5),(25.0,53),(23.5,48)],float)
 ring=[]
 for i in range(len(controls)):
  a,b,c,d=[controls[j%len(controls)] for j in [i-1,i,i+1,i+2]]
  for t in np.linspace(0,1,12,endpoint=False):ring.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
 pool=Polygon(ring)
 poolworld=F.poly(list(pool.exterior.coords))
 B.planar('ht-paving',deck.difference(poolworld.buffer(.45)),.25,True)
 B.planar('ht-stone',poolworld.buffer(.45).difference(poolworld),.33,True)
 B.shell(poolworld,-1.2,.32,'ht-pool-tile',roof=False,solid=True)
 B.planar('hampton_pool',poolworld,.08)
 B.planar('ht-pool-tile',poolworld,-1.2,True)
 for x in [21.2,34.9]:
  for z in [41,46,51,56,61,66]:
   if x>30 and z in [46,51]:continue
   F.box('ht-wood',(x,.47,z),(.73,.12,1.95));F.box('ht-blue',(x,.57,z),(.69,.08,1.80))
   for zz in [z-.65,z+.65]:F.box('ht-wood',(x,.34,zz),(.68,.26,.08))
   B.face('ht-blue',[F.p(x-.34,.61,z+.50),F.p(x+.34,.61,z+.50),F.p(x+.34,1.1,z+.95),F.p(x-.34,1.1,z+.95)])
 for z in [38,68]:
  for x in [21,35]:F.lathe('ht-stone',x,z,[(.25,.60),(.9,.48)],16)
 # Rock feature at the head of the basin. Original irregular boulders, no photo textures.
 rng=random.Random(276)
 for row,yy,count in [(0,.80,4),(1,1.70,4),(2,2.55,3)]:
  for i in range(count):
   zz=48+(i-(count-1)/2)*1.25
   F.box('ht-rock',(32.65+rng.uniform(-.12,.12),yy,zz),(1.9-rng.random()*.20,.95,1.48))
 # Hidden inside the bottom rock tier; one collision volume for the substantial feature.
 F.box('ht-rock',(32.65,.85,48),(1.3,1.1,4.9),True)
 # Landscaped boundary beds and fan palms. Tree positions/heights are estimated.
 from courtyard_525 import palm
 for x in [20.0,36.2]:
  F.box('ht-soil',(x,.37,54.5),(1.05,.24,28),True)
  for j,z in enumerate([40.7,48,56,64.5]):
   h=7.5+(j%3)*1.1;palm(B,F,x,z,h)
   for yy in np.arange(.3,h,.18):F.lathe('c525-bark',x,z,[(float(yy),.23),(float(yy)+.06,.26),(float(yy)+.12,.22)],12)
  for z in np.arange(41,68,.7):
   for j in range(3):
    px=x+rng.uniform(-.35,.35);pz=float(z)+rng.uniform(-.25,.25)
    B.sphere('ht-shrub',F.p(px,.8+rng.random()*.25,pz),.40,8,5,scale=(1,.9,1))
 # Photo-supported public lobby; private hotel circulation remains closed.
 room=F.poly([(17,.12),(39,.12),(39,16),(17,16)])
 B.planar('ht-floor',room,.32,True)
 B.property=KEY+'-interior';B.source='public/'+KEY
 B.shell(room,.32,4.0,'ht-interior',openings=doors,roof=False);B.planar('ht-ceiling',room,3.98)
 F.box('ht-wood',(24,3.96,6.4),(10,.05,7.2))
 # Two reception counters at the right, framing a clear central arrival route.
 for z in [5.2,11.0]:
  F.box('ht-cream',(37.2,.99,z),(1.1,1.34,3.8),True);F.box('ht-wood',(36.62,1.00,z),(.055,1.12,3.6))
  F.box('ht-cream',(36.58,1.07,z),(.06,.06,3.68));F.box('ht-stone',(37.2,1.69,z),(1.25,.10,3.96))
  F.box('ht-metal',(37.0,1.76,z),(.35,.07,.40));F.box('ht-metal',(37.0,1.98,z),(.08,.4,.08));F.box('ht-screen',(36.98,2.15,z),(.10,.40,.55))
  F.box('ht-metal',(38.83,2.6,z),(.07,1.5,2.1));F.box('ht-cream',(38.78,2.6,z),(.04,1.35,1.95))
  for dz in [-.6,0,.6]:F.box('ht-blue',(38.74,2.6,z+dz),(.015,.88,.3))
 for z in [2.0,8.1,14.6]:F.box('ht-cream',(38.65,2.15,z),(.6,3.7,.6))
 # Lounge suite from official lobby image, with ring chandelier.
 F.box('ht-carpet',(23,.335,6.1),(8,.02,7))
 for x,z,yaw in [(20.2,4.1,0),(25.5,4.1,0),(20.2,8.4,math.pi),(25.5,8.4,math.pi)]:
  q=F.p(x,0,z);G=Frame(B,q[0],q[2],F.yaw+yaw,y=0)
  G.box('ht-upholstery',(0,.87,0),(.88,.20,.82),True);G.box('ht-upholstery',(0,1.20,.35),(.90,.70,.16),True)
  for xx in [-.37,.37]:
   G.box('ht-upholstery',(xx,1.04,0),(.16,.20,.78))
   for zz in [-.29,.29]:G.tube('ht-wood',(xx,.34,zz),(xx*.88,.79,zz*.88),.035,10,r2=.045)
 F.box('ht-wood',(23,1.0,6.1),(2.2,.16,1.4),True);F.box('ht-wood',(23,.62,6.1),(1.0,.76,.65))
 for x in [20,26]:F.lathe('ht-green',x,6.1,[(.33,.35),(.45,.46),(.92,.18),(1.15,.45),(1.20,.46)],20)
 ring=[F.p(23+1.45*math.cos(a),3.05,6.1+1.45*math.sin(a)) for a in np.linspace(0,math.tau,49)];B.path('ht-metal',ring,.07,8)
 for a in np.linspace(0,math.tau,32,endpoint=False):
  x=23+1.45*math.cos(a);z=6.1+1.45*math.sin(a);F.tube('ht-metal',(x,3.05,z),(x,3.58,z),.025,6);F.lathe('ht-light',x,z,[(2.98,.055),(3.07,.055)],8)
 # Breakfast nook behind lounge: magenta wall, buffet and mustard seating.
 F.box('ht-magenta',(23.4,2.16,15.85),(12.6,3.65,.10))
 for x in [19.5,23.7,28.0]:
  F.box('ht-stone',(x,1.12,12.5),(1.65,.10,1.0),True);F.box('ht-wood',(x,.72,12.5),(.20,.72,.20))
  for zz in [11.55,13.45]:
   F.box('ht-mustard',(x,.87,zz),(.65,.18,.62),True);F.box('ht-mustard',(x,1.18,zz+(.27 if zz>12.5 else -.27)),(.65,.65,.12))
   for dx in [-.25,.25]:F.tube('ht-wood',(x+dx,.33,zz),(x+dx,.80,zz),.035,8)
 F.box('ht-cream',(32.8,.88,13.5),(3.6,1.1,1.0),True);F.box('ht-stone',(32.8,1.47,13.5),(3.8,.12,1.15))
 for x in [31.6,33.7]:F.box('ht-metal',(x,1.9,13.5),(.65,.78,.5));F.box('ht-screen',(x,2.0,13.23),(.5,.32,.04))
 for x,z in [(23,6),(32,9)]:F.light(x,3.6,z,power=24,range=15)
 routes=[dict(name='Arrival and public lobby',points=[F.p(x,.32,z) for x,z in [(28,-18),(28,1.5),(30,3),(30,9),(30,14.5),(28,14.5)]]),dict(name='Lounge access',points=[F.p(x,.32,z) for x,z in [(28,3),(23,2.0),(18.2,2),(18.2,9.7),(27,9.7)]])]
 routes.append(dict(name='Courtyard pool circuit',points=[F.p(x,.25,z) for x,z in [(22,38.5),(34.6,38.5),(34.6,53),(33.5,54),(33.5,64),(22,64),(22,38.5)]]))
 return dict(key=KEY,name='Hampton Inn Tropicana',center=[-944,0,1825],bounds=[-997,1773,-887,1864],structural=True,exteriorOnly=False,portals=doors,zones=[dict(origin=F.p(28,.32,.12),yaw=F.yaw,width=22,depth=15.88,height=3.68)],lights=B.lights,routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
