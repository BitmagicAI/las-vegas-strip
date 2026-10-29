"""Original site reconstruction; measured footprint, fitted heights and inferred counter room."""
from common import *
KEY='in-n-out-sahara';IDS=['way/276426443']
def build(B):
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0;p=footprint(IDS[0]);Q=Frame(B,0,0,0,y=0)
 R=Frame(B,-682.78,-3195.08,math.pi,y=0)
 opening=dict(p=R.p(0,.22,0),yaw=R.yaw,width=4.6,height=3.5)
 door=dict(p=R.p(0,.22,0),yaw=R.yaw,width=1.9,height=2.9,name='In-N-Out public counter',venue=KEY)
 B.shell(p,.02,4.7,'ino-white',roof=False,openings=[opening]);B.planar('ino-membrane',p,4.7)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  for y,h,d in [(4.72,.16,.30),(4.5,.10,.22)]:F.box('ino-white',(0,y,0),(L+.05,h,d))
  if F.z>-3196:continue
  for side in [-1,1]:
   F.box('ino-stone',(0,.38,side*.08),(L,.76,.12))
  if L<4:continue
  front=F.x>-678 or F.z>-3198
  if front:
   for u in np.linspace(-L/2+1.7,L/2-1.7,max(1,int(L/3.4))):
    for side in [-1,1]:
     F.box('ino-glass',(float(u),2.1,side*.15),(2.7,2.5,.05))
     for x in [-1.4,0,1.4]:F.box('ino-metal',(float(u+x),2.1,side*.20),(.055,2.6,.055))
     for y in [.8,3.4]:F.box('ino-metal',(float(u),y,side*.20),(2.85,.06,.05))
 # Tiled entry roofs, one at south entrance and one on east elevation.
 def roof(cx,cz,w,d,y):
  pts=[(cx-w/2,y,cz-d/2),(cx+w/2,y,cz-d/2),(cx+w/2,y,cz+d/2),(cx-w/2,y,cz+d/2)]
  apex=(cx,y+1.25,cz)
  for i in range(4):B.face('ino-tile',[pts[i],pts[(i+1)%4],apex])
  for t in np.arange(.15,1,.13):
   for i in range(4):
    a=tuple(apex[j]+(pts[i][j]-apex[j])*float(t) for j in range(3));b=tuple(apex[j]+(pts[(i+1)%4][j]-apex[j])*float(t) for j in range(3));B.path('ino-tile-edge',[a,b],.035,6)
  for i in range(4):B.path('ino-tile-edge',[pts[i],apex],.065,8)
 def tower(F,w,d):
  F.box('ino-white',(0,5.45,d/2),(w,1.5,d))
  for y in [6.16,6.3]:F.box('ino-white',(0,y,d/2),(w+.25,.12,d+.25))
  x,_,z=F.p(0,0,d/2);roof(x,z,w+.5,d+.5,6.4)
  F.text('IN-N-OUT',(0,5.0,-.20),.38,'ino-red')
  # Original arrow silhouette.
  F.box('ino-yellow',(-.35,5.5,-.12),(1.4,.18,.10));B.face('ino-yellow',[F.p(.3,5.75,-.18),F.p(1.05,5.5,-.18),F.p(.3,5.25,-.18)])
 tower(R,4.8,3.8)
 E=Frame(B,-675.13,-3207.0,-math.pi/2,y=0);tower(E,4.2,3.8)
 # South entrance glazing and ramp.
 for u in [-1.65,1.65]:R.box('ino-clear',(u,1.95,0),(1.35,3.25,.05),True)
 for u in [-2.3,-.95,.95,2.3]:R.box('ino-metal',(u,1.95,0),(.07,3.4,.12),True)
 R.box('ino-metal',(0,3.65,0),(4.65,.09,.12));R.text('2900',(0,3.88,-.1),.22,'ino-red')
 B.upface('ino-paving',[R.p(-1.15,.01,-3),R.p(1.15,.01,-3),R.p(1.15,.22,.2),R.p(-1.15,.22,.2)],True)
 def awning(F,w):
  B.face('ino-red',[F.p(-w/2,3.8,0),F.p(w/2,3.8,0),F.p(w/2,3.15,-1.15),F.p(-w/2,3.15,-1.15)])
  F.box('ino-white',(0,3.03,-1.15),(w,.24,.07))
  for y in [2.92,3.13]:F.box('ino-red',(0,y,-1.20),(w,.025,.025))
  for u in np.arange(-w/2+.2,w/2,.32):F.box('ino-red',(float(u),3.02,-1.20),(.04,.12,.025))
 awning(Frame(B,-687.0,-3197.1,math.pi,y=0),3.4)
 awning(Frame(B,-678.2,-3197.18,math.pi,y=0),3.4)
 for z in [-3201,-3214]:awning(Frame(B,-675.8,z,-math.pi/2,y=0),4.3)
 # Drive-through west pickup and north service door.
 W=Frame(B,-689.25,-3208,math.pi/2,y=0)
 W.box('ino-glass',(0,2,-.16),(2.6,1.5,.06));W.box('ino-metal',(0,1.22,-.28),(2.8,.12,.45))
 for u in [-1.32,0,1.32]:W.box('ino-metal',(u,2,-.21),(.05,1.6,.05))
 awning(W,3.0)
 Q.box('ino-service',(-682.4,1.4,-3220.9),(1.15,2.8,.08))
 for z in [-3212,-3217]:
  Q.box('ino-service',(-683,5.05,z),(2.8,.7,2.1))
  for x in np.arange(-684.1,-681.9,.2):Q.box('ino-metal',(float(x),5.42,z),(.035,.03,1.8))
 # Two photographed east patio tables; position and furniture dimensions fitted.
 for z in [-3201,-3214]:
  Q.box('ino-metal',(-672.8,.48,z),(.14,.8,.14))
  Q.box('ino-counter',(-672.8,.92,z),(1.3,.10,.8),True)
  for dz in [-.8,.8]:
   Q.box('ino-stone',(-672.8,.5,z+dz),(1.3,.13,.4),True)
   for x in [-673.25,-672.35]:Q.box('ino-metal',(x,.25,z+dz),(.1,.43,.25))
 # Public counter room occupies the southern dining volume; no private kitchen.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 # Narrow vestibule joins wider counter room without touching exterior side walls.
 room=R.poly([(-2.3,0),(2.3,0),(2.3,2.3),(5.6,2.3),(5.6,11.3),(-5.6,11.3),(-5.6,2.3),(-2.3,2.3)])
 B.shell(room,.22,3.8,'ino-white',roof=False,openings=[opening]);B.planar('ino-floor',room,.22,True);B.planar('ino-ceiling',room,3.8)
 for u in np.arange(-5.5,5.6,.5):R.box('ino-grout',(float(u),.225,6.8),(.012,.008,9))
 for v in np.arange(2.4,11.3,.5):R.box('ino-grout',(0,.225,float(v)),(11.1,.008,.012))
 # Tile grids and palm band are original geometry, not copied photographic textures.
 for side in [-1,1]:
  for y in np.arange(.25,3.8,.25):R.box('ino-grout',(side*5.57,float(y),6.8),(.015,.008,8.9))
  for v in np.arange(2.4,11.3,.25):R.box('ino-grout',(side*5.57,2.0,float(v)),(.015,3.5,.008))
  for y in [1.6,1.88]:R.box('ino-red',(side*5.54,y,6.8),(.02,.025,8.8))
 # Angular front counter with open public queue in front.
 R.box('ino-white',(0,.76,9.0),(8.3,1.08,.95),True);R.box('ino-counter',(0,1.33,9.0),(8.5,.10,1.1),True)
 for u in np.arange(-4.1,4.11,.25):R.box('ino-grout',(float(u),.76,8.51),(.01,1.06,.01))
 for y in np.arange(.25,1.31,.25):R.box('ino-grout',(0,float(y),8.51),(8.25,.009,.01))
 for y in [.64,.93]:R.box('ino-red',(0,y,8.49),(8.2,.025,.02))
 for u in np.arange(-3.9,4.0,.36):
  R.path('ino-red',[(float(u),.67,8.47),(float(u+.03),.81,8.47)],.012,5)
  for du,dy in [(-.08,-.02),(-.06,.05),(0,.08),(.07,.05),(.09,-.02)]:R.tube('ino-red',(float(u+.03),.81,8.47),(float(u+.03+du),.81+dy,8.47),.012,5)
 for u in [-2.8,0,2.8]:
  R.box('ino-metal',(u,1.48,9.0),(.08,.26,.08));R.box('ino-frame',(u,1.67,9.0),(.48,.34,.06))
 R.box('ino-white',(0,3.28,9.25),(8.7,1.04,1.6));R.box('ino-red',(-1.7,3.25,8.38),(3.8,.88,.06))
 for u in [-.5,-1.7,-2.9]:
  R.box('ino-menu',(u,3.25,8.33),(1.1,.77,.035))
  for y in [3.05,3.18,3.31,3.44]:R.box('ino-red',(u,y,8.30),(.72,.018,.015))
 R.text('Quality',(2.4,3.3,8.35),.34,'ino-yellow');R.text('you can taste',(2.4,2.98,8.35),.22,'ino-yellow')
 for u in [-3,0,3]:
  for v in [3.5,6.5]:R.lathe('ino-lamp',u,v,[(3.765,0),(3.765,.12),(3.79,.14),(3.79,0)],16)
 routes=[dict(name='Entry to public counter and return',points=[R.p(0,.22,v) for v in [-5,-2,1,3.5,6,7.8]]),dict(name='West pickup frontage',points=[[-694,.24,-3192],[-694,.24,-3206],[-694,.24,-3223]])]
 return dict(key=KEY,name='In-N-Out West Sahara',center=[-683,0,-3208],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.22,0),yaw=R.yaw,width=11.3,depth=11.4,height=3.9)],lights=[dict(p=R.p(u,3.4,v),color=0xfff2d9,power=3,range=6) for u,v in [(-3,4),(3,4),(-3,8),(3,8)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
