"""Original photo-fitted public restaurant; room arrangement inferred, private rooms excluded."""
from common import *
from shapely.ops import triangulate,voronoi_diagram
from shapely.geometry import GeometryCollection,MultiPoint
KEY='los-amores-julia-sahara';IDS=['way/276426262']
def build(B):
 p=footprint(IDS[0]);B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 R=Frame(B,-166.19,-3194.35,-math.pi/2,y=0)
 door=dict(p=R.p(0,.15,0),yaw=-math.pi/2,width=2,height=2.7,name='Los Amores public dining',venue=KEY)
 B.shell(p,0,4,'aj-stucco',roof=False,openings=[dict(p=R.p(0,.15,0),width=2.2,height=2.85)])
 # Perimeter pitched tile apron and flat equipment well follow the mapped footprint.
 inner=p.buffer(-3,join_style=2)
 for t in triangulate(GeometryCollection([p.boundary,inner.boundary])):
  if p.buffer(.00001).covers(t):
   pts=[(x,4.04+min(Point(x,z).distance(p.boundary),3)*.48,z) for x,z in list(t.exterior.coords)[:-1]];B.upface('aj-tile',pts)
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  length=math.dist(a,b)
  if length<.5:continue
  dx=(b[0]-a[0])/length;dz=(b[1]-a[1])/length;nx,nz=-dz,dx
  mid=Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)
  if not p.contains(mid):nx,nz=-nx,-nz
  B.tube('aj-dark',(a[0],4,a[1]),(b[0],4,b[1]),.10,7)
  for d in np.arange(.18,length-.1,.28):
   x,z=a[0]+dx*d,a[1]+dz*d
   q=Point(x+nx*2.7,z+nz*2.7)
   if p.covers(q):B.tube('aj-tilecap',(x,4.12,z),(q.x,4.12+min(q.distance(p.boundary),3)*.48,q.y),.065,7)
 B.planar('aj-membrane',inner,5.5)
 # Layered gable entry with original irregular stone joints; historic envelope, fitted signage.
 for u in [-1.55,1.55]:R.box('aj-joint',(u,1.9,-.08),(.9,3.8,.28),True)
 B.face('aj-joint',[R.p(-2.25,3.05,-.23),R.p(2.25,3.05,-.23),R.p(2.25,4.2,-.23),R.p(0,5.6,-.23),R.p(-2.25,4.2,-.23)])
 def stone(region,v,seed):
  rng=random.Random(seed);x0,y0,x1,y1=region.bounds
  points=[(float(x)+rng.uniform(-.15,.15),float(y)+rng.uniform(-.13,.13))for y in np.arange(y0-.6,y1+.6,.42)for x in np.arange(x0-.6,x1+.6,.48)]
  for cell in voronoi_diagram(MultiPoint(points)).geoms:
   q=cell.buffer(-.014,join_style=2).intersection(region);mat='aj-stone'+str(rng.randrange(3))
   for part in parts(q):
    for t in triangles(part):B.face(mat,[R.p(x,y,v)for x,y in list(t.exterior.coords)[:-1]])
 region=Polygon([(-2.25,.15),(2.25,.15),(2.25,4.2),(0,5.6),(-2.25,4.2)]).difference(box(-1.12,0,1.12,3.1))
 stone(region,-.255,23)
 # Taller second gable establishes the layered silhouette visible in the dated reference.
 rear=Polygon([(-4,4.1),(4,4.1),(4,5.1),(0,7.0),(-4,5.1)])
 B.face('aj-joint',[R.p(x,y,3.1)for x,y in list(rear.exterior.coords)[:-1]])
 stone(rear,3.08,31)
 for u in [-4.2,4.2]:
  B.upface('aj-tile',[R.p(u,5.03,2.9),R.p(0,7.12,2.9),R.p(0,7.12,7),R.p(u,5.03,7)])
  R.tube('aj-dark',(u,5.09,2.9),(0,7.18,2.9),.12,8)
 R.arch(0,-.34,2.3,3.5,'aj-dark',.10,base=.15)
 for u in [-2.5,2.5]:
  B.upface('aj-tile',[R.p(u,4.05,-.55),R.p(0,5.7,-.55),R.p(0,5.7,3),R.p(u,4.05,3)])
  R.tube('aj-dark',(u,4.1,-.55),(0,5.74,-.55),.12,8)
 for a,b in zip(np.linspace(0,math.tau,25),np.linspace(0,math.tau,25)[1:]):R.tube('aj-dark',(.32*math.cos(a),4.48+.32*math.sin(a),-.29),(.32*math.cos(b),4.48+.32*math.sin(b),-.29),.045,6)
 B.face('aj-dark',[R.p(.29*math.cos(a),4.48+.29*math.sin(a),-.29)for a in np.linspace(0,math.tau,25)])
 R.box('aj-dark',(0,3.63,-.38),(3.6,.43,.08));R.text('LOS AMORES DE JULIA',(0,3.51,-.44),.25,'aj-letter')
 # Individual windows follow irregular east/south walls, with dark surrounds.
 for x,z,yaw,w in [(-168.52,-3201.5,-math.pi/2,2.4),(-168.87,-3188.5,-math.pi/2,2.3),(-180,-3183.20,math.pi,3),(-187,-3183.25,math.pi,3),(-196.05,-3192,math.pi/2,2),(-195.95,-3202,math.pi/2,2)]:
  F=Frame(B,x,z,yaw,y=0);F.box('aj-dark',(0,2,-.10),(w+.2,2.35,.12));F.box('aj-window',(0,2,-.18),(w,2.15,.035))
  for y in [1.2,2.8]:F.box('aj-mullion',(0,y,-.22),(w,.055,.06))
 for u,v in [(-8,12),(8,12)]:R.box('aj-stucco',(u,5.3,v),(1.4,3.0,1.4));R.box('aj-dark',(u,6.9,v),(1.6,.25,1.6))
 for x,z in [(-183,-3193),(-182,-3200),(-188,-3198)]:
  F=Frame(B,x,z,0,y=0);F.box('aj-service',(0,6,0),(2,1,1.6));F.box('aj-alloy',(0,6.55,0),(2.1,.1,1.7))
  for u in [-.55,.55]:F.lathe('aj-dark',u,0,[(6.62,0),(6.62,.35),(6.65,.35),(6.65,0)],16)
 for u in [-7,7]:R.plant(u,1.5)
 for x in [-179,-190]:Frame(B,x,-3181.3,0,y=0).plant(0,0,palm=True)
 R.box('aj-paving',(0,.075,-1.8),(5,.15,3.6),True)
 B.upface('aj-paving',[R.p(-1.1,.15,-3.6),R.p(1.1,.15,-3.6),R.p(1.1,0,-5.1),R.p(-1.1,0,-5.1)],True)
 for u in [-2.25,2.25]:R.box('aj-red',(u,.1,-2.0),(.15,.2,3.7),True)
 # Public dining room with a narrow entrance vestibule; fitted, not a surveyed floor plan.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=unary_union([R.poly([(-11,6.4),(10,6.4),(10,27.5),(-11,27.5)]),R.poly([(-1.4,.25),(1.4,.25),(1.4,6.5),(-1.4,6.5)])])
 assert p.buffer(.1).covers(room)
 B.shell(room,.15,4.0,'aj-inwall',roof=False,openings=[dict(p=R.p(0,.15,.25),width=2.2,height=2.85)])
 B.planar('aj-floor',room,.15,True);B.planar('aj-dark',room,4.02)
 for u in [-9,-5,0,5,9]:R.box('aj-dark',(u,3.87,17),( .14,.3,20.8))
 for v in [8,12,16,20,24]:R.box('aj-dark',(-.5,3.85,v),(20.7,.32,.16))
 # Woven overhead panels, original hanging leaf forms and string lights.
 for u in [-7,0,7]:
  for v in [10,17,24]:
   R.box('aj-weave',(u,3.65,v),(4,.06,2.4))
   for d in np.arange(-1.95,2,.13):R.tube('aj-straw',(u+float(d),3.61,v-1.2),(u+float(d),3.61,v+1.2),.018,5)
   for du in [-1.5,1.5]:
    for dv in [-1,1]:
     for j in range(7):
      y=3.55-j*.10;xx=u+du+.08*math.sin(j);zz=v+dv
      for side in [-1,1]:B.face('aj-leaf',[R.p(xx,y,zz),R.p(xx+side*.18,y-.13,zz+.03),R.p(xx+side*.04,y-.2,zz+.06)],False)
   profile=[(2.8,.48),(3.0,.55),(3.2,.46),(3.4,.22),(3.45,.1)]
   for a in np.linspace(0,math.tau,21):R.path('aj-straw',[(u+r*math.cos(a),y,v+r*math.sin(a))for y,r in profile],.012,5)
   for y in np.arange(2.8,3.46,.065):
    radius=float(np.interp(y,[q[0]for q in profile],[q[1]for q in profile]))
    R.path('aj-pendant',[(u+radius*math.cos(a),float(y),v+radius*math.sin(a))for a in np.linspace(0,math.tau,25)],.012,5)
   R.lathe('aj-lamp',u,v,[(2.86,0),(2.86,.12),(3.15,.12),(3.15,0)],12)
 for v in [9,15,21,26]:
  R.tube('aj-dark',(-10,3.6,v),(9,3.6,v),.012,5)
  for u in np.arange(-9,10,1.4):R.lathe('aj-lamp',float(u),v,[(3.4,0),(3.42,.045),(3.52,.05),(3.55,0)],7)
 # Wood tables and curved woven-backed chairs keep the central route open.
 def chair(u,v,yaw):
  Q=R.p(u,0,v);C=Frame(B,Q[0],Q[2],R.yaw+yaw,y=0)
  C.box('aj-leather',(0,.61,0),(.58,.12,.55),True)
  for x in [-.24,.24]:
   for z in [-.22,.22]:C.tube('aj-wood',(x,.18,z),(x,.58,z),.035,7)
  pts=[(.34*math.cos(a),1.05,.1+.3*math.sin(a))for a in np.linspace(0,math.pi,13)]
  C.path('aj-leather',pts,.065,8)
  for x,y,z in pts:C.tube('aj-woven',(x,.64,z),(x,1.03,z),.018,5)
 for u in [-7.4,-3.8,3.8,7.4]:
  for v in [10,15,20]:
   R.box('aj-wood',(u,.95,v),(1.7,.1,1.15),True)
   for du in [-.65,.65]:
    for dv in [-.4,.4]:R.tube('aj-dark',(u+du,.15,v+dv),(u+du,.9,v+dv),.04,6)
   for du,dv,yaw in [(-.44,-.95,math.pi),(.44,-.95,math.pi),(-.44,.95,0),(.44,.95,0)]:chair(u+du,v+dv,yaw)
   R.lathe('aj-pot',u,v,[(1.01,.11),(1.22,.14),(1.24,.13)],12)
   for a in np.linspace(0,math.tau,6):R.tube('aj-leaf',(u,1.22,v),(u+.18*math.cos(a),1.47,v+.18*math.sin(a)),.025,5)
 # Photo-supported public tortilla counter and brick arch; service space remains closed.
 R.box('aj-mortar',(-.5,1.95,27.35),(20.8,3.6,.14))
 for y in np.arange(.35,3.8,.24):
  for j,u in enumerate(np.arange(-10.7,9.8,.52)):
   u=float(u)+(.26 if int(y/.24)%2 else 0)
   R.box('aj-brick'+str(j%3),(u,float(y),27.25),(.49,.215,.025))
 for u in [-4.4,3.6]:R.tube('aj-dark',(u,.15,27.10),(u,2.7,27.10),.20,8)
 R.path('aj-dark',[(-.4+4*math.cos(a),2.7+math.sin(a),27.10)for a in np.linspace(0,math.pi,33)],.20,8)
 R.box('aj-wood',(-.4,.8,26.4),(8,1.3,1),True);R.box('aj-counter',(-.4,1.48,26.4),(8.2,.12,1.1))
 R.text('TORTILLERIA',(-.4,2.8,27.10),.5,'aj-letter')
 for u in [-2.5,0,2.5]:R.lathe('aj-pot',u,26.4,[(1.55,.28),(1.84,.3),(1.9,.32)],18)
 R.box('aj-dark',(-8.5,1.4,26.5),(2,2.5,.9),True)
 for y in [.5,1,1.5,2]:
  R.box('aj-alloy',(-8.5,y,25.99),(1.8,.06,.08))
  for u in [-9.1,-8.7,-8.3,-7.9]:R.lathe('aj-bottle',u,26.1,[(y+.05,.06),(y+.3,.06),(y+.38,.025)],8)
 for u in [-6,6]:R.box('aj-dark',(u,3.1,26.9),(2,.95,.08));R.box('aj-screen',(u,3.1,26.84),(1.86,.81,.02))
 routes=[dict(name='Entry to public dining',points=[R.p(0,y,v) for y,v in [(0,-5.6),(0,-5.1),(.15,-3),(.15,0),(.15,4),(.15,9),(.15,18),(.15,23.8)]]),dict(name='Public counter cross aisle',points=[R.p(u,.15,23.8)for u in [0,-4,-8]])]
 return dict(key=KEY,name='Los Amores de Julia Sahara',center=[-181,0,-3198],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(-.5,.15,6.4),yaw=R.yaw,width=21,depth=21.1,height=4),dict(origin=R.p(0,.15,.2),yaw=R.yaw,width=2.8,depth=6.2,height=4)],lights=[dict(p=R.p(u,3.4,v),color=0xffdfaf,power=3,range=11)for u,v in [(-5,11),(5,11),(-5,23),(5,23)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
