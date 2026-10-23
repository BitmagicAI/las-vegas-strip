"""Local, reference-led public-floor expansion. See RESORT-INTERIORS.md."""
import sys,os,math,json,ast,random
from pathlib import Path
sys.path.insert(0,'tools/blender-level');sys.path.insert(0,'tools/level')
from bmlevel import *
from bmlevel.core import HullCollider,Stairs
import bpy
from mathutils import Vector
from geometry_quality import orient_closed_solids
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/interiors/baseline.blend'))
scene.materials.update({m.name:m for m in bpy.data.materials})
data=json.loads(Path('build/interiors/baseline.mesh-level.json').read_text())
old_doors=json.loads(Path('build/interiors/baseline.doors.json').read_text())
P='Interiors / ';serial=0;labels=[];rng=random.Random(2909)
def uid(n):
 global serial
 serial+=1;return P+f'{serial:05d} '+n
for n,c,metal,rough,em in [('ivory',(.67,.60,.47),0,.63,0),('marble',(.36,.34,.30),.1,.3,0),('dark',(.034,.035,.039),.35,.45,0),('gold',(.52,.32,.10),.7,.27,0),('pink',(.27,.034,.09),.05,.76,0),('red',(.17,.016,.023),0,.9,0),('blue',(.022,.08,.14),.05,.7,0),('felt',(.025,.105,.075),0,.96,0),('wood',(.13,.055,.025),0,.7,0),('glass',(.07,.16,.19),.65,.22,0),('water',(.015,.15,.18),.45,.18,0),('light',(1,.67,.32),.1,.3,2),('screen',(.035,.24,.31),.2,.3,1.2),('sky',(.18,.25,.38),0,.8,.18),('statue',(.65,.61,.49),.05,.77,0)]:mat('ri_'+n,c,metal=metal,roughness=rough,glow=em)
def B(n,p,s,m='ivory',**kw):box(uid(n),p,s,'ri_'+m,**kw)
def D(n,p,s,m='gold',**kw):decor(uid(n),p,s,'ri_'+m,**kw)
def floor(n,x,z,w,d,y=.075):slab(uid(n),(x,z),(w,d),'ri_marble',y=y,thickness=.3)
def sign(s,p,size=.65,yaw=0,max_width=None):
 cr=bpy.data.curves.new(uid(s),'FONT');cr.body=s;cr.align_x='CENTER';cr.size=size;cr.extrude=.009
 ob=bpy.data.objects.new(cr.name,cr);scene.collection.objects.link(ob);ob.location=(p[0],-p[2],p[1]);ob.rotation_euler=(math.pi/2,0,yaw);cr.materials.append(bpy.data.materials['ri_light']);labels.append(ob)
 if max_width:
  bpy.context.view_layer.update();cr.size*=min(1,max_width/max(ob.dimensions.x,.001))
def mesh(n,vs,fs,m='ivory',solid=False):
 name=uid(n);me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y) for x,y,z in vs],[],fs);me.update();ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);me.materials.append(bpy.data.materials['ri_'+m])
 if solid:level.colliders.append(HullCollider(name,[v for p in vs for v in p]))
 return ob
def lathe(n,x,z,profile,m='gold',count=24):
 vs=[(x+r*math.cos(i*math.tau/count),y,z+r*math.sin(i*math.tau/count)) for r,y in profile for i in range(count)]
 fs=[(j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i) for j in range(len(profile)-1) for i in range(count)];fs += [tuple(reversed(range(count))),tuple(range((len(profile)-1)*count,len(profile)*count))]
 return mesh(n,vs,fs,m)
def limb(n,a,b,r,m='statue'):
 a=Vector(a);b=Vector(b);v=b-a;q=v.to_track_quat('Y','Z');vs=[]
 for p in [a,b]:
  for i in range(12):vs.append(tuple(p+q@Vector((r*math.cos(i*math.tau/12),0,r*math.sin(i*math.tau/12)))))
 return mesh(n,vs,[tuple(reversed(range(12))),tuple(range(12,24))]+[(i,(i+1)%12,(i+1)%12+12,i+12) for i in range(12)],m)
def ellipsoid(n,p,r,m='statue'):
 vs=[]
 for j in range(13):
  t=math.pi*j/12
  for i in range(20):
   a=math.tau*i/20;vs.append((p[0]+r[0]*math.sin(t)*math.cos(a),p[1]+r[1]*math.cos(t),p[2]+r[2]*math.sin(t)*math.sin(a)))
 return mesh(n,vs,[(j*20+i,j*20+(i+1)%20,(j+1)*20+(i+1)%20,(j+1)*20+i) for j in range(12) for i in range(20)],m)
def column(x,z,h=10,y=0):
 lathe('fluted column',x,z,[(.7,y),(.7,y+.25),(.45,y+.55),(.39,y+h-.6),(.7,y+h-.45),(.7,y+h)],'ivory')
 for j in range(12):
  a=j*math.tau/12;limb('flute',(x+.405*math.cos(a),y+.7,z+.405*math.sin(a)),(x+.405*math.cos(a),y+h-.7,z+.405*math.sin(a)),.025,'gold')
 B('column collision',(x,y+h/2,z),(.85,h,.85))
def node(n,p):volume(P+n,(p[0],p[1]+1.5,p[2]),(1,3,1),roofed=False,tags=['route'])
def route(n,points):
 for i,p in enumerate(points):node(n+str(i),p)
 for i in range(len(points)-1):link(P+n+str(i),P+n+str(i+1))
def light(n,x,z,y=7,color='#ffd5a5',intensity=160,distance=24):
 lamp(uid(n),(x,y,z),color,intensity,distance);D('ceiling light',(x,y+.18,z),(1.6,.08,1.6),'light')
def doorway(n,axis,coord,lo,hi,at,h=12,w=5,base=0):
 # wall segments with automatic sliding leaf; h is total wall height.
 for a,b in [(lo,at-w/2),(at+w/2,hi)]:
  if b>a:B(n+' wall',(coord,base+h/2,(a+b)/2) if axis=='x' else ((a+b)/2,base+h/2,coord),(.5,h,b-a+.025) if axis=='x' else (b-a+.025,h,.5))
 B(n+' header',(coord,base+(h+4.2)/2,at) if axis=='x' else (at,base+(h+4.2)/2,coord),(.55,h-4.2,w+.05) if axis=='x' else (w+.05,h-4.2,.55))
 pos=(coord,base+.075,at) if axis=='x' else (at,base+.075,coord)
 door(P+n,pos,width=w,height=4.1,yaw=math.pi/2 if axis=='x' else 0,animation='slide',auto_open_radius=6)
def shell(n,x0,x1,z0,z1,h=12,entry=None,exit=None):
 floor(n+' floor',(x0+x1)/2,(z0+z1)/2,x1-x0+.5,z1-z0+.5)
 floor(n+' ceiling',(x0+x1)/2,(z0+z1)/2,x1-x0+.5,z1-z0+.5,h+.4)
 for side,axis,c,lo,hi in [('west','x',x0,z0,z1),('east','x',x1,z0,z1),('north','z',z0,x0,x1),('south','z',z1,x0,x1)]:
  a=next((a for a in [entry,exit] if a and a[0]==side),None)
  if a:doorway(n+' '+side,axis,c,lo,hi,a[1],h=h)
  else:B(n+' '+side+' wall',(c,h/2,(lo+hi)/2) if axis=='x' else ((lo+hi)/2,h/2,c),(.5,h,hi-lo+.2) if axis=='x' else (hi-lo+.2,h,.5))
 volume(P+n+' envelope',((x0+x1)/2,h/2+.075,(z0+z1)/2),(x1-x0,h,z1-z0),tags=['indoors','public'])
 for x in range(math.ceil(x0+8),int(x1-4),18):
  for z in range(math.ceil(z0+7),int(z1-3),18):light(n,x,z,h-1.4)
 for z in [z0+.4,z1-.4]:D('continuous cove',((x0+x1)/2,h-.6,z),(x1-x0-.5,.10,.12),'light')
def slots(n,x,z,theme='pink',count=4):
 for i in range(count):
  xx=x+i*1.6;B(n+' slot cabinet',(xx,1.1,z),(1.15,2.1,.85),'dark')
  D('cabinet surround',(xx,1.6,z-.47),(1.04,1.08,.12),theme);D('screen',(xx,1.6,z-.55),(.85,.78,.055),'screen');D('console',(xx,.92,z-.62),(1.1,.15,.55),'gold')
  for dx in [-.26,0,.26]:D('slot reel',(xx+dx,1.65,z-.59),(.14,.3,.02),'light')
  lathe('slot stool',xx,z-1.3,[(.3,0),(.1,.55),(.35,.6),(.35,.78)],theme,12)
def table(x,z):
 B('gaming pedestal',(x,.55,z),(1.5,1.1,1.2),'wood');D('gaming table',(x,1.15,z),(3.8,.22,2.4),'wood',bevel=.2);D('felt',(x,1.29,z),(3.5,.04,2.1),'felt')
 for dx in [-1.3,0,1.3]:
  lathe('table chair',x+dx,z-1.9,[(.27,0),(.1,.5),(.35,.6),(.35,.78)],'red',12)
  D('card',(x+dx,1.32,z),(.12,.015,.18),'ivory')
def registration(n,x,z,w=9,theme='gold'):
 B(n+' registration counter',(x,.65,z),(w,1.3,1.1),'wood');D('stone counter',(x,1.34,z),(w+.2,.12,1.3),'marble')
 for xx in [x-w*.3,x,x+w*.3]:D('reception monitor',(xx,1.63,z+.1),(.65,.45,.1),'dark')
 sign(n+' / REGISTRATION',(x,3,z+.7),.5)
def shop(n,x,z,w=9,d=8,y=0,theme='gold',label=None):
 # Open south-facing retail bay, three solid walls and a generous entry.
 floor(n+' shop floor',x,z,w,d,y+.09)
 for xx in [x-w/2,x+w/2]:B(n+' shop return',(xx,y+1.9,z),(.22,3.8,d),'ivory')
 B(n+' shop back',(x,y+1.9,z-d/2),(w,3.8,.22),'ivory')
 for side in [-1,1]:
  inner=2.28;outer=w/2-.15;xx=x+side*(inner+outer)/2;B(n+' display window base',(xx,y+.35,z+d/2),(outer-inner,.7,.3),theme)
  D(n+' window',(xx,y+2,z+d/2),(outer-inner,2.6,.08),'glass')
 D(n+' fascia',(x,y+3.7,z+d/2),(w,.55,.4),theme);sign(label or n,(x,y+3.58,z+d/2+.23),min(.43,w/25),max_width=3.5)
 for yy in [.55,1.4,2.3]:
  D('shop shelf',(x,y+yy,z-d/2+.65),(w-1,.12,.8),'wood')
  for dx in [-w*.3,0,w*.3]:D('display merchandise',(x+dx,y+yy+.25,z-d/2+.65),(.55,.45,.45),theme)
 B(n+' sales desk',(x-w*.28,y+.6,z+.5),(2,1.2,1),'wood')
 route(n+' shop entry',[(x,y+.1,z+d/2+1),(x,y+.1,z+1.6)]);landmark(P+n+' supplies',(x,y+.1,z),tags=['supply-reserve','shop'])
def straight(n,x,z,rise=6,run=14,width=3,y=.075,escalator=False):
 with context(P+n):stairs(P+n,(x,y,z),rise,run,'ri_dark' if escalator else 'ri_marble',width=width,rail='ri_gold')
 # Tread edges and glass/metal balustrades are static after the apocalypse.
 steps=math.ceil(rise/.18)
 for i in range(steps):D('tread nosing',(x,y+(i+1)*rise/steps+.01,z+(i+.05)*run/steps),(width,.035,.07),'gold')
 route(n+' ascent',[(x,y,z-.7),(x,y+rise,z+run+.7)])
 sign('UPPER GALLERY',(x,y+2.5,z-.5),.4,math.pi)
def guard(n,x,z,w,d,y,open_south=None):
 # Clear solid parapets around mezzanines; south opening reserved for stairs.
 for xx in [x-w/2,x+w/2]:B(n+' balustrade',(xx,y+.55,z),(.18,1.1,d),'gold')
 B(n+' back balustrade',(x,y+.55,z+d/2),(w,1.1,.18),'gold')
 a,b=x-w/2,x+w/2
 if open_south is not None:
  for lo,hi in [(a,open_south-(5.8 if n=='Planet Hollywood mezzanine' else 2.1)),(open_south+(5.8 if n=='Planet Hollywood mezzanine' else 2.1),b)]:
   if hi>lo:B(n+' front balustrade',((lo+hi)/2,y+.55,z-d/2),(hi-lo,1.1,.18),'gold')
 else:B(n+' front balustrade',(x,y+.55,z-d/2),(w,1.1,.18),'gold')
def remove_names(names):
 bpy.data.batch_remove([o for o in bpy.data.objects if o.name in names]);data['colliders']=[c for c in data['colliders'] if c['name'] not in names]
def lift_mass(prefix,bottom=12.4):
 cs=[c for c in data['colliders'] if c['name']==prefix+' / mass']
 for c in cs:
  ob=bpy.data.objects.get(c['name']);oldbottom=c['position'][1]-c['size'][1]/2;top=c['position'][1]+c['size'][1]/2
  # Bake the world vertices so existing bevels and material UVs survive.
  if ob:
   inv=ob.matrix_world.inverted()
   for v in ob.data.vertices:
    p=ob.matrix_world@v.co;p.z=bottom+(p.z-oldbottom)*(top-bottom)/(top-oldbottom);v.co=inv@p
  c['position'][1]=(top+bottom)/2;c['size'][1]=top-bottom
 # Old window bands and pilasters must not span new public openings.
 remove=[]
 for ob in bpy.data.objects:
  if not ob.name.startswith(prefix+' / ') or ob.name.endswith('/ mass') or ob.type!='MESH':continue
  pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];low=min(p.z for p in pts);high=max(p.z for p in pts)
  if high<bottom:remove.append(ob)
  elif low<bottom:
   inv=ob.matrix_world.inverted()
   for v in ob.data.vertices:
    p=ob.matrix_world@v.co;p.z=max(bottom,p.z);v.co=inv@p
 bpy.data.batch_remove(remove)

# Three previously solid resort blocks become traversable public floors.
for n in ['Flamingo hotel','Horseshoe north wing','Planet Hollywood resort']:lift_mass(n)
shell('Flamingo',90,200,-259,-215,entry=('west',-237),exit=('south',145))
D('Flamingo pink gaming carpet',(127,.105,-237),(68,.04,35),'pink')
for x in [98,115,132]:
 for z in [-250,-223]:slots('Flamingo',x,z)
for x in [105,124,141]:table(x,-244);table(x,-229)
registration('FLAMINGO',157,-251,12)
for z in [-254,-238,-222]:column(167,z,12)
for x,n in [(174,'FLAMINGO GIFTS'),(189,'GARDEN CAFE')]:shop(n,x,-251,12,12,theme='pink')
straight('Flamingo escalator',175,-237,6,14,3,escalator=True)
floor('Flamingo upper lounge',184,-219,29,8,6.075);guard('Flamingo gallery',184,-219,29,8,6.075,175)
registration('GARDEN LOUNGE',187,-217,8)
route('Flamingo public',[(86,.075,-237),(96,.075,-237),(153,.075,-237),(160,.075,-237),(160,.075,-219),(145,.075,-219),(145,.075,-211)])
route('Flamingo shops',[(160,.075,-237),(160,.075,-240),(175,.075,-240),(190,.075,-240)])
landmark(P+'Flamingo entrance',(86,.1,-237),tags=['entrance'])

shell('Horseshoe',92,128,-147,-85,entry=('north',110),exit=('south',110))
D('Horseshoe gaming carpet',(110,.11,-118),(31,.035,54),'red')
for z in [-139,-126]:slots('Horseshoe',96,z,'red',4)
for z in [-133,-115]:table(101,z)
registration('HORSESHOE',120,-91,9)
shop('AVENUE GIFTS',98,-101,9,8,theme='red')
straight('Horseshoe gallery stairs',123,-137,6,18,3)
floor('Horseshoe upper dining',119,-115,15,8,6.075);guard('Horseshoe upper',119,-115,15,8,6.075,123)
for x in [115,121]:D('dining table',(x,6.95,-113),(2,.18,1.5),'wood')
route('Horseshoe spine',[(110,.075,-151),(110,.075,-142),(110,.075,-108),(110,.075,-90),(110,.075,-82)])
route('Horseshoe stair approach',[(110,.075,-142),(123,.075,-142),(123,.075,-138)])
landmark(P+'Horseshoe entrance',(110,.1,-151),tags=['entrance'])

shell('Planet Hollywood',65,198,173,274,entry=('west',218),exit=('south',174))
D('Planet Hollywood casino carpet',(131,.11,218),(69,.04,58),'blue')
for x in [103,123,144]:
 for z in [199,239]:slots('Planet Hollywood',x,z,'blue',5)
for x in [106,122,151]:
 for z in [208,228]:table(x,z)
registration('PLANET HOLLYWOOD',78,201,13)
lathe('Heart Bar drum',135,218,[(4,.1),(4,1.2),(4.4,1.3),(4.4,1.45)],'gold',48);B('Heart Bar collision',(135,.7,218),(7,1.4,7),'dark');sign('HEART BAR',(135,3.4,218),.65)
for x in [82,101,121,141,161,184]:shop('MIRACLE MILE '+str(x),x,179,14,10,theme='blue')
for x in [103,122,143,162,186]:shop('MIRACLE MILE '+str(x)+' SOUTH',x,266,14,12,theme='red')
# Arcade on the east side: shallow open display bays between clear cross aisles.
for z in [202,224,246]:shop('MIRACLE MILE BOUTIQUE '+str(z),188,z,15,12,theme='gold')
for x in [79,85]:straight('Planet Hollywood escalator '+str(x),x,224,6,15,2.5,escalator=True)
floor('Planet Hollywood mezzanine',78,253,23,28,6.075);guard('Planet Hollywood mezzanine',78,253,23,28,6.075,82)
shop('MEZZANINE LOUNGE',78,260,18,11,y=6.075,theme='blue')
route('Planet Hollywood entry',[(61,.075,218),(72,.075,218),(96,.075,218),(119,.075,218)])
route('Miracle Mile circuit',[(94,.075,190),(174,.075,190),(174,.075,256),(94,.075,256),(94,.075,218),(94,.075,190)])
route('Miracle Mile exit',[(174,.075,256),(174,.075,278)])
route('Planet Hollywood stairs',[(72,.075,218),(79,.075,218),(79,.075,223)])
landmark(P+'Planet Hollywood entrance',(61,.1,218),tags=['entrance'])

# Paris-to-Horseshoe passage: replace the old solid northern casino end wall.
remove_names({c['name'] for c in data['colliders'] if 'Paris' in c['name'] and 'south envelope' in c['name']})
doorway('Paris Horseshoe passage','z',-80,72,138,110,h=8,w=5)
floor('Paris Horseshoe connector',110,-82.5,5.5,5.6)
B('connector roof',(110,5.2,-82.5),(5.5,.4,5.6))
for x in [107.25,112.75]:B('connector wall',(x,2.5,-82.5),(.3,5,5.5))
route('Paris connector',[(110,.075,-90),(110,.075,-76),(120,.075,-76),(120,.075,-68)])
registration('PARIS / LA RECEPTION',81,-25,9)
shop('LE BOULEVARD / PATISSERIE',131,-49,10,10,theme='gold')
shop('LE BOULEVARD / BOUTIQUE',131,-24,10,10,theme='blue')
straight('Paris upper gallery stairs',120,-68,4.2,13,3)
floor('Paris upper gallery',127.5,-49.5,19,11,4.275);guard('Paris upper gallery',127.5,-49.5,19,11,4.275,120)
D('Paris gallery seating',(132,4.8,-48),(4,.8,1.3),'red')
route('Le Boulevard',[(120,.075,-39),(120,.075,-18),(120,.075,5)])

# Cosmopolitan: ground registration and mezzanine beside the central gaming aisle.
registration('COSMOPOLITAN',-41,267,12)
straight('Cosmopolitan mezzanine stairs',-126,225,4.2,14,3)
floor('Cosmopolitan mezzanine',-125.5,246,21,14,4.275);guard('Cosmopolitan mezzanine',-125.5,246,21,14,4.275,-126)
shop('BOULEVARD LOUNGE',-125,247,16,6,y=4.275,theme='blue')
route('Cosmopolitan stair approach',[(-126,.075,242),(-139,.075,242),(-139,.075,222),(-126,.075,222),(-126,.075,224)])

# Forum Shops: casino-connected Roman shopping court north of Caesars.
remove_names({c['name'] for c in data['colliders'] if 'Caesars' in c['name'] and 'south casino wall' in c['name']})
doorway('Caesars Forum connection','z',-257,-174,-92,-120,h=8,w=6)
shell('Forum Shops',-174,-88,-296,-257,h=14)
# Shared south wall is replaced with the matching casino doorway, one leaf only.
remove_new=[c.name for c in level.colliders if 'Forum Shops south wall' in c.name]
level.colliders[:]=[c for c in level.colliders if c.name not in remove_new];bpy.data.batch_remove([o for o in bpy.data.objects if o.name in remove_new])
# Forum taller wall closes the space above the adjoining casino ceiling.
B('Forum south end closure',(-90,4,-257),(4,8,.5))
B('Forum south upper closure',(-131,11,-257),(86,6,.5))
for x,label in [(-162,'FORUM GIFTS'),(-144,'GALLERIA'),(-126,'BOUTIQUE')]:shop('FORUM ARCADE '+str(x),x,-290,14,10,theme='gold',label=label)
for x in [-168,-151,-133]:column(x,-282,13.6)
# Painted twilight ceiling and stepped cornices.
D('Forum painted sky',(-131,13.85,-276),(84,.04,37),'sky')
for z in [-295.5,-257.5]:
 for y in [11.7,12.2,12.7]:D('Forum layered cornice',(-131,y,z),(85,.22,.7),'ivory')
# Statuary court: original modeled draped figures with faces, limbs and attributes.
def statue(x,z,pose=0,scale=1):
 B('statue plinth',(x,.6,z),(2.2,1.2,2.2),'marble');lathe('statue pedestal',x,z,[(1.15,1.2),(.85,1.4),(.7,1.55)],'ivory')
 y=1.5
 for s in [-1,1]:
  limb('statue calf',(x+s*.22,y+.12,z),(x+s*.18,y+1.15,z),.16);limb('statue thigh',(x+s*.18,y+1.15,z),(x+s*.2,y+2,z),.23)
  ellipsoid('sandalled foot',(x+s*.22,y+.12,z+.13),(.19,.13,.35))
 ellipsoid('statue torso',(x,y+2.43,z),(.57,.78,.31));ellipsoid('statue head',(x,y+3.49,z),(.27,.36,.26));ellipsoid('nose',(x,y+3.48,z+.27),(.07,.11,.10))
 for s in [-1,1]:
  elbow=(x+s*.82,y+2.35+pose*.25,z+.1);hand=(x+s*(1.0 if s==1 else .72),y+(3.05 if s==1 else 1.95),z+.3)
  limb('upper arm',(x+s*.45,y+2.75,z),elbow,.17);limb('forearm',elbow,hand,.13);ellipsoid('hand',hand,(.12,.17,.1))
 # Toga: pleated asymmetric closed skirt, draped sash across the torso.
 vs=[];N=32
 for yy,r in [(y+.5,.5),(y+1.8,.47),(y+2.15,.42)]:
  for i in range(N):
   a=i*math.tau/N;rr=r+.035*(i%2);vs.append((x+rr*math.cos(a),yy,z+rr*.7*math.sin(a)))
 mesh('pleated toga',vs,[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(2) for i in range(N)],'statue')
 for j in range(7):limb('toga sash',(x-.48+j*.05,y+2.8,z+.28),(x+.35+j*.04,y+1.9,z+.27),.035)
 if pose==1:
  limb('trident shaft',(x+1,y+.2,z+.3),(x+1,y+4.1,z+.3),.045,'gold')
  for dx in [-.25,0,.25]:limb('trident tine',(x+1,y+3.7,z+.3),(x+1+dx,y+4.3,z+.3),.04,'gold')
 else:ellipsoid('laurel crown',(x,y+3.8,z),(.3,.08,.28),'gold')
lathe('Atlantis fountain basin',-147,-272,[(5.5,.08),(5.5,.55),(5,.65),(5,.2)],'marble',64)
lathe('Atlantis water',-147,-272,[(4.9,.24),(4.9,.26)],'water',64)
level.colliders.append(HullCollider(uid('fountain basin collider'),[v for y in [0,.55] for i in range(48) for v in (-147+5.5*math.cos(i*math.tau/48),y,-272+5.5*math.sin(i*math.tau/48))]))
for x,z,pose in [(-147,-273,1),(-151,-275,0),(-143,-275,2)]:statue(x,z,pose)
sign('ATLANTIS / COURT OF FOUNTAINS',(-147,1.0,-266.7),.35)
# Two curved flights, each with closed convex ramp segments and modeled treads.
def curved(n,r):
 cx,cz=-106,-276;N=48;width=2.1;rise=6.2;base=.075
 for i in range(N):
  a=i*math.pi/N;b=(i+1)*math.pi/N;lo=base+rise*i/N;hi=base+rise*(i+1)/N
  poly=[(cx+(r+s)*math.cos(t),cz+(r+s)*math.sin(t)) for s,t in [(-width/2,a),(width/2,a),(width/2,b),(-width/2,b)]]
  vs=[(x,base-.1,z) for x,z in poly]+[(x,yy,z) for (x,z),yy in zip(poly,[lo,lo,hi,hi])]
  mesh(n+' ramp',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'dark',True)
  prism(uid(n+' tread'),poly,hi-.07,hi,'ri_dark',solid=False)
  for side in [-1,1]:
   rr=r+side*(width/2+.07);p=(cx+rr*math.cos(a),lo+1,cz+rr*math.sin(a));q=(cx+rr*math.cos(b),hi+1,cz+rr*math.sin(b));limb('curved handrail',p,q,.08,'gold')
   # Continuous collision parapet, follows the curved incline.
   railing=[(cx+(rr+s)*math.cos(t),y,cz+(rr+s)*math.sin(t)) for yoff in [0,1.05] for s,t,y in [(-.07,a,lo+yoff),(.07,a,lo+yoff),(.07,b,hi+yoff),(-.07,b,hi+yoff)]]
   mesh('curved glass parapet',railing,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'glass',True)
 pts=[(cx+r*math.cos(i*math.pi/12),base+rise*i/12,cz+r*math.sin(i*math.pi/12)) for i in range(13)]
 route(n,pts);level.stairs.append(Stairs(P+n,pts[0],pts[-1]))
curved('Forum inner curved escalator',6.2);curved('Forum outer curved escalator',9.2)
floor('Forum upper arcade',-122,-282,22,12,6.275)
# Upper platform joins both curved flight ends at z=-276; openings for each lane.
for lo,hi in [(-133,-116.4),(-113.9,-113.4),(-110.9,-111)]:
 if hi>lo:B('upper balcony rail',((lo+hi)/2,6.825,-276),(hi-lo,1.1,.18),'gold')
for x in [-132.9,-111.1]:B('Forum upper side guard',(x,6.825,-282),(.18,1.1,12),'gold')
B('Forum upper back guard',(-122,6.825,-288),(22,1.1,.18),'gold')
shop('FORUM UPPER BOUTIQUE',-122,-285,16,5,y=6.275)
route('Forum entry',[(-120,.075,-242),(-120,.075,-261),(-120,.075,-266),(-128,.075,-266),(-128,.075,-279),(-156,.075,-279),(-162,.075,-279)])
route('Forum escalator access',[(-120,.075,-266),(-97,.075,-263),(-91,.075,-270),(-91,.075,-280),(-96.8,.075,-280),(-96.8,.075,-276)])
route('Forum inner access',[(-96.8,.075,-280),(-99.8,.075,-280),(-99.8,.075,-276)])
node('Forum upper landing',(-122,6.275,-278));landmark(P+'Forum Atlantis',(-147,.1,-265),tags=['landmark','statue-court'])
landmark(P+'Forum escalators',(-94,.1,-276),tags=['landmark','escalator'])

# Architectural detail pass: recessed panels, ceiling coffers, patterned carpets,
# lighting fixtures and shopfront arches give each public floor a readable scale.
def arch_trim(n,x,z,w,y=0,h=4.5,material='ivory'):
 r=w/2;spring=y+h-r
 for side in [-1,1]:D(n+' jamb',(x+side*(r+.12),(y+spring)/2,z),(.24,spring-y,.3),material)
 for i in range(20):
  a=i*math.pi/20;b=(i+1)*math.pi/20
  vs=[(x+rr*math.cos(t),spring+rr*math.sin(t),zz) for zz in [z-.12,z+.12] for rr,t in [(r,a),(r,b),(r+.23,b),(r+.23,a)]]
  mesh(n+' arch',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)
def coffer(n,x,z,w,d,y,theme='gold'):
 D(n+' ceiling inset',(x,y,z),(w,.15,d),'dark')
 for inset in [0,.22]:
  for zz in [-1,1]:D(n+' coffer molding',(x,y-.13-inset*.2,z+zz*(d/2-inset)),(w-inset*2,.15,.14),theme)
  for xx in [-1,1]:D(n+' coffer molding',(x+xx*(w/2-inset),y-.13-inset*.2,z),(.14,.15,d-inset*2),theme)
 lathe(n+' chandelier',x,z,[(.12,y-.12),(.12,y-.8),(.8,y-1),(.85,y-1.1),(.4,y-1.35)],theme)
 for i in range(10):
  a=i*math.tau/10;D('chandelier pendant',(x+.75*math.cos(a),y-1.35,z+.75*math.sin(a)),(.075,.55,.075),'light')
def wall_detail(n,x0,x1,z0,z1,theme):
 for z in [z0+.3,z1-.3]:
  for x in range(math.ceil(x0+4),int(x1-2),6):
   # Do not place any infill across a doorway: only shallow decorative moldings.
   D(n+' pilaster',(x,3.8,z),(.38,7.3,.25),theme)
   D(n+' wall panel',(x+2.7,2.5,z),(4.7,3.1,.12),'wood')
   for yy in [1,4.1,5.1]:D(n+' panel molding',(x+2.7,yy,z+.09),(4.8,.12,.17),theme)
 for x in [x0+.35,x1-.35]:
  for z in range(math.ceil(z0+4),int(z1-2),6):D(n+' side pilaster',(x,3.8,z),(.25,7.3,.38),theme)
# Panels omitted near public openings by removing doorway-overlapping decoration below.
wall_detail('Flamingo deco',90,200,-259,-215,'gold')
wall_detail('Horseshoe deco',92,128,-147,-85,'gold')
wall_detail('Planet Hollywood deco',65,198,173,274,'blue')
# Hotel walls get layered soffits; casinos have lower articulated ceilings while
# escalator/lobby volumes remain tall enough for the upper floors.
for n,x0,x1,z0,z1,y,t in [('Flamingo',95,155,-254,-219,7.7,'gold'),('Horseshoe',96,117,-141,-107,7.8,'gold'),('Planet Hollywood',101,164,193,244,8.0,'gold')]:
 for x in range(x0,x1,12):
  for z in range(z0,z1,12):coffer(n,x,z,9,9,y,t)
# Art-deco carpet lattice: fine geometry rests just above the carpet plane.
for n,x0,x1,z0,z1 in [('Flamingo',96,158,-251,-222),('Horseshoe',96,125,-143,-89),('Planet Hollywood',99,164,194,244)]:
 for x in range(x0,x1,4):
  for z in range(z0,z1,4):
   for angle in [-math.pi/4,math.pi/4]:D(n+' woven diamond',(x,.137,z),(.045,.012,2.5),'gold',yaw=angle)
# Boutique front arches and tenant variety, with an open arcade under a sky ceiling.
for x in [-162,-144,-126]:arch_trim('Forum boutique arch',x,-284.85,4,0,6)
for x in [82,101,121,141,161,184]:arch_trim('Miracle Mile arch',x,184.2,4,0,5.3,'ivory')
for x in [103,122,143,162,186]:arch_trim('Miracle Mile south arch',x,272.2,4,0,5.3,'ivory')
D('Miracle Mile east sky', (174,11.85,221),(11,.05,65),'sky')
D('Miracle Mile north sky',(130,11.85,190),(88,.05,10),'sky')
for z in range(193,258,10):
 for x in [169,180]:D('Miracle Mile arcade pilaster',(x,4.8,z),(.42,9.6,.42),'ivory')
 for yy in [8.5,9.0]:D('Miracle Mile entablature',(174.5,yy,z),(11,.25,.5),'gold')
# Lounge furniture, baggage carts and abandonment details, set off audited aisles.
for x,z,y in [(188,-220,6.075),(-130,244,4.275),(82,248,6.075),(123,-113,6.075)]:
 D('lounge sofa seat',(x,y+.5,z),(2.7,.35,1),'red');D('lounge sofa back',(x,y+1,z+.45),(2.7,.85,.2),'red');D('lounge low table',(x,y+.4,z-1.6),(2,.15,1),'marble')
for x,z in [(156,-255),(124,-89),(71,202)]:
 D('luggage trolley',(x,.3,z),(1.4,.15,.9),'gold')
 for dx in [-.6,.6]:limb('trolley upright',(x+dx,.3,z),(x+dx,1.8,z),.06,'gold')
 limb('trolley handle',(x-.6,1.8,z),(x+.6,1.8,z),.06,'gold')
 D('abandoned luggage',(x,.8,z),(1,.8,.65),'wood')
# Remove decorative panel infill where it would visually cover a new door.
remove=[]
for ob in bpy.data.objects:
 if 'wall panel' not in ob.name and 'panel molding' not in ob.name and 'deco pilaster' not in ob.name:continue
 p=ob.location
 for dr in level.doors_json():
  q=dr['position']
  if abs(p.x-q['x'])<dr['width']/2+2.7 and abs(-p.y-q['z'])<.6:remove.append(ob);break
bpy.data.batch_remove(remove)

light('Paris retail light',131,-42,6.8,intensity=90)
light('Paris boutique light',131,-18,6.8,intensity=90)
light('Cosmopolitan lounge light',-125,245,7.7,intensity=70)
B('Planet Hollywood escalator divider',(82,6.625,239),(2.5,1.1,.18),'gold')
# Convert all signage once; save authored geometry and merge runtime meshes.
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for ob in labels:
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));new=bpy.data.objects.new(ob.name+' glyphs',me);scene.collection.objects.link(new);new.matrix_world=ob.matrix_world.copy()
bpy.data.batch_remove(labels)
addition=level.mesh_level_json()
for key in ['colliders','volumes','landmarks','lights']:data[key]+=addition[key]
for key in ['links','stairs','doors']:data['extras'].setdefault(key,[]);data['extras'][key]+=addition['extras'][key]
Path('build/level/vegas.mesh-level.json').write_text(json.dumps(data,indent=2));Path('build/level/vegas.doors.json').write_text(json.dumps(old_doors+level.doors_json(),indent=2))
Path('build/interiors/addition.mesh-level.json').write_text(json.dumps(addition,indent=2))
orient_closed_solids();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
source=ast.parse(Path('tools/level/vegas.py').read_text());fn=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='fast_export');exec(compile(ast.Module(body=[fn],type_ignores=[]),'vegas.py','exec'));fast_export('build/level/vegas.glb')
print('INTERIORS COMPLETE',len(addition['colliders']),'new colliders',len(addition['volumes']),'volumes',len(level.doors),'doors',flush=True)
