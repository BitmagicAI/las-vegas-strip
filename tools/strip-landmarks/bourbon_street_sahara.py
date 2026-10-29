"""Original reference-fitted exterior/public billiards room; dimensions and room plan inferred."""
from common import *
KEY='bourbon-street-sahara';IDS=['way/276426298']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 R=Frame(B,-262.2,-3198,math.pi/2,y=0)
 door=dict(p=R.p(0,.15,.08),yaw=R.yaw,width=2.2,height=2.8,name='Bourbon Street public entrance',venue=KEY)
 tower=box(-262.7,-3217,-252,-3207)
 B.shell(p.difference(tower),0,6.1,'bs-stucco',roof=False,openings=[dict(p=door['p'],width=2.4,height=3)])
 B.planar('bs-membrane',p.difference(tower),6.12)
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  B.tube('bs-cornice',(a[0],6.18,a[1]),(b[0],6.18,b[1]),.13,6)
 for x,z in [(-239,-3218),(-242,-3211),(-240,-3201),(-242,-3190),(-247,-3183)]:
  B.box('bs-service',(x,6.5,z),(1.7,.7,1.4));B.box('bs-dark',(x,6.88,z),(1.25,.06,1.0))
 # West portico and grey timber cladding; individual raised boards stay off the shell.
 for u,w in [(-5.5,8.6),(5.5,8.6)]:
  for y in np.arange(.3,4.5,.19):R.box('bs-board'+str(int(y*10)%3),(u,float(y),-.07),(w,.17,.055))
 R.box('bs-wood',(0,5.38,-.12),(20,.8,.13));R.box('bs-cornice',(0,5.9,-.18),(20,.18,.22))
 B.upface('bs-canopy',[R.p(-10,3.5,-3.8),R.p(10,3.5,-3.8),R.p(10,4.6,-.2),R.p(-10,4.6,-.2)])
 for u in np.arange(-9.9,10,.23):R.tube('bs-alloy',(float(u),3.54,-3.8),(float(u),4.64,-.2),.022,5)
 R.box('bs-wood',(0,3.45,-3.85),(20.4,.23,.25))
 for u in [-9,-5,5,9]:
  R.box('bs-brick',(u,.65,-3.4),(.68,1.3,.68),True)
  # Tapered square cream column, visually distinct from masonry plinth.
  for side in range(4):
   a=side*math.pi/2+math.pi/4;b=a+math.pi/2
   B.face('bs-stucco',[R.p(u+.26*math.cos(a),1.3,-3.4+.26*math.sin(a)),R.p(u+.26*math.cos(b),1.3,-3.4+.26*math.sin(b)),R.p(u+.17*math.cos(b),3.5,-3.4+.17*math.sin(b)),R.p(u+.17*math.cos(a),3.5,-3.4+.17*math.sin(a))])
  for y in np.arange(.15,1.3,.16):R.box('bs-mortar',(u,float(y),-3.75),(.69,.025,.015))
 R.floor(20,3.4,-1.7,'bs-paving',.15)
 B.upface('bs-paving',[R.p(-1.4,0,-5),R.p(1.4,0,-5),R.p(1.4,.15,-3.4),R.p(-1.4,.15,-3.4)],True)
 for a,b in [(-9,-1.5),(1.5,9)]:
  for y in [.4,1.05]:R.tube('bs-dark',(a,y,-3.4),(b,y,-3.4),.035,6)
  for u in np.arange(a,b,.5):R.tube('bs-dark',(float(u),.15,-3.4),(float(u),1.05,-3.4),.025,5)
 def sign(F,u,y,v,width=8):
  F.box('bs-dark',(u,y,v),(width,1.25,.14));F.box('bs-letter',(u,y-.9,v),(width,.55,.14))
  F.text('Bourbon Street',(u,y-.23,v-.09),width/10,'bs-letter')
  F.text('SPORTS BAR',(u,y-1.05,v-.09),.35,'bs-dark')
 sign(R,0,6.6,-.28,8)
 R.text('Gaming & Spirits 24 Hours',(0,5.0,-.4),.55,'bs-red')
 # Brick south-west facade with tall arched window panels.
 S=Frame(B,-262.0,-3185,math.pi/2,y=0)
 S.box('bs-brick',(0,3.1,-.09),(9.8,6.1,.12))
 def bricklines(F,u,y,v,w,h):
  for yy in np.arange(y-h/2+.1,y+h/2,.18):
   F.box('bs-mortar',(u,float(yy),v),(w,.018,.012))
   for xx in np.arange(u-w/2+.12,u+w/2,.42):F.box('bs-mortar',(float(xx)+(.21 if int(yy/.18)%2 else 0),float(yy)+.08,v),(.015,.16,.013))
 bricklines(S,0,3.05,-.16,9.8,6)
 def window(F,u,y,v,w,h,arch=False):
  F.box('bs-wood',(u,y,v),(w+.2,h+.2,.12));F.box('bs-window',(u,y,v-.075),(w,h,.015))
  for du in [-w/2,0,w/2]:F.box('bs-mullion',(u+du,y,v-.1),(.05,h,.04))
  for yy in [y-h/2,y,y+h/2]:F.box('bs-mullion',(u,yy,v-.1),(w,.05,.04))
  if arch:F.arch(u,v-.11,w,h+.3,'bs-brick',.13,base=y-h/2)
 for u in [-2.7,2.7]:window(S,u,2.7,-.2,2.4,4.5,True)
 # Northwest upper room and green hip crown, fitted to the roof footprint.
 B.shell(tower,0,7.75,'bs-stucco',roof=False,solid=True)
 for a,b in zip(list(tower.exterior.coords),list(tower.exterior.coords)[1:]):B.upface('bs-green',[(a[0]-.03,7.85,a[1]),(b[0]-.03,7.85,b[1]),(-257,9.5,-3212)])
 T=Frame(B,-262.77,-3212,math.pi/2,y=0)
 def awning(F,u,y,v,w):
  for j in range(24):
   a=u-w/2+w*j/24;b=u-w/2+w*(j+1)/24;mat='bs-letter' if j%2 else 'bs-green'
   B.upface(mat,[F.p(a,y,v),F.p(b,y,v),F.p(b,y-.45,v-1),F.p(a,y-.45,v-1)])
   F.box(mat,((a+b)/2,y-.55,v-1),(w/24,.2,.05))
 for u in [-2.7,0,2.7]:window(T,u,6.3,-.02,2,2.1)
 awning(T,0,7.65,-.16,8.6)
 for u in [-2.4,2.4]:window(T,u,2.1,-.02,3,2.5);awning(T,u,3.6,-.15,3.3)
 # Each south-facing edge gets its own cladding plane, respecting the mapped projection.
 for a,b in zip(coords,coords[1:]):
  if max(a[1],b[1])<-3180 or min(a[1],b[1])<-3181:continue
  length=math.dist(a,b);dx=(b[0]-a[0])/length;dz=(b[1]-a[1])/length
  x,z=(a[0]+b[0])/2,(a[1]+b[1])/2;yaw=math.atan2(-dz,dx)
  F=Frame(B,x,z,yaw,y=0)
  if not p.covers(Point(F.p(0,0,.1)[0],F.p(0,0,.1)[2])):F=Frame(B,x,z,yaw+math.pi,y=0)
  w=length-.15
  F.box('bs-board1' if length>8 else 'bs-brick',(0,1.3,-.07),(w,2.6,.1))
  if length<=8:bricklines(F,0,1.3,-.135,w,2.5)
  else:
   for y in np.arange(.15,2.6,.18):F.box('bs-board'+str(int(y*10)%3),(0,float(y),-.14),(w,.16,.03))
  n=max(1,int(length/3.5))
  for u in np.linspace(-w/2+w/(2*n),w/2-w/(2*n),n):
   ww=min(2.4,w/n-.4);window(F,float(u),1.5,-.18,ww,1.8);window(F,float(u),4.9,-.1,ww,1.7);awning(F,float(u),5.9,-.22,ww+.3)
  if length>8:
   for y in np.arange(2.7,4,.18):F.box('bs-board'+str(int(y*10)%3),(0,float(y),-.12),(w,.16,.05))
   F.box('bs-green',(0,4.1,-.16),(w,.15,.12))
   B.upface('bs-wood',[F.p(-w/2,2.65,-1.7),F.p(w/2,2.65,-1.7),F.p(w/2,2.85,-.1),F.p(-w/2,2.85,-.1)])
   F.text('Gaming & Spirits 24 Hours',(0,3.1,-.25),.45,'bs-red')
  elif length>6:sign(F,0,3.65,-.25,min(5.8,w))
 for u in [-9,9]:R.plant(u,-4.6)
 for x,z in [(-231,-3183),(-230,-3201),(-233,-3171)]:Frame(B,x,z,y=0).plant(0,0,True)
 # Public room fitted within the footprint; no speculative private rooms or copied artwork.
 B.property=KEY+'-interior';B.detail=1
 room=R.poly([(-8.8,.25),(8.8,.25),(8.8,19.8),(-8.8,19.8)])
 assert p.buffer(.25).covers(room)
 B.shell(room,.15,5.8,'bs-inwall',roof=False,openings=[dict(p=R.p(0,.15,.25),width=2.4,height=3)])
 B.planar('bs-carpet',room,.15,True);B.planar('bs-dark',room,5.82)
 for v in [3,7,11,15,19]:R.box('bs-wood',(0,5.55,v),(17.5,.35,.2))
 # Two original detailed billiard tables and suspended stained-glass shades.
 for u in [-4.5,4.5]:
  v=11
  R.box('bs-dark',(u,.82,v),(1.65,.3,3.0),True);R.box('bs-wood',(u,.84,v),(1.72,.32,3.05))
  R.box('bs-felt',(u,1.05,v),(1.48,.06,2.78))
  for du in [-.82,.82]:R.box('bs-wood',(u+du,1.08,v),(.18,.13,3.14))
  for dv in [-1.52,1.52]:R.box('bs-wood',(u,1.08,v+dv),(1.8,.13,.18))
  for du in [-.75,.75]:
   for dv in [-1.43,0,1.43]:R.lathe('bs-dark',u+du,v+dv,[(1.12,.1),(1.13,.1)],12)
  for du in [-.6,.6]:
   for dv in [-1.1,1.1]:R.box('bs-dark',(u+du,.46,v+dv),(.28,.62,.28))
  for du in [-.87,.87]:
   R.box('bs-dark',(u+du,.83,v),(.025,.18,.55))
   for dv in [-1.35,-.7,0,.7,1.35]:R.box('bs-letter',(u+du*.93,1.155,v+dv),(.04,.012,.04))
  for j in range(6):B.sphere('bs-ball'+str(j%3),R.p(u-.3+j*.12,1.12,v+.35),.032,8,5)
  R.tube('bs-wood',(u-.2,1.16,v-.8),(u+.5,1.16,v+.9),.012,6)
  for dv in [-.65,.65]:R.tube('bs-dark',(u,3.4,v+dv),(u,5.6,v+dv),.018,5)
  for a,b in [((-1,-1.5),(1,-1.5)),((1,-1.5),(1,1.5)),((1,1.5),(-1,1.5)),((-1,1.5),(-1,-1.5))]:
   for j in range(12):
    t=j/12;tt=(j+1)/12;aa=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t);bb=(a[0]+(b[0]-a[0])*tt,a[1]+(b[1]-a[1])*tt)
    B.face('bs-shade'+str(j%3),[R.p(u+aa[0],3.0,v+aa[1]),R.p(u+bb[0],3.0,v+bb[1]),R.p(u+bb[0]*.55,3.65,v+bb[1]*.55),R.p(u+aa[0]*.55,3.65,v+aa[1]*.55)])
    R.tube('bs-dark',(u+aa[0],3,v+aa[1]),(u+aa[0]*.55,3.65,v+aa[1]*.55),.012,5)
  R.box('bs-lamp',(u,3.05,v),(1.5,.04,2.3))
 # Public wall displays are original abstract graphics, never reproduced sports artwork.
 for u in [-7,-3.5,0,3.5,7]:
  R.box('bs-dark',(u,3.2,19.62),(2.4,1.4,.13));R.box('bs-screen',(u,3.2,19.54),(2.2,1.2,.02))
  for j in range(3):R.box('bs-art'+str(j),(u-.7+j*.7,3.2,19.51),(.3,.8,.01))
  R.box('bs-wood',(u,4.65,19.6),(1.6,1.2,.1));R.box('bs-art1',(u,4.65,19.53),(1.4,1,.02))
  R.text('VEGAS',(u,4.55,19.5),.23,'bs-letter')
 for side in [-1,1]:
  for v in [4,7,10,13,16]:
   Q=R.p(side*8.72,0,v);W=Frame(B,Q[0],Q[2],R.yaw+side*math.pi/2,y=0)
   for y in [3.5,4.8]:
    W.box('bs-wood',(0,y,0),(1.6,1,.08));W.box('bs-art1',(0,y,-.06),(1.45,.85,.015))
    for k in range(3):W.box('bs-art'+str(k),(-.4+k*.4,y,-.075),(.25,.5,.01))
 for u in [-7,7]:
  for v in [4,17]:
   R.lathe('bs-dark',u,v,[(.15,.4),(.22,.4),(.24,.06),(1.3,.06)],12);R.lathe('bs-wood',u,v,[(1.3,.65),(1.4,.65)],24)
   for du in [-.95,.95]:
    R.box('bs-dark',(u+du,.9,v),(.45,.1,.45),True);R.box('bs-dark',(u+du,1.2,v+.22),(.45,.6,.06))
    for dx in [-.18,.18]:R.tube('bs-dark',(u+du+dx,.15,v-.17),(u+du+dx,.85,v-.17),.025,6);R.tube('bs-dark',(u+du+dx,.15,v+.17),(u+du+dx,1.45,v+.17),.025,6)
 routes=[dict(name='West entry to pool room',points=[R.p(0,y,v)for y,v in [(0,-5.4),(0,-5),(.15,-3.2),(.15,0),(.15,4),(.15,10),(.15,17)]]),dict(name='Public rear cross aisle',points=[R.p(u,.15,16)for u in [0,-4.5,0,4.5]])]
 return dict(key=KEY,name='Bourbon Street Sahara',center=[-248,0,-3200],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.15,.25),yaw=R.yaw,width=17.6,depth=19.55,height=5.8)],lights=[dict(p=R.p(u,4,v),color=0xffe4bc,power=3,range=12)for u,v in [(-4,6),(4,6),(-4,15),(4,15)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
