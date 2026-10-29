"""Original 2691 Sahara shop/fuel canopy; dated photo-supported finishes, fitted layout."""
from common import *
KEY='seven-eleven-sahara';IDS=['way/1018431818','way/943068966']
def build(B):
 p,c=map(footprint,IDS);F=Frame(B,-367.48,-3075.09,-.0249,y=0)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=F.p(0,.15,0),yaw=-.0249,width=2,height=2.6,name='Shop entry',venue=KEY)
 wins=[dict(p=F.p(u,.65,0),yaw=-.0249,width=2.1,height=2.25)for u in [-4.4,-2.1,2.1,4.4]]
 B.shell(p,0,4.7,'ss-masonry',openings=[door,*wins],roof=False);B.planar('ss-membrane',p,4.7)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  w=math.dist(a,b);R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  R.box('ss-coping',(0,4.72,0),(w,.12,.32))

 # Forward fascia and glazed storefront, separated from existing shell.
 F.box('ss-dark',(0,3.78,-.22),(13.4,1.35,.62));F.box('ss-coping',(0,4.48,-.22),(13.6,.12,.7))
 for u in [-4.4,-2.1,2.1,4.4]:
  F.box('ss-glass',(u,1.8,-.04),(2.1,2.3,.035),True)
  for v in [-1.08,1.08]:F.box('ss-dark',(u+v,1.8,-.07),(.065,2.4,.1))
  for y in [.6,2.98]:F.box('ss-dark',(u,y,-.07),(2.2,.065,.1))
  F.box('ss-base-tile',(u,.29,-.08),(2.24,.58,.12))
 for u in [-.5,.5]:
  F.box('ss-glass',(u,1.45,-.06),(.92,2.5,.035))
  for du in [-.48,.48]:F.box('ss-dark',(u+du,1.45,-.1),(.04,2.6,.08))
  for y in [.15,1.1,2.75]:F.box('ss-dark',(u,y,-.1),(1,.045,.08))
  F.tube('ss-alloy',(u*.35,1.05,-.17),(u*.35,1.5,-.17),.025,10)
 def sign(R,u,y,v,w):
  R.box('ss-white',(u,y,v),(w,1.05,.07))
  for yy,h,m in [(y+.35,.15,'ss-orange'),(y,.22,'ss-green'),(y-.33,.15,'ss-red')]:R.box(m,(u,yy,v-.05),(w,.15,.025))
  R.box('ss-white',(u,y,v-.08),(1.3,1,.03));R.text('7',(u,y-.12,v-.12),.63,'ss-red');R.text('ELEVEN',(u,y-.38,v-.13),.15,'ss-green')
 sign(F,0,3.8,-.56,8.1)
 # Authored block joints only on solid facade wings, never through windows.
 for lo,hi in [(-8.7,-5.6),(5.6,8.7)]:
  for row,y in enumerate(np.arange(.2,4.6,.27)):
   F.box('ss-mortar',((lo+hi)/2,float(y),-.045),(hi-lo,.012,.025))
   for u in np.arange(lo+.2+(row%2)*.25,hi,.5):F.box('ss-mortar',(float(u),float(y)+.13,-.045),(.012,.25,.025))
 F.text('2691',(0,2.82,-.12),.25,'ss-white')
 # Store pavement and accessible lip ramp; no public road edits.
 F.box('ss-concrete',(0,.075,-1.3),(18,.15,2.5),True)
 B.upface('ss-concrete',[F.p(-1.1,.01,-3),F.p(1.1,.01,-3),F.p(1.1,.15,-1.8),F.p(-1.1,.15,-1.8)],True)
 for u in [-7.8,7.8]:
  F.box('ss-dark',(u,.65,-1.2),(.55,1,.5),True);F.box('ss-alloy',(u,1.18,-1.2),(.61,.1,.56));F.box('ss-black',(u,.98,-1.46),(.35,.18,.025))
 for x,z in [(-373,-3065),(-363,-3064)]:
  B.box('ss-alloy',(x,5,z),(1.5,.6,1.1));B.box('ss-dark',(x,5.32,z),(1.2,.04,.8))
 # Independent open fuel canopy: never close its sides with a ground-level wall.
 B.shell(c,4.9,5.7,'ss-white',roof=False,solid=False);B.planar('ss-membrane',c,5.7)
 for t in triangles(c):
  pts=[(x,4.9,z)for x,z in list(t.exterior.coords)[:-1]];a=np.array(pts);B.face('ss-soffit',pts if np.cross(a[1]-a[0],a[2]-a[0])[1]<0 else list(reversed(pts)))
 for a,b in zip(list(c.exterior.coords),list(c.exterior.coords)[1:]):
  w=math.dist(a,b);R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  for y,h,m in [(5.53,.12,'ss-orange'),(5.28,.23,'ss-green'),(5.04,.12,'ss-red')]:R.box(m,(0,y,0),(w,h,.04))
 # Four double-faced dispensers inferred from photograph numbered8; count not surveyed.
 for j,x in enumerate([-385,-379,-373,-367]):
  R=Frame(B,x,-3099.5,0,y=0)
  R.box('ss-concrete',(0,.13,0),(1.6,.26,3.8),True)
  for u in [-.63,.63]:R.box('ss-alloy',(u,2.55,0),(.18,4.7,.22),True)
  R.box('ss-white',(0,2.38,0),(1.55,.42,.7));R.box('ss-dark',(0,1.26,0),(1.02,1.94,.65),True)
  for side in [-1,1]:
   S=Frame(B,x,-3099.5,0 if side==-1 else math.pi,y=0)
   S.box('ss-screen',(0,1.65,-.34),(.55,.35,.025));S.box('ss-alloy',(.29,1.23,-.35),(.18,.27,.03))
   for row in range(4):
    for col in range(3):S.box('ss-black',(.235+col*.053,1.32-row*.06,-.37),(.035,.035,.02))
   S.box('ss-green',(0,.78,-.35),(.8,.35,.03));S.text(str(j*2+(1 if side==-1 else 2)),(.39,2.3,-.37),.18,'ss-dark');S.text('7-ELEVEN',(-.14,2.32,-.37),.13,'ss-green')
   S.path('ss-black',[(.5,1.9,-.1),(.78,1.5,-.2),(.8,.48,-.25),(.58,.37,-.3),(.46,1.25,-.36)],.035,8)
   S.tube('ss-alloy',(.46,1.25,-.36),(.4,1.48,-.36),.05,8)
  for v in [-1.5,1.5]:R.tube('ss-yellow',(0,.25,v),(0,1.1,v),.07,12)
  R.box('ss-light',(0,4.87,0),(1.4,.035,1.4))
 # Public sales room, original generic merchandise. Private stockroom excluded.
 B.property=KEY+'-interior';B.source='public/'+KEY
 room=p.buffer(-.18);B.planar('ss-floor',room,.15,True);B.shell(room,.15,3.25,'ss-cream',openings=[door,*wins],roof=False,solid=False)
 for t in triangles(room):
  pts=[(x,3.22,z)for x,z in list(t.exterior.coords)[:-1]];a=np.array(pts);B.face('ss-ceiling',pts if np.cross(a[1]-a[0],a[2]-a[0])[1]<0 else list(reversed(pts)))
 # Photo-supported horizontal gray wood cladding, inside rear wall.
 for row,y in enumerate(np.arange(.28,3.2,.2)):F.box('ss-board'+str(row%3),(0,float(y),14.43),(17,.19,.04))
 for u in np.arange(-8.3,8.4,.6):F.box('ss-grout',(float(u),.157,7.6),(.014,.007,14.1));F.box('ss-grid',(float(u),3.2,7.6),(.02,.025,14.1))
 for v in np.arange(.6,14.8,.6):F.box('ss-grout',(0,.158,float(v)),(17,.007,.014));F.box('ss-grid',(0,3.2,float(v)),(17,.025,.02))
 for u in [-6,-2,2,6]:
  for v in [3,7,11]:F.box('ss-light',(u,3.18,v),(.55,.025,1.15))
 def goods(R,u,v,y,n=8):
  for j in range(n):
   x=u+(j-(n-1)/2)*.22;m=['ss-pack-red','ss-pack-blue','ss-pack-gold','ss-pack-green'][j%4]
   R.box(m,(x,y+.12,v),(.17,.24,.14));R.box('ss-white',(x,y+.14,v-.075),(.12,.07,.008))
 def rack(u,v,w=2.3):
  R=Frame(B,*[F.p(u,0,v)[k]for k in [0,2]],-.0249,y=.15)
  R.box('ss-dark',(0,.08,0),(w,.16,.95),True)
  for x in [-w/2,w/2]:R.box('ss-dark',(x,.82,0),(.05,1.65,.08))
  for y in [.25,.65,1.05,1.45]:
   R.box('ss-alloy',(0,y,0),(w,.04,.9));goods(R,0,-.26,y+.03)
   for v in [-.46,.46]:
    R.tube('ss-alloy',(-w/2,y+.12,v),(w/2,y+.12,v),.009,6)
    for xx in np.arange(-w/2,w/2,.15):R.tube('ss-alloy',(float(xx),y,v),(float(xx),y+.12,v),.007,6)
   for j in range(8):R.box('ss-pack-gold',((j-3.5)*.22,y+.15,.26),(.17,.24,.14))
 for u in [-4.5,4.3]:
  for v in [4.5,8]:rack(u,v)
 # Rear refrigerator bank and drinks counter separated by circulation.
 for u in [-6.7,-5.5,-4.3,-3.1,-1.9]:
  F.box('ss-dark',(u,1.4,13.8),(1.16,2.5,1),True)
  for y in [.6,1,1.4,1.8,2.2]:F.box('ss-alloy',(u,y,13.24),(1,.035,.5));goods(F,u,13.05,y+.03,4)
  F.box('ss-cabinet',(u,.43,13.2),(1.14,.55,.2))
  for y in [.24,.29,.34,.39,.44]:F.box('ss-dark',(u,y,13.085),(.85,.012,.012))
 F.box('ss-dark',(-4.3,2.85,13.1),(6.2,.4,.2));F.text('QUICK EATS',(-4.3,2.75,12.97),.3,'ss-white')
 F.box('ss-cabinet',(5.3,.72,12.8),(5.6,1.14,1.15),True);F.box('ss-counter',(5.3,1.32,12.8),(5.75,.1,1.25))
 for u in [3.5,4.4,5.3]:
  F.box('ss-dark',(u,1.7,12.95),(.64,.7,.55));F.box('ss-screen',(u,1.8,12.65),(.4,.22,.02));F.tube('ss-alloy',(u,1.5,12.62),(u,1.43,12.52),.025,8)
 # Cabinet fronts, drip grates and fittings are original geometry.
 for u in [3.3,4.3,5.3,6.3,7.3]:
  F.box('ss-cabinet',(u,.73,12.21),(.94,1.0,.04));F.box('ss-alloy',(u+.32,1.05,12.17),(.12,.035,.04))
  for y in [.3,.35,.4,.45,.5]:F.box('ss-dark',(u,float(y),12.18),(.65,.012,.015))
 for u in [3.5,4.4,5.3]:
  F.box('ss-alloy',(u,1.39,12.42),(.54,.055,.35))
  for xx in np.arange(u-.24,u+.25,.045):F.box('ss-dark',(float(xx),1.423,12.42),(.015,.008,.3))
  F.box('ss-white',(u,2.07,12.95),(.57,.035,.5))
 for u in [6.3,6.7]:
  for y in [1.4,1.47,1.54]:F.lathe('ss-white',u,12.45,[(y,.07),(y+.15,.1)],12)
 # Hot food case and till on front-side counter, outside walking aisle.
 F.box('ss-cabinet',(6.9,.7,2),(2.6,1.1,1.2),True);F.box('ss-counter',(6.9,1.3,2),(2.7,.1,1.25))
 for y in [1.36,1.7,2.04]:F.box('ss-alloy',(6.5,y,2),(1.6,.04,.8))
 for u in [5.72,7.28]:F.box('ss-alloy',(u,1.7,2),(.04,.7,.8))
 F.box('ss-clear',(6.5,1.7,1.58),(1.54,.65,.02))
 for u in [6,6.4,6.8]:F.lathe('ss-pack-gold',u,2,[(1.4,.12),(1.5,.13),(1.55,.08)],12)
 F.box('ss-dark',(7.7,1.55,2),(.4,.4,.25))
 lights=[dict(p=F.p(u,2.9,v),color=0xfff6e7,power=4,range=10)for u,v in [(-4,4),(4,4),(-4,11),(4,11)]]
 routes=[dict(name='Forecourt entry and rear aisle',points=[F.p(0,y,v)for v,y in [(-5,0),(-3,0),(-1.5,.15),(1,.15),(6,.15),(11,.15)]]),dict(name='Rear drinks aisle',points=[F.p(u,.15,11)for u in [0,4,6]])]
 return dict(key=KEY,name='7-Eleven Sahara',center=[p.centroid.x,0,p.centroid.y],bounds=list(p.union(c).bounds),structural=True,exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(0,.15,.25),yaw=-.0249,width=17.2,depth=14.2,height=3.2)],lights=lights,hotelSources=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
