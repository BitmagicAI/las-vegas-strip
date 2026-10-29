"""Original photo-supported public envelope and waiting space. Layout inferred."""
from common import *
from shapely.geometry.polygon import orient
KEY='sahara-surgery'
def build(B):
 p=orient(footprint('way/1062820474'),sign=1);F=Frame(B,-358.9,-3303.4,math.pi/2,y=0)
 B.property=KEY+'-exterior';B.source='clinic/'+KEY;B.detail=0
 door=dict(p=F.p(0,.15,0),yaw=F.yaw,width=2.4,height=2.8,name='Public waiting entry',venue=KEY)
 wins=[dict(p=F.p(u,.35,0),yaw=F.yaw,width=2.25,height=2.6)for u in [-5.9,-3,3,5.9]]
 a,b=(-365.147,-3319.135),(-355.687,-3328.431);L=math.dist(a,b);N=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
 # Outward front normal depends on ring direction; this edge faces northwest.
 if N.p(0,0,-1)[0]>N.x:N=Frame(B,N.x,N.z,N.yaw+math.pi,y=0)
 narrow=[dict(p=N.p(u,.55,0),yaw=N.yaw,width=.58,height=2.4)for u in [-4.8,-3.2,-1.6,0,1.6,3.2,4.8]]
 tower=p.intersection(box(-370,-3335,-349,-3313))
 B.shell(p.difference(tower),0,5.25,'ssc-stucco',openings=[door,*wins],roof=False);B.planar('ssc-membrane',p.difference(tower),5.23)
 B.shell(tower,0,7.5,'ssc-block',openings=narrow,roof=False);B.planar('ssc-membrane',tower,7.48)
 for R,entries in [(F,wins),(N,narrow)]:
  for o in entries:
   pt=o['p'];u=(pt[0]-R.x)*R.co-(pt[2]-R.z)*R.si;w=o['width'];y=pt[1];h=o['height']
   R.box('ssc-clear'if R==F else'ssc-glass',(u,y+h/2,.1),(w,h,.025),True)
   for du in [-w/2,w/2]:R.box('ssc-alloy',(u+du,y+h/2,.03),(.05,h+.15,.15))
   for yy in [y,y+.8,y+h]:R.box('ssc-alloy',(u,yy,.03),(w,.05,.15))
 for u in [-.6,.6]:
  F.box('ssc-clear',(u,1.55,.03),(1.15,2.75,.025))
  for du in [-.58,.58]:F.box('ssc-alloy',(u+du,1.55,-.05),(.045,2.8,.1))
  for yy in [.15,1.1,2.95]:F.box('ssc-alloy',(u,yy,-.05),(1.2,.045,.1))
  F.tube('ssc-alloy',(u*.3,1.1,-.13),(u*.3,1.65,-.13),.025,10)
 # Fine square masonry joints on solid tall diagonal wall, excluded around narrow openings.
 for row,yy in enumerate(np.arange(.4,7.45,.4)):
  spans=[(-L/2,L/2)]if yy>3.1 else[(-6.6,-5.15),(-4.45,-3.55),(-2.85,-1.95),(-1.25,-.35),(.35,1.25),(1.95,2.85),(3.55,4.45),(5.15,6.6)]
  for lo,hi in spans:N.box('ssc-joint',((lo+hi)/2,float(yy),-.026),(hi-lo,.009,.015))
  if yy>3.1:
   for u in np.arange(-6.5,6.6,.4):N.box('ssc-joint',(float(u),float(yy)+.19,-.026),(.009,.38,.015))
 for poly,h in [(p,5.3),(tower,7.55)]:
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   if h<6 and tower.buffer(.01).covers(Point((a[0]+b[0])/2,(a[1]+b[1])/2)):continue
   R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0);R.box('ssc-coping',(0,h,0),(math.dist(a,b)+.03,.13,.28))
 # Covered drop-off with real overhead clearance and two round columns.
 F.box('ssc-white',(0,4.15,-3.6),(17.2,.65,7.2),True);F.box('ssc-coping',(0,4.52,-3.6),(17.4,.12,7.4));F.box('ssc-soffit',(0,3.8,-3.6),(17,.04,7))
 for u in [-7.6,7.6]:F.lathe('ssc-white',u,-6.4,[(0,.48),(.16,.5),(.25,.39),(3.75,.39),(3.83,.48)],24)
 F.text('Sahara Surgery Center',(0,4.03,-7.26),.42,'ssc-letter')
 for u in [-6,-3,0,3,6]:F.lathe('ssc-lamp',u,-3.7,[(3.76,.1),(3.79,.1)],12)
 F.box('ssc-paving',(0,.075,-2),(16,.15,4),True)
 B.upface('ssc-paving',[F.p(-1.5,0,-5),F.p(1.5,0,-5),F.p(1.5,.15,-3),F.p(-1.5,.15,-3)],True)
 for u in [-6,-3,3,6]:F.tube('ssc-alloy',(u,.15,-2.4),(u,1.05,-2.4),.065,12)
 # Roof equipment and service wing details preserve irregular mapped footprint.
 for x,z in [(-345,-3305),(-338,-3305),(-331,-3305)]:
  B.box('ssc-curb',(x,5.4,z),(2.8,.3,5));B.box('ssc-equipment',(x,6,z),(2.4,.9,4.5))
  for dz in [-1.3,0,1.3]:B.lathe('ssc-dark',(x,z+dz),[(6.46,.55),(6.5,.55)],16)
  for dz in np.arange(-1.8,1.9,.25):B.box('ssc-alloy',(x+1.22,5.95,z+float(dz)),(.03,.45,.08))
 for x,z in [(-316,-3298),(-325,-3331),(-337,-3282)]:
  B.box('ssc-service',(x,1.3,z),(1.2,2.6,.1),True)
 # Local planting only; no parking or roads regenerated.
 for u,v in [(11,-4),(-11,-4),(13,0),(-13,0)]:
  F.box('ssc-gravel',(u,.025,v),(3,.05,3))
  for j in range(5):B.sphere('ssc-leaf',F.p(u+.55*math.cos(j*2),.6,v+.55*math.sin(j*2)),.5,10,6)
 for u,v,h in [(12,-6,9),(-12,-6,10)]:
  F.tube('ssc-trunk',(u,0,v),(u+.3,h,v+.2),.18,10)
  for j in range(9):
   a=j*math.tau/9;pts=[]
   for k in range(5):
    r=k*.7;pts.append((u+.3+r*math.cos(a),h+.5*math.sin(k*.8)-k*.14,v+.2+r*math.sin(a)))
   F.path('ssc-leaf',pts,.035,6)
   for k in range(1,5):
    x,y,z=pts[k];side=.45*(1-k/6);leaf=[F.p(x,y,z),F.p(x+side*math.cos(a+1.2),y-.3,z+side*math.sin(a+1.2)),F.p(x+.45*math.cos(a),y-.1,z+.45*math.sin(a)),F.p(x+side*math.cos(a-1.2),y-.3,z+side*math.sin(a-1.2))];B.face('ssc-leaf',leaf);B.face('ssc-leaf',list(reversed(leaf)))
 # Public waiting room only, inferred dimensions. Reception rear remains private/closed.
 B.property=KEY+'-interior';B.source='public/'+KEY
 room=Polygon([(F.p(u,0,v)[0],F.p(u,0,v)[2])for u,v in [(-8,.2),(8,.2),(8,15),(-8,15)]])
 B.planar('ssc-carpet',room,.15,True);B.shell(room,.15,3.6,'ssc-cream',openings=[door,*wins],roof=False,solid=True)
 for t in triangles(room):
  pts=[(x,3.6,z)for x,z in list(t.exterior.coords)[:-1]];ar=np.array(pts);B.face('ssc-ceiling',pts if np.cross(ar[1]-ar[0],ar[2]-ar[0])[1]<0 else list(reversed(pts)))
 # Ceiling border and suspended linear light strips.
 for u in [-7,7]:F.box('ssc-white',(u,3.35,7.6),(2,.45,14.6))
 for v in [1.2,14]:F.box('ssc-white',(0,3.35,v),(12,.45,2))
 for v in [3.2,6.5,9.8,12.7]:
  F.box('ssc-alloy',(0,3.3,v),(10,.12,.18));F.box('ssc-lamp',(0,3.23,v),(9.8,.025,.14))
  for u in [-4,4]:F.tube('ssc-alloy',(u,3.35,v),(u,3.6,v),.012,8)
 for u in np.arange(-7.5,8,.6):F.box('ssc-floorjoint',(float(u),.155,7.6),(.006,.006,14.6))
 for v in np.arange(.6,15,.6):F.box('ssc-floorjoint',(0,.155,float(v)),(16,.006,.006))
 def chair(u,v,yaw0,mat):
  C=Frame(B,*[F.p(u,0,v)[i]for i in [0,2]],F.yaw+yaw0,y=.15)
  C.box(mat,(0,.46,0),(.55,.1,.55),True);C.box(mat,(0,.86,.24),(.55,.65,.08),True)
  for side in [-1,1]:
   C.path('ssc-alloy',[(side*.32,0,-.22),(side*.32,.72,-.22),(side*.32,.78,-.1),(side*.32,.78,.2),(side*.32,0,.27)],.026,10)
 for row,v in enumerate([3.5,6.5,9.5]):
  for j,u in enumerate([-6,-4.8,-3.6,3.6,4.8,6]):chair(u,v,0 if row%2 else math.pi,['ssc-seatgray','ssc-seatpurple','ssc-seatbeige'][(row+j)%3])
 for u in [-5.4,5.4]:
  for v in [4.9,8]:
   F.box('ssc-table',(u,.65,v),(.7,.06,.7),True)
   for xx in [-.28,.28]:
    for zz in [-.28,.28]:F.tube('ssc-alloy',(u+xx,.15,v+zz),(u+xx,.63,v+zz),.02,8)
   F.lathe('ssc-pot',u,v,[(.69,.12),(.94,.16)],14)
   for j in range(4):B.sphere('ssc-leaf',F.p(u+.12*math.cos(j*2),1.06,v+.12*math.sin(j*2)),.17,8,5)
 # Public reception counter, cabinets and inactive screens, no patient content.
 F.box('ssc-cabinet',(-5,.7,13.2),(5.5,1.1,1),True);F.box('ssc-table',(-5,1.3,13.2),(5.6,.1,1.1))
 for u in [-7,-5.6,-4.2,-2.8]:
  F.box('ssc-cabinet',(u,.72,12.68),(1.32,1.06,.04));F.box('ssc-alloy',(u+.48,1,12.63),(.08,.035,.04))
 for u in [-6,-3.5]:
  F.box('ssc-dark',(u,1.62,13.25),(.6,.4,.06));F.box('ssc-alloy',(u,1.43,13.25),(.06,.2,.06));F.box('ssc-dark',(u,1.38,13.25),(.3,.04,.2))
 F.box('ssc-white',(-5,2.9,13.2),(5.7,.35,1.2));F.text('RECEPTION',(-5,2.05,14.87),.22,'ssc-letter')
 F.box('ssc-dark',(0,3.01,.26),(1,.24,.04));F.text('EXIT',(0,2.93,.3),.18,'ssc-red',True)
 routes=[dict(name='Entrance and waiting aisle',points=[F.p(0,y,v)for v,y in [(-9,0),(-5,0),(-3,.15),(1,.15),(6,.15),(11,.15)]]),dict(name='Reception approach',points=[F.p(u,.15,v)for u,v in [(0,11),(0,11.8),(-3,11.8),(-5,11.8)]])]
 return dict(key=KEY,name='Sahara Surgery Center',center=[-341,0,-3308],bounds=list(p.buffer(8).bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(0,.15,.2),yaw=F.yaw,width=16,depth=14.8,height=3.5)],lights=[dict(p=F.p(u,3,v),color=0xfff5e7,power=3.5,range=10)for u,v in [(-4,4),(4,4),(-4,11),(4,11)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
