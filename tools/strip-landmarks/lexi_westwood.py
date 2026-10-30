"""The Lexi: original reconstruction from official gallery and mapped footprint.
Heights and lobby arrangement are inferred, not a surveyed floor plan.
This generator writes ONLY its own assets; grouped installation is separate.
"""
from common import *
from shapely.geometry.polygon import orient
KEY='lexi-westwood'
COLORS={'lx-stucco':'deddd3','lx-cornice':'d8d7cd','lx-iron':'292e2d','lx-glass':'3a494b','lx-tile':'535650','lx-tile-edge':'666960','lx-roof':'c9c8be','lx-paving':'b9b09a','lx-coping':'dbd4bd','lx-basin':'63918b','lexi_pool':'398c91','lx-cushion':'ae423e','lx-fabric':'c6b58b','lx-wall':'c3b09b','lx-floor':'ddd9ca','lx-blacktile':'333b39','lx-grout':'6f7169','lx-velvet':'414743','lx-green':'5d7565','lx-wood':'6b4c34','lx-metal':'949e98','lx-lamp':'e9e4cc','lx-art':'927d58','lx-leaf':'456044'}

def rail(R,u,y,v,w):
 for yy in [y+.13,y+.92]:R.box('lx-iron',(u,yy,v),(w,.045,.055))
 for x in np.linspace(u-w/2,u+w/2,max(3,int(w/.18)+1)):R.box('lx-iron',(float(x),y+.52,v),(.024,.82,.035))

def hip(B,p,y,depth=1.6,rise=.85):
 inner=p.buffer(-depth,join_style=2)
 for tri in triangles(p.difference(inner)):
  B.upface('lx-tile',[(x,y+rise*min(1,p.boundary.distance(Point(x,z))/depth),z)for x,z in list(tri.exterior.coords)[:-1]])
 B.planar('lx-roof',inner,y+rise-.03)
 # Raised courses follow the hip perimeter; no coplanar decorative overlays.
 for inset in np.arange(.18,depth,.28):
  ring=p.buffer(-float(inset),join_style=2)
  if ring.geom_type!='Polygon':continue
  pts=[(x,y+rise*float(inset)/depth+.018,z)for x,z in ring.exterior.coords]
  B.path('lx-tile-edge',pts,.018,5)


def chair(R,u,v,yaw=0):
 C=Frame(R.b,*[R.p(u,0,v)[i]for i in [0,2]],R.yaw+yaw,y=R.y)
 C.box('lx-velvet',(0,.47,0),(1.05,.25,.95),True)
 for x in [-.49,.49]:C.box('lx-velvet',(x,.66,0),(.15,.45,1.02))
 C.box('lx-velvet',(0,.87,.42),(1.08,.8,.18))
 for x in np.linspace(-.42,.42,8):C.tube('lx-velvet',(float(x),.58,.31),(float(x),1.24,.31),.053,8)
 for x in [-.4,.4]:
  for z in [-.35,.35]:C.tube('lx-iron',(x,.2,z),(x,.4,z),.028,8)

def build(B):
 B.property=KEY+'-exterior';B.source='hotel/'+KEY;B.detail=0
 p=orient(footprint('way/276428190'),sign=1)
 # Open west stair shaft: remove its volume from the opaque hotel shell.
 stair=box(257.0,-3093.7,263.0,-3076.2).intersection(p)
 body=p.difference(stair)
 B.shell(body,0,16.8,'lx-stucco',roof=False)
 hip(B,p.buffer(.4,join_style=2),16.8)
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  R.box('lx-cornice',(0,16.63,0),(length,.28,.48))
  # Windows have shallow projecting surrounds; opaque backs conceal unmodelled rooms.
  if length<8:continue
  n=max(1,int(length/4.0))
  for j in range(n):
   u=(j+.5)*length/n-length/2
   if stair.buffer(.4).covers(Point(*[R.p(u,0,0)[i]for i in [0,2]])):continue
   for row in range(4):
    y=4.6+row*2.85
    wx,_,wz=R.p(u,0,0)
    if row==0 and 285<wx<303 and wz>-3078:continue
    R.box('lx-glass',(u,y+.92,-.035),(2.48,1.84,.08))
    for du in [-1.27,0,1.27]:R.box('lx-iron',(u+du,y+.92,-.105),(.075,1.98,.10))
    for yy in [y-.05,y+1.88]:R.box('lx-cornice',(u,yy,-.10),(2.72,.13,.23))
    rail(R,u,y-.05,-.40,2.68)
    R.box('lx-cornice',(u,y-.12,-.24),(2.8,.13,.55))
 # Two open shaft elevations with real openings, landings and switchback flights.
 for R,w in [(Frame(B,257.1,-3085,math.pi/2,y=0),15.5),(Frame(B,260.1,-3076.25,math.pi,y=0),5.8)]:
  openingw=w-1.6;radius=openingw/2;spring=16.2-radius
  archpts=[(-openingw/2,.2),(openingw/2,.2),(openingw/2,spring)]+[(radius*math.cos(t),spring+radius*math.sin(t))for t in np.linspace(0,math.pi,30)[1:]]+[(-openingw/2,.2)]
  face=box(-w/2,0,w/2,16.8).difference(Polygon(archpts))
  for tri in triangles(face):B.face('lx-stucco',[R.p(x,y,0)for x,y in list(tri.exterior.coords)[:-1]],True)
  R.path('lx-iron',[(x,y,-.055)for x,y in archpts[2:-1]],.06,10)
 # Interior stair geometry is deliberately separate from the closed hotel guest corridors.
 S=Frame(B,260,-3091,0,y=0)
 for level in range(5):
  y=.18+level*3.15;S.box('lx-cornice',(0,y-.09,1),(5.1,.18,2.0),True)
  rail(S,0,y,0,4.9)
  if level<4:
   S.stairs(-1.25,2,1.9,1.575,4.6,y=y)
   S.box('lx-cornice',(0,y+1.485,7.1),(5.1,.18,1.3),True)
   T=Frame(B,*[S.p(1.25,0,6.45)[i]for i in [0,2]],math.pi,y=0)
   T.stairs(0,0,1.9,1.575,4.6,y=y+1.575)
 # Shaft guards continue across the open west elevation at each landing.
 W=Frame(B,256.95,-3085,math.pi/2,y=0)
 for y in [.18,3.33,6.48,9.63,12.78]:rail(W,0,y,0,15.0)
 for x,z in [(274,-3086),(289,-3087),(305,-3094)]:
  R=Frame(B,x,z,y=0);R.box('lx-cornice',(0,17.65,0),(3,.35,2.2));R.box('lx-metal',(0,18.15,0),(2.7,.7,1.9))
  for u in [-.65,.65]:R.lathe('lx-iron',u,0,[(18.51,.48),(18.56,.48)],20)
  for j in range(8):R.box('lx-iron',(-1.36,18.13,-.8+j*.23),(.025,.45,.045))
 # Low south arrival/lobby wing, inferred from aerial outline and official entry photo.
 L=Frame(B,294,-3063,math.pi+.0315,y=0)
 lobby=L.poly([(-7.2,0),(7.2,0),(7.2,12.3),(-7.2,12.3)])
 door=dict(p=L.p(1,.2,0),yaw=L.yaw,width=2.7,height=3.5,name='The Lexi public lobby',venue=KEY)
 B.shell(lobby,0,5.9,'lx-stucco',openings=[door],roof=False);hip(B,lobby.buffer(.35,join_style=2),5.9,1.45,.75)
 for u in [-5.9,-3.9,4.7]:
  L.box('lx-glass',(u,2.0,-.035),(1.5,2.5,.07));L.box('lx-iron',(u,2,-.09),(.06,2.55,.10))
 for u in [-.4,2.4]:L.box('lx-iron',(u,1.95,-.06),(.11,3.65,.14))
 L.box('lx-iron',(1,3.8,-.06),(2.9,.12,.14));L.text('THE LEXI',(1,4.45,-.09),.50,'lx-iron')
 L.box('lx-paving',(1,.10,-.7),(3.3,.20,1.5),True)
 B.upface('lx-paving',[L.p(-.65,0,-2),L.p(2.65,0,-2),L.p(2.65,.2,-1.4),L.p(-.65,.2,-1.4)],True)
 # Porte cochere to southwest: posts stay clear of the drive and lobby approach.
 C=Frame(B,280,-3065,math.pi+.0315,y=0)
 for u in [-5.6,5.6]:
  for v in [-3.4,3.4]:C.box('lx-stucco',(u,2.15,v),(.50,4.3,.50),True)
 C.box('lx-iron',(0,4.2,0),(12.2,.25,7.6));hip(B,C.poly([(-6.3,-4),(6.3,-4),(6.3,4),(-6.3,4)]),4.3,1.3,.75)
 # Pool courtyard: recessed basin, unobstructed deck and shallow end stairs.
 Q=Frame(B,248.0,-3073,0,y=0)
 pool=Q.poly([(-3.1,-7.0),(3.1,-7),(3.1,7),(-3.1,7)])
 deck=Q.poly([(-8,-10),(8,-10),(8,10),(-8,10)]).difference(pool)
 B.planar('lx-paving',deck,.13,True);B.shell(pool,-1.25,.13,'lx-basin',roof=False);B.planar('lx-basin',pool,-1.25,True);B.planar('lexi_pool',pool,.05) # Above retained city datum; eight centimetres below coping.
 for a,b in zip(list(pool.exterior.coords),list(pool.exterior.coords)[1:]):
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0);R.box('lx-coping',(0,.13,0),(math.dist(a,b),.12,.33),True)
 for side in [-1,1]:
  for j in range(4):Q.box('lx-basin',(0,-.03-j*.21,side*(6.65-j*.38)),(5.9,.22,.4),True)
 for z in [-5,-1.7,1.7,5]:
  Q.box('lx-iron',(5.7,.31,z),(2.3,.24,1.7),True);Q.box('lx-cushion',(5.7,.52,z),(2.25,.18,1.6));Q.box('lx-cushion',(6.4,.8,z),(.5,.5,1.6))
  for u in [-7.2,-4.4]:Q.tube('lx-iron',(u,.13,z-1.3),(u,2.7,z-1.3),.045,8)
  corners=[Q.p(-7.5,2.7,z-1.5),Q.p(-4.1,2.7,z-1.5),Q.p(-4.1,2.7,z+1.5),Q.p(-7.5,2.7,z+1.5)]
  for i in range(4):B.face('lx-fabric',[corners[i],corners[(i+1)%4],Q.p(-5.8,3.5,z)])
 # Original fan palms: tapered segmented trunks and individually folded fronds.
 for i,(x,z,h) in enumerate([(240,-3078,8.5),(240,-3065,9),(258,-3065,10),(264,-3066,11),(277,-3063,9),(306,-3065,10)]):
  R=Frame(B,x,z,y=0);R.lathe('bark',0,0,[(.12,.28),(h*.4,.23),(h,.16)],12)
  for yy in np.arange(.5,h,.22):R.lathe('lx-wood',0,0,[(float(yy),.24),(float(yy)+.055,.25)],10)
  for j in range(24):
   a=j*2.399+i;length=2.7+(j%4)*.28;pts=[]
   for k in range(13):
    t=k/12;r=length*t;pts.append(R.p(r*math.cos(a),h+.85*math.sin(t*math.pi)-1.25*t,r*math.sin(a)))
   B.path('lx-leaf',pts,.021,6)
   # Individual narrow leaflets arc from the midrib, with a folded centre.
   for k in range(2,12):
    c=pts[k];w=.72*math.sin(k/12*math.pi)
    for side in [-1,1]:
     tip=(c[0]+side*w*math.sin(a)+.22*math.cos(a),c[1]-.28,c[2]-side*w*math.cos(a)+.22*math.sin(a))
     mid=tuple((c[q]+tip[q])/2 for q in range(3));ridge=(mid[0],mid[1]+.065,mid[2])
     edge=(mid[0]-.055*math.cos(a),mid[1]-.02,mid[2]-.055*math.sin(a))
     edge2=(mid[0]+.055*math.cos(a),mid[1]-.02,mid[2]+.055*math.sin(a))
     mat='lx-green' if (j+k)%3 else 'lx-leaf'
     for face in [[c,edge,ridge],[c,ridge,edge2],[edge,tip,ridge],[ridge,tip,edge2]]:B.face(mat,face)
 # Public lobby: observed seating island, foliage doorway, mezzanine and stair.
 B.property=KEY+'-interior';B.source='public/'+KEY
 # Public floor clears retained mapped service-road/sidewalk surfaces (max .28m).
 L.y=.3
 B.upface('lx-floor',[L.p(-.3,-.1,-.4),L.p(2.3,-.1,-.4),L.p(2.3,.2,.5),L.p(-.3,.2,.5)],True)
 room=lobby.buffer(-.12);B.planar('lx-floor',room,.5,True);B.shell(room,.5,5.75,'lx-wall',openings=[door],roof=False)
 for tri in triangles(room):B.face('lx-wall',[(x,5.75,z)for x,z in reversed(list(tri.exterior.coords)[:-1])])
 # Black tile inset rather than coplanar overlays on an uncut floor.
 inset=L.poly([(-4,3),(3.5,3),(3.5,10),(-4,10)])
 # Inset is raised 3cm; decorative joints cannot trip the capsule.
 B.planar('lx-blacktile',inset,.53)
 for u in np.arange(-3.5,3.5,.75):L.box('lx-grout',(float(u),.234,6.5),(.008,.006,7))
 for v in np.arange(3.5,10,.75):L.box('lx-grout',(-.25,.234,float(v)),(7.5,.006,.008))
 for u,v,a in [(-2.8,4.7,-.3),(1.8,4.7,.3),(-2.8,8.2,math.pi+.3),(1.8,8.2,math.pi-.3)]:chair(L,u,v,a)
 L.box('lx-iron',(-.5,.47,6.5),(2.5,.12,1.1),True)
 for u in [-1.5,.5]:L.box('lx-metal',(u,.34,6.5),(.06,.24,.8))
 L.box('lx-green',(-5.7,.55,8.3),(1.1,.40,4.0),True);L.box('lx-green',(-6.15,1.0,8.3),(.2,.9,4))
 for v in np.arange(6.4,10.2,.22):L.box('lx-green',(-6.02,1.0,float(v)),(.15,.8,.13))
 L.box('lx-wood',(-3.8,1.65,12.07),(1.8,2.9,.11),True)
 for u in [-4.5,-3.1]:
  for yy in [.9,2.1]:L.box('lx-art',(u,yy,11.99),(.55,.90,.045))
 # Original abstract relief replaces photographed art, never a copied image or sculpture.
 L.box('lx-leaf',(-3.8,3,12.12),(3.7,5.3,.12))
 for j in range(500):
  u=-5.5+(j%25)*.145;yy=.48+(j//25)*.255
  if -4.8<u<-2.8 and yy<3.2:continue
  a=j*2.399;cx=u+.055*math.sin(a);cy=yy+.07*math.cos(a);v=11.93-.04*(j%3)
  B.face('lx-green'if j%3 else'lx-leaf',[L.p(cx-.10,cy-.06,v),L.p(cx,cy+.15,v-.06),L.p(cx+.11,cy+.03,v),L.p(cx,cy-.14,v-.03)])
 L.box('lx-metal',(-6.95,3.7,8.3),(.08,2.2,2.5));L.box('lx-art',(-6.87,3.7,8.3),(.06,2.0,2.3))
 for j in range(9):L.box('lx-wood',(-6.82,3.05+j*.15,7.5+j*.18),(.04,.09,.6))
 L.stairs(5.2,5.0,1.8,2.7,4.5,y=.2)
 L.box('lx-floor',(3.9,2.80,10.8),(6.0,.2,2.7),True);rail(L,2.5,2.9,9.45,3.2);rail(L,6.6,2.9,9.45,.6)
 for u in [-4,0,4]:
  for v in [2,6,11]:L.lathe('lx-lamp',u,v,[(5.36,.11),(5.40,.11)],12)
 routes=[dict(name='Arrival to public lobby',points=[L.p(1,-.3,-5),L.p(1,-.3,-2),L.p(1,-.1,-1.4),L.p(1,.2,1.5),L.p(4,.2,3.3),L.p(4,.2,5.2)]),dict(name='Lobby seating circulation',points=[L.p(u,.2,v)for u,v in [(4,3.3),(-4.8,2),(-4.8,4),(-4.8,10.8),(3.8,9),(3.8,6)]]),dict(name='Lobby mezzanine stair',points=[L.p(5.2,.2,4.6),L.p(5.2,.2,5.0),L.p(5.2,2.9,9.5),L.p(5.2,2.9,10.8),L.p(2.0,2.9,10.8)]),dict(name='Pool east deck',points=[Q.p(3.8,.13,z)for z in [-8,-4,0,4,8]])]
 return dict(key=KEY,name='The Lexi',center=(283,0,-3083),bounds=list(unary_union([p,lobby,deck]).buffer(3).bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=L.p(0,.2,.12),yaw=L.yaw,width=14.1,depth=12.05,height=5.25)],lights=[dict(p=L.p(u,5.1,v),color=0xffeee0,power=1,range=12)for u,v in [(-4,3),(4,3),(-4,11),(4,11)]],routes=routes)
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
