"""Original Firefly Hughes Center geometry; documented fitted public layout.
Reference photographs are not textures. Room sizes and heights are estimates.
"""
from common import *
KEY='firefly-hughes'; IDS=['way/511850831','way/511850830']; YAW=-math.pi/2+.036

def build(B):
 F=Frame(B,1429.2,105.8,YAW,y=0);p=footprint(IDS[0]);can=footprint(IDS[1])
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=F.p(0,.22,0),yaw=YAW,width=2.4,height=2.7,name='Firefly public entrance',venue=KEY)
 B.shell(p,.95,4.15,'ff-siding',roof=False,openings=[door]);B.shell(p,.02,.95,'ff-stone',roof=False,solid=False,openings=[door]);B.planar('ff-membrane',p,4.15)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0);L=math.dist(a,b)
  R.box('ff-trim',(0,4.02,0),(L+.12,.22,.22))
  for u in np.arange(-L/2+.15,L/2,.22):
   pt=R.p(float(u),0,0)
   if L>4 and ((a[0]+b[0])/2<1431 or (a[1]+b[1])/2>123) and any(abs(float(u)-w)<1.48 for w in np.arange(-L/2+1.7,L/2-1,3.5)):continue
   if math.dist([pt[0],pt[2]],[door['p'][0],door['p'][2]])>1.5:R.box('ff-siding',(float(u),2.45,.085),(.035,2.8,.035))
 # Tiled hipped roof bands around west and south frontage; flat equipment area east.
 def hip(u,v,w,d,eave=4.2,rise=1.35):
  a=F.p(u-w/2,eave,v-d/2);b=F.p(u+w/2,eave,v-d/2);c=F.p(u+w/2,eave,v+d/2);d0=F.p(u-w/2,eave,v+d/2)
  if w>=d:
   r1=F.p(u-(w-d)/2,eave+rise,v);r2=F.p(u+(w-d)/2,eave+rise,v)
   for vs in [[a,b,r2,r1],[b,c,r2],[c,d0,r1,r2],[d0,a,r1]]:B.upface('ff-tile',vs)
  else:
   r1=F.p(u,eave+rise,v-(d-w)/2);r2=F.p(u,eave+rise,v+(d-w)/2)
   for vs in [[a,b,r1],[b,c,r2,r1],[c,d0,r2],[d0,a,r1,r2]]:B.upface('ff-tile',vs)
 hip(-3,-3.7,32,7.6);hip(18,-13,7,23);hip(10.5,2.2,7,8.5)
 # West porte-cochere: open pitched timber frame on stone plinths.
 C=Frame(B,can.centroid.x,can.centroid.y,.036,y=0)
 for u in [-4.5,4.5]:
  for v in [-2.85,2.85]:
   C.box('ff-stone',(u,.48,v),(.85,.9,.85),True);C.box('ff-trim',(u,2.0,v),(.28,2.2,.28),True)
 for v in [-3.3,3.3]:
  C.tube('ff-trim',(-5,3.35,v),(5,3.35,v),.12,8)
  for a,b in [((-5,3.35,v),(0,5.0,v)),((0,5.0,v),(5,3.35,v)),((0,3.35,v),(0,5.0,v)),((-2.5,3.35,v),(0,5.0,v)),((2.5,3.35,v),(0,5.0,v))]:C.tube('ff-trim',a,b,.11,8)
 for side in [-1,1]:B.upface('ff-tile',[C.p(0,5.08,-3.5),C.p(side*5,3.43,-3.5),C.p(side*5,3.43,3.5),C.p(0,5.08,3.5)])
 # Trellis connecting arrival to entrance; no solid wall or road slab beneath it.
 for u in [-1.7,1.7]:F.box('ff-trim',(u,3.18,5),( .16,.22,10))
 for v in np.arange(.1,10.1,.55):F.box('ff-trim',(0,3.3,float(v)),(3.8,.18,.12))
 B.upface('ff-paving',[F.p(-1.2,.22,0),F.p(1.2,.22,0),F.p(1.2,.16,2.4),F.p(-1.2,.16,2.4)],True)
 F.text('FIREFLY*',(0,3.75,.35),.45,'ff-letter',back=True)
 # Window bays follow actual mapped west/south edge, avoiding floating planes.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);mx=(a[0]+b[0])/2;mz=(a[1]+b[1])/2
  if L<4 or not (mx<1431 or mz>123):continue
  R=Frame(B,mx,mz,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  # Determine external normal from the polygon, independent of ring winding.
  pp=R.p(0,0,.2);side=-1 if p.contains(Point(pp[0],pp[2])) else 1
  for uu in np.arange(-L/2+1.7,L/2-1,3.5):
   pos=R.p(float(uu),0,0)
   if math.dist([pos[0],pos[2]],[door['p'][0],door['p'][2]])<2.5:continue
   R.box('ff-glass',(float(uu),2.33,side*.06),(2.75,2.45,.04))
   for du in [-1.4,0,1.4]:R.box('ff-cream',(float(uu)+du,2.33,side*.1),(.06,2.53,.08))
   for yy in [1.08,3.1,3.58]:R.box('ff-cream',(float(uu),yy,side*.1),(2.86,.07,.08))
 # Northwest patio with a curved outer railing, umbrellas and small tables.
 patio=F.poly([(-21,0),(-3,0),(-3,5),(-5,7),(-18,7),(-21,5)])
 B.planar('ff-paving',patio,.18,True)
 pts=[(-21,0),(-21,5),(-18,7),(-5,7),(-3,5)]
 for a,b in zip(pts,pts[1:]):
  for y in [.26,1.15]:F.tube('ff-black',(a[0],y,a[1]),(b[0],y,b[1]),.035,8)
  for t in np.linspace(0,1,max(2,int(math.dist(a,b)/.18))):
   u=a[0]+(b[0]-a[0])*t;v=a[1]+(b[1]-a[1])*t;F.tube('ff-black',(u,.22,v),(u,1.15,v),.018,6)
 for u in [-18,-11,-5]:
  F.lathe('ff-black',u,3.2,[(.18,.35),(.24,.35),(.26,.06),(.9,.06)],16);F.lathe('ff-table',u,3.2,[(.9,.67),(.97,.67)],32)
  F.tube('ff-black',(u,.2,3.2),(u,2.9,3.2),.035,8)
  F.lathe('ff-cream',u,3.2,[(2.55,1.65),(2.9,.08)],8)
  for dv in [-1,1]:F.box('ff-seat',(u,.6,3.2+dv),(.55,.15,.55),True)
 for u,v in [(-20,-9),(-5,-18),(8,-21),(13,-13)]:
  F.box('ff-equipment',(u,4.65,v),(1.8,1,1.3))
  for yy in np.arange(4.25,5.05,.12):F.box('ff-black',(u,float(yy),v+.66),(1.6,.025,.025))
 # Public rooms follow observed bar/window-banquette arrangement, fitted within mapped shell.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=unary_union([F.poly([(-18,-.12),(0.9,-.12),(.9,-14.5),(-18,-14.5)]),F.poly([(-2,-.12),(18,-.12),(18,-22),(-2,-22)])]).intersection(p.buffer(-.12))
 B.shell(room,.22,3.6,'ff-panel',roof=False,openings=[door]);B.planar('ff-plank',room,.22,True);B.planar('ff-panel',room,3.6)
 # Cornices and skirting, clipped to room outline; entrance has no crossing skirting.
 for a,b in zip(list(room.exterior.coords),list(room.exterior.coords)[1:]):
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0);L=math.dist(a,b)
  for y,w in [(3.42,.15),(3.54,.22)]:R.box('ff-trim',(0,y,0),(L,.09,w))
 # Interior window rhythm above the banquette, with recessed green framing.
 for u in [-15.5,-11.5,-7.5]:
  F.box('ff-glass',(u,2.25,-.24),(3.4,2.25,.04))
  for du in [-1.75,0,1.75]:F.box('ff-trim',(u+du,2.25,-.29),(.08,2.34,.09))
  for y in [1.12,2.95,3.4]:F.box('ff-trim',(u,y,-.29),(3.55,.08,.09))
 # Long bar facing the window banquettes; brass front and green stone top.
 F.box('ff-brass',(-10,.8,-9.7),(12,1.15,1.2),True);F.box('ff-marble',(-10,1.42,-9.7),(12.3,.13,1.5),True)
 F.box('ff-mirror',(-10,2,-13.9),(12,2.5,.06))
 for u in [-16,-10,-4]:
  F.lathe('ff-panel',u,-13.5,[(.22,.28),(.45,.28),(.5,.2),(2.9,.2),(3.1,.34)],20)
 for y in [1.4,2.15,2.9]:
  F.box('ff-brass',(-10,y,-13.5),(11.5,.06,.55))
  for u in np.arange(-15.3,-4.5,.45):F.lathe('ff-bottle',float(u),-13.45,[(y+.04,.065),(y+.28,.065),(y+.4,.023)],8)
 for u in np.arange(-15,-4,.95):
  F.box('ff-tan',(float(u),1.0,-8.2),(.48,.14,.5),True);F.box('ff-tan',(float(u),1.28,-7.97),(.5,.53,.07))
  for du in [-.18,.18]:
   for dv in [-.18,.18]:F.tube('ff-brass',(float(u)+du,.22,-8.2+dv),(float(u)+du*.7,.96,-8.2+dv*.7),.026,8)
 # Upholstered window banquette and round green tables; broad central aisle stays clear.
 for u in [-15.5,-11.5,-7.5]:
  F.box('ff-seat',(u,.65,-.72),(3.75,.28,.75),True);F.box('ff-seat',(u,1.0,-.35),(3.75,1.1,.16),True)
  for du in np.arange(-1.7,1.8,.22):F.box('ff-seat',(u+float(du),1.02,-.23),(.04,.96,.07))
 def table(u,v):
  F.lathe('ff-black',u,v,[(.22,.36),(.27,.36),(.3,.055),(.96,.055)],20);F.lathe('ff-table',u,v,[(.96,.67),(1.03,.67)],32)
  for side in [-1,1]:
   F.box('ff-seat',(u+side*.98,.62,v),(.53,.17,.55),True);# Curved upholstered back around the outer side of each chair.
   cx=u+side*.98
   for t in np.linspace(-math.pi/2,math.pi/2,13)[:-1]:
    t2=t+math.pi/12
    B.face('ff-seat',[F.p(cx+side*.3*math.cos(t),.66,v+.3*math.sin(t)),F.p(cx+side*.3*math.cos(t2),.66,v+.3*math.sin(t2)),F.p(cx+side*.3*math.cos(t2),1.19,v+.3*math.sin(t2)),F.p(cx+side*.3*math.cos(t),1.19,v+.3*math.sin(t))])
   for dv in [-.2,.2]:F.tube('ff-black',(u+side*.98,.22,v+dv),(u+side*.98,.6,v+dv),.025,8)
   F.lathe('ff-pink',u+side*.35,v,[(1.035,.18),(1.06,.18)],20)
  F.lathe('ff-glass',u,v,[(1.04,.06),(1.22,.06)],12)
 for u in [-15.5,-11.5,-7.5]:table(u,-2.5)
 for u in [4,9,14]:
  for v in [-5,-10,-16]:table(u,v)
 # Rectangular wall panels and shallow coffer beams from the photographed joinery.
 for u in [3,7,11,15]:
  for yy in [.6,1.1,2.9,3.25]:F.box('ff-trim',(u,yy,-21.82),(3.8,.045,.045))
  for du in [-1.9,1.9]:F.box('ff-trim',(u+du,1.92,-21.82),(.045,2.7,.045))
 for u in [-17,-3,1,17]:F.box('ff-trim',(u,3.5,-7),(.22,.16,14))
 for vv in [-1,-7,-14]:F.box('ff-trim',(-9,3.5,vv),(16,.16,.22))
 # Panel moldings and original abstract wall pieces; no copyrighted art reproduced.
 for u in [3,8,13,17]:
  F.box('ff-brass',(u,2.1,-21.7),(2.1,1.6,.06));F.box('ff-art',(u,2.1,-21.64),(1.94,1.44,.04))
 # Brass chandelier arms and candle sleeves. Lighting uses existing venue pool only.
 for u,v in [(-12,-5.5),(-5,-5.5),(5,-12),(13,-12)]:
  F.tube('ff-brass',(u,3.58,v),(u,2.85,v),.025,8)
  for t in np.linspace(0,math.tau,8,endpoint=False):
   x=u+.6*math.cos(t);z=v+.6*math.sin(t);F.tube('ff-brass',(u,2.87,v),(x,2.87,z),.022,8)
   F.lathe('ff-brass',x,z,[(2.87,.065),(3.1,.065)],10);F.lathe('ff-lamp',x,z,[(3.1,.035),(3.23,.035)],10)
 routes=[dict(name='Arrival to bar and dining',points=[F.p(0,.22,v) for v in [10,3,-1,-5]]+[F.p(u,.22,-5) for u in [1.7,2]]+[F.p(2,.22,v) for v in [-8,-13,-19]]),dict(name='Bar aisle',points=[F.p(u,.22,-5.5) for u in [0,-3,-8,-13,-16]])]
 routes.append(dict(name='Northwest patio',points=[F.p(u,.22,v) for u,v in [(0,3),(-2,3),(-2,1.5),(-10,1.5),(-19,1.5)]]))
 return dict(key=KEY,name='Firefly Tapas Kitchen + Bar',center=[p.centroid.x,0,p.centroid.y],bounds=list(p.union(can).bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(-8.5,.22,0),yaw=F.yaw+math.pi,width=19,depth=15,height=3.8),dict(origin=F.p(8,.22,0),yaw=F.yaw+math.pi,width=20,depth=22.3,height=3.8)],lights=[dict(p=F.p(u,3.1,v),color=0xffe4c5,power=8,range=10) for u,v in [(-12,-5),(-4,-5),(5,-12),(13,-12)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
