"""Original shared Sahara storefronts and photo-supported Bespoke public dining.
No measured tenant plan: dimensions, furniture count and unseen faces inferred.
"""
from common import *
from shapely.geometry.polygon import orient
KEY='sahara-2600'
def build(B):
 p=orient(footprint('way/1018431835'),sign=1);yaw=math.pi-.0072
 F=Frame(B,-385,-3241.4,yaw,y=0)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=F.p(0,.15,0),yaw=yaw,width=2.1,height=2.9,name='Bespoke public entry',venue=KEY)
 cuts=[door];bays=[]
 # Follow each mapped frontage step; avoid stretching one plane through projecting bays.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
  if mid[1]<-3244 or L<6:continue
  R=Frame(B,*mid,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  n=max(1,int(L/4.2))
  for j in range(n):
   u=(j-(n-1)/2)*(L/n);x,_,z=R.p(u,0,0)
   if -395<x<-375:continue
   w=min(3.45,L/n-.4);cuts.append(dict(p=R.p(u,.45,0),yaw=R.yaw,width=w,height=3.1));bays.append((R,u,w))
 for u in [-7,-3.8,3.8,7]:cuts.append(dict(p=F.p(u,.45,0),yaw=yaw,width=2.8,height=3.1))
 B.shell(p,0,5.4,'s26-stucco',openings=cuts,roof=False);B.planar('s26-membrane',p,5.38)
 def glazing(R,u,w,y=.45,h=3.1,clear=False,solid=True):
  R.box('s26-clear'if clear else's26-glass',(u,y+h/2,.05),(w,h,.025),solid)
  for du in [-w/2,0,w/2]:R.box('s26-mullion',(u+du,y+h/2,-.035),(.06,h+.1,.1))
  for yy in [y,y+.8,y+h]:R.box('s26-mullion',(u,yy,-.035),(w,.055,.1))
  for du in [-w/2,w/2]:R.box('s26-reveal',(u+du,y+h/2,.06),(.1,h+.24,.42))
  for yy in [y-.08,y+h+.09]:R.box('s26-reveal',(u,yy,.06),(w+.1,.13,.42))
 for R,u,w in bays:glazing(R,u,w)
 for u in [-7,-3.8,3.8,7]:glazing(F,u,2.8,clear=True)
 glazing(F,0,2.1,.15,2.9,True,False)
 for u in [-.14,.14]:F.tube('s26-alloy',(u,1.1,-.15),(u,1.65,-.15),.026,10)
 # Coping and sloping standing seam cap along the public front, flat service roof behind.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  R.box('s26-white',(0,5.44,0),(L+.03,.18,.35))
  if (a[1]+b[1])/2>-3244 and L>6:
   B.upface('s26-cap',[R.p(-L/2,4.45,-.9),R.p(L/2,4.45,-.9),R.p(L/2,5.38,1.7),R.p(-L/2,5.38,1.7)])
   for u in np.arange(-L/2,L/2,.42):R.tube('s26-seam',(float(u),4.47,-.9),(float(u),5.40,1.7),.018,6)
   R.box('s26-white',(0,4.36,-.9),(L,.17,.18))
 # Raised portals inferred from dated frontage views; transparent lower storefront remains open.
 for x,z,w,h,m,words in [(-385,-3241.4,10.5,7.2,'s26-mint','bespoke kitchen'),(-359,-3241.2,9,7.6,'s26-green','ADAM & EVE'),(-330,-3240,12,7.8,'s26-white',"DAVID'S BRIDAL"),(-273,-3240,11,6.8,'s26-white','RED WING')]:
  R=Frame(B,x,z,yaw,y=0)
  for u in [-w/2+.35,w/2-.35]:R.box(m,(u,h/2,-.3),(.7,h,1.2),True)
  R.box(m,(0,(h+3.7)/2,-.3),(w,h-3.7,1.2),True);R.box('s26-white',(0,h+.05,-.3),(w+.22,.15,1.4))
  R.text(words,(0,5.35,-.93),.57 if w>11 else .48,'s26-letter')
  for u in [-w/2+.7,w/2-.7]:
   R.box('s26-dark',(u,3.5,-.95),(.16,.4,.24));R.box('s26-lamp',(u,3.48,-1.08),(.12,.23,.03))
 F.text('ALL DAY CAFE',(0,3.27,-.18),.21,'s26-letter')
 # Local continuous pedestrian apron; geometry matches stepped frontage, roads untouched.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b)
  if (a[1]+b[1])/2<-3244 or L<6:continue
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0);R.box('s26-paving',(0,.075,-1.5),(L,.15,3),True)
 B.upface('s26-paving',[F.p(-1.3,0,-4),F.p(1.3,0,-4),F.p(1.3,.15,-2),F.p(-1.3,.15,-2)],True)
 # Roof HVAC and rear closed service entries. No fabricated access to other tenants.
 for x in range(-392,-263,12):
  for z in [-3258,-3250]:
   B.box('s26-curb',(x,5.56,z),(2.1,.35,1.8));B.box('s26-equipment',(x,6,z),(1.8,.6,1.5))
   B.lathe('s26-dark',(x,z),[(6.31,.49),(6.35,.49)],16)
   for j in np.arange(-.4,.41,.1):B.box('s26-alloy',(x,6.37,z+float(j)),(.8,.02,.025))
 for x in [-390,-370,-350,-330,-310,-290,-270]:
  R=Frame(B,x,-3265.3,0,y=0);R.box('s26-service',(0,1.25,-.08),(1.2,2.5,.1),True);R.box('s26-alloy',(.4,1.2,-.16),(.15,.04,.07));R.box('s26-dark',(0,2.8,-.1),(.4,.18,.2))
 # Interior is limited to reference-supported public cafe, never the whole retail shell.
 B.property=KEY+'-interior';B.source='public/'+KEY
 room=Polygon([(F.p(u,0,v)[0],F.p(u,0,v)[2])for u,v in [(-9,.2),(9,.2),(9,19),(-9,19)]])
 B.planar('s26-concrete',room,.15,True);B.shell(room,.15,4.7,'s26-cream',openings=cuts[:1]+[dict(p=F.p(u,.45,0),yaw=yaw,width=2.8,height=3.1)for u in [-7,-3.8,3.8,7]],roof=False,solid=True)
 for t in triangles(room):
  pts=[(x,4.68,z)for x,z in list(t.exterior.coords)[:-1]];a=np.array(pts);B.face('s26-dark',pts if np.cross(a[1]-a[0],a[2]-a[0])[1]<0 else list(reversed(pts)))
 for u in np.arange(-8,9,2):F.box('s26-joint',(float(u),.156,9.5),(.012,.008,18.5))
 for v in np.arange(2,19,2):F.box('s26-joint',(0,.157,float(v)),(18,.008,.012))
 for v in [3,8,13,17]:
  F.box('s26-beam',(0,4.4,v),(18,.2,.15));F.tube('s26-duct',(-8,4.1,v),(8,4.1,v),.23,16)
  for u in [-7,-3,3,7]:F.lathe('s26-alloy',u,v,[(4.0,.26),(4.15,.26)],12)
 for u in [-6,5]:
  for v in [3,6.5,10,13.5]:
   F.box('s26-wood',(u,.91,v),(1.4,.09,.85),True);F.box('s26-dark',(u,.54,v),(.12,.7,.12));F.box('s26-dark',(u,.2,v),(.65,.06,.5))
   for side in [-1,1]:
    C=Frame(B,*[F.p(u,0,v+side*.85)[i]for i in [0,2]],yaw if side==1 else yaw+math.pi,y=.15)
    C.box('s26-seat',(0,.45,0),(.46,.08,.46),True)
    for xx in [-.2,.2]:
     for zz in [-.2,.2]:C.tube('s26-chair',(xx,0,zz),(xx,.45,zz),.025,8)
     C.tube('s26-chair',(xx,.45,.2),(xx,.87,.2),.028,8)
    C.path('s26-chair',[(-.2,.63,.2),(-.23,.82,.2),(-.15,.91,.2),(.15,.91,.2),(.23,.82,.2),(.2,.63,.2)],.035,10)
   F.lathe('s26-white',u,v,[(.97,.08),(1.08,.055)],12)
 # Wood plant divider and slatted wall from photos; center aisle stays clear.
 F.box('s26-wood',(-2.7,.75,8.5),(.65,1.2,7),True)
 for v in np.arange(5.2,12,.35):
  for j in range(3):
   vv=float(v);xx=-2.7+(j-1)*.16;top=1.65+(j%2)*.27
   F.tube('s26-stem',(-2.7,1.3,vv),(xx,top,vv+.12),.009,6)
   for k in range(4):
    yy=1.39+k*.09;side=1 if k%2 else -1;leaf=[F.p(xx,yy,vv),F.p(xx+side*.12,yy+.16,vv-.08),F.p(xx+side*.23,yy+.25,vv+.05),F.p(xx+side*.08,yy+.11,vv+.11)]
    B.face('s26-leaf',leaf);B.face('s26-leaf',list(reversed(leaf)))
 for yy in np.arange(.25,1.3,.15):F.box('s26-woodjoint',(-2.7,float(yy),4.98),(.65,.012,.02))
 for y in np.arange(.4,3.7,.17):F.box('s26-slat',(-8.8,float(y),9.5),(.1,.12,18))
 # Inferred rear service counter enclosing private kitchen. Public circulation only.
 F.box('s26-wood',(4.9,.71,16.9),(6.4,1.12,1.1),True);F.box('s26-alloy',(4.9,1.31,16.9),(6.5,.08,1.2))
 for u in [2.3,3.5,4.7,5.9,7.1]:F.box('s26-wood',(u,.72,16.33),(1.15,1.06,.04));F.box('s26-alloy',(u+.4,1.05,16.28),(.08,.03,.05))
 F.box('s26-wood',(4.9,3.3,17),(6.7,.7,1.15))
 F.box('s26-dark',(4,1.65,17),(.9,.6,.55));F.box('s26-alloy',(4,1.66,16.68),(.7,.3,.03))
 for u in [3.7,4.3]:F.tube('s26-alloy',(u,1.53,16.65),(u,1.42,16.55),.025,8)
 F.box('s26-dark',(6.8,1.5,16.9),(.4,.3,.3));F.box('s26-screen',(6.8,1.55,16.73),(.32,.18,.02))
 # Small original abstract wall reliefs, no copied artwork or photo textures.
 for v in [4,8,12]:
  F.box('s26-wood',(-8.65,2.6,v),(.1,1.1,1.4))
  for j in range(4):F.box(['s26-mint','s26-cream','s26-green','s26-chair'][j],(-8.57,2.3+j*.16,v+(j-1.5)*.2),(.025,.25,.4))
 for u in [-5,4]:
  for v in [4,10,15]:
   F.tube('s26-dark',(u,3.4,v),(u,4.6,v),.015,8);F.lathe('s26-white',u,v,[(3.2,.32),(3.4,.22),(3.5,.1)],20);F.lathe('s26-lamp',u,v,[(3.19,.28),(3.2,.28)],20)
 routes=[dict(name='Cafe entrance and dining aisle',points=[F.p(0,y,v)for v,y in [(-5,0),(-4,0),(-2,.15),(1,.15),(7,.15),(14.5,.15)]]),dict(name='Public service approach',points=[F.p(u,.15,v)for u,v in [(0,14.5),(0,15.3),(3,15.3),(6,15.3)]])]
 return dict(key=KEY,name='2600 Sahara and Bespoke Kitchen',center=[-329,0,-3252],bounds=list(p.buffer(4).bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(0,.15,.2),yaw=yaw,width=18,depth=18.8,height=4.6)],lights=[dict(p=F.p(u,3.5,v),color=0xfff4df,power=4,range=12)for u,v in [(-4,5),(4,5),(-4,13),(4,13)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
