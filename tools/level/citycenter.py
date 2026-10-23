"""Local CityCenter extension. References / coordinates: CITYCENTER.md.
Rebuilds from the immutable post-exteriors baseline; never uploads assets.
"""
import bpy, math, json, os, sys, random
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'tools/blender-level');sys.path.insert(0,'tools/level')
from bmlevel import *
from bmlevel.core import BoxCollider, HullCollider
from geometry_quality import orient_closed_solids
from surface_geometry import slab_union, subtract_rectangle
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/citycenter/baseline.blend'))
scene.materials.update({m.name:m for m in bpy.data.materials})
data=json.loads(Path('build/citycenter/baseline.mesh-level.json').read_text())
old_doors=json.loads(Path('build/citycenter/baseline.doors.json').read_text())
P='CityCenter / ';hotel='Streets';serial=0;labels=[];batches={};floor_slabs=[];rng=random.Random(20260928)
def uid(n):
 global serial
 serial+=1;return P+hotel+f' / {serial:05d} '+n
palette=[
 ('silver',(.60,.64,.66),.76,.30,0),('pearl',(.80,.80,.75),.35,.34,0),('steel',(.24,.30,.34),.70,.30,0),
 ('blue',(.085,.22,.30),.64,.22,0),('sky',(.24,.43,.52),.62,.22,0),('glint',(.39,.57,.62),.64,.2,0),
 ('deep',(.035,.095,.14),.58,.25,0),('black',(.025,.032,.037),.25,.6,0),('white',(.79,.78,.70),.03,.6,0),
 ('stone',(.46,.43,.36),.03,.72,0),('paving',(.32,.30,.26),.02,.81,0),('asphalt',(.065,.069,.073),0,.92,0),
 ('paint',(.63,.59,.43),.02,.8,0),('gold',(.52,.38,.13),.65,.30,0),('yellow',(.60,.51,.20),.45,.29,0),
 ('olive',(.32,.33,.16),.50,.26,0),('bronze',(.36,.27,.17),.65,.30,0),('wood',(.35,.16,.061),.04,.69,0),
 ('timber',(.62,.35,.13),.08,.55,0),('leaf',(.082,.13,.054),0,.87,0),('trunk',(.21,.15,.095),0,.85,0),
 ('water',(.035,.18,.20),.48,.18,0),('carpet',(.085,.12,.13),0,.91,0),('felt',(.022,.12,.08),0,.98,0),
 ('light',(1,.69,.31),.04,.38,1.4),('screen',(.055,.19,.22),.25,.32,.30),('glass',(.26,.44,.47),.22,.21,0),
 ('red',(.24,.035,.045),.05,.77,0),('marble',(.66,.61,.49),.15,.34,0)]
for n,c,metal,rough,glow in palette:mat('cc_'+n,c,metal=metal,roughness=rough,glow=glow,alpha=.24 if n=='glass' else 1)
for n in ['glass','leaf','wood','timber']:bpy.data.materials['cc_'+n].use_backface_culling=False
BOXF=[(1,2,3,0),(7,6,5,4),(4,5,1,0),(5,6,2,1),(6,7,3,2),(7,4,0,3)]
def M(n,vs,fs,m='silver',solid=False,role='auto'):
 if solid:
  signed=sum(Vector(vs[f[0]]).dot(Vector(vs[f[i]]).cross(Vector(vs[f[i+1]]))) for f in fs for i in range(1,len(f)-1))
  if signed<0:fs=[tuple(reversed(f)) for f in fs]
 # Author many small details in material batches; export still classifies each face.
 key=(hotel,m,role);g=batches.setdefault(key,{'v':[],'f':[]});base=len(g['v']);g['v']+=vs;g['f'] += [tuple(base+i for i in f) for f in fs]
 if solid:level.colliders.append(HullCollider(uid(n),[v for p in vs for v in p]))
def D(n,p,s,m='silver',yaw=0,role='auto',solid=False):
 x,y,z=p;w,h,d=[v/2 for v in s];c=math.cos(yaw);si=math.sin(yaw)
 vs=[(x+c*a+si*b,y+yy,z-si*a+c*b) for yy in [-h,h] for a,b in [(-w,-d),(w,-d),(w,d),(-w,d)]]
 M(n,vs,BOXF,m,role=role)
 if solid:level.colliders.append(BoxCollider(uid(n),p,s,yaw))
def B(n,p,s,m='stone',**kw):D(n,p,s,m,solid=True,**kw)
def floor(n,x,z,w,d,y=.075,m='marble',role='auto',depth=.40):
 # Keep overlapping collision coverage, but emit only the union's exposed faces.
 level.colliders.append(BoxCollider(uid(n),(x,y-depth/2,z),(w,depth,d),0))
 floor_slabs.append(dict(owner=hotel,x0=x-w/2,x1=x+w/2,z0=z-d/2,z1=z+d/2,top=y,depth=depth,material=m,role=role))
def poly(n,outline,y0,y1,m='stone',solid=True,role='auto'):
 k=len(outline);vs=[(x,y,z) for y in [y0,y1] for x,z in outline];fs=[tuple(range(k)),tuple(reversed(range(k,2*k)))]+[(i+k,(i+1)%k+k,(i+1)%k,i) for i in range(k)]
 M(n,vs,fs,m,solid,role)
def beam(n,a,b,r,m='silver',role='auto',sides=6):
 a=Vector(a);b=Vector(b);v=(b-a).normalized();u=v.cross(Vector((0,1,0)))
 if u.length<.001:u=v.cross(Vector((1,0,0)))
 u.normalize();w=v.cross(u).normalized();vs=[tuple(p+r*(math.cos(j*math.tau/sides)*u+math.sin(j*math.tau/sides)*w)) for p in [a,b] for j in range(sides)]
 M(n,vs,[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)],m,role=role)
def face(n,a,b,y0,y1,m='blue',out=0,role='shell'):
 dx=b[0]-a[0];dz=b[1]-a[1];L=math.hypot(dx,dz);ox=dz/L*out;oz=-dx/L*out
 D(n,((a[0]+b[0])/2+ox,(y0+y1)/2,(a[1]+b[1])/2+oz),(L+.015,y1-y0,.10),m,yaw=math.atan2(-dz,dx),role=role)
def sign(s,p,size=1,yaw=math.pi/2,m='light',role='shell'):
 cr=bpy.data.curves.new(uid(s),'FONT');cr.body=s;cr.align_x='CENTER';cr.size=size;cr.extrude=.014;cr.resolution_u=4
 ob=bpy.data.objects.new(cr.name,cr);scene.collection.objects.link(ob);ob.location=(p[0],-p[2],p[1]);ob.rotation_euler=(math.pi/2,0,yaw);cr.materials.append(bpy.data.materials['cc_'+m]);ob['visibilityRole']=role;labels.append(ob)
def node(n,p):volume(P+n,(p[0],p[1]+1.45,p[2]),(.8,2.8,.8),tags=['route'],roofed=False)
def route(n,points):
 for i,p in enumerate(points):node(n+str(i),p)
 for i in range(len(points)-1):link(P+n+str(i),P+n+str(i+1))
def light(n,x,z,y=6,intensity=110,distance=24):lamp(uid(n),(x,y,z),'#ffe0b1',intensity,distance)
def rail(n,a,b,y=6.2):
 face(n,a,b,y,y+1.1,'glass',role='interior');beam(n+' handrail',(a[0],y+1.13,a[1]),(b[0],y+1.13,b[1]),.05,'steel',role='interior')
 L=math.dist(a,b)
 for i in range(math.ceil(L/3)+1):
  t=i/max(1,math.ceil(L/3));x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t;beam(n+' post',(x,y,z),(x,y+1.15,z),.04,'steel',role='interior')
 # Continuous thin collider prevents falling over the decorative glass.
 dx=b[0]-a[0];dz=b[1]-a[1]
 level.colliders.append(BoxCollider(uid(n+' guard collision'),((a[0]+b[0])/2,y+.55,(a[1]+b[1])/2),(L,1.1,.12),math.atan2(-dz,dx)))
def doorway(n,axis,c,lo,hi,at,h=12,w=5,y=.075,m='stone'):
 for a,b in [(lo,at-w/2),(at+w/2,hi)]:
  if b>a:B(n+' return',(c,y+h/2,(a+b)/2) if axis=='x' else ((a+b)/2,y+h/2,c),(.55,h,b-a+.04) if axis=='x' else (b-a+.04,h,.55),m,role='shell')
 B(n+' lintel',(c,y+(h+4.2)/2,at) if axis=='x' else (at,y+(h+4.2)/2,c),(.55,h-4.2,w+.05) if axis=='x' else (w+.05,h-4.2,.55),m,role='shell')
 id=P+n;pos=(c,y,at) if axis=='x' else (at,y,c)
 for existing in level.doors:
  if math.dist(existing.position,(pos[0],pos[1]+2.1,pos[2]))<.01:return existing.id
 door(id,pos,width=w,height=4.2,yaw=math.pi/2 if axis=='x' else 0,auto_open_radius=6)
 return id
def shell(n,x0,x1,z0,z1,h=12,entries={},windowed=False,roof=True,m='stone',shared_sides=()):
 floor(n+' floor',(x0+x1)/2,(z0+z1)/2,x1-x0+.5,z1-z0+.5)
 # A real ceiling thickness encloses the tower base caps (Y=14 / Y=12).
 # Never put the underside on the same plane as a structural tower bottom.
 if roof:floor(n+' roof',(x0+x1)/2,(z0+z1)/2,x1-x0+.7,z1-z0+.7,h+.4,m='pearl',role='shell',depth=.95)
 for side,axis,c,lo,hi in [('east','x',x1,z0,z1),('west','x',x0,z0,z1),('north','z',z0,x0,x1),('south','z',z1,x0,x1)]:
  # The adjoining room owns the shared wall and its existing doorway.
  if side in shared_sides:continue
  if side in entries:
   ats=entries[side] if isinstance(entries[side],list) else [entries[side]]
   ats=sorted(ats);cuts=[lo]+[(a+b)/2 for a,b in zip(ats,ats[1:])]+[hi]
   for i,at in enumerate(ats):doorway(n+' '+side+(' '+str(i) if len(ats)>1 else ''),axis,c,cuts[i],cuts[i+1],at,h=h,m=m)
  else:B(n+' '+side,(c,h/2+.075,(lo+hi)/2) if axis=='x' else ((lo+hi)/2,h/2+.075,c),(.5,h,hi-lo+.2) if axis=='x' else (hi-lo+.2,h,.5),m,role='shell')
 volume(P+n+' envelope',((x0+x1)/2,h/2+.075,(z0+z1)/2),(x1-x0,h,z1-z0),tags=['indoors','public']+(['windowed'] if windowed else []))
def stairs_at(n,x,z,y=.075,rise=6,run=15,width=4,yaw=0):
 # Use a local origin, so both visual treads and the ramp share exactly one transform.
 with context(P+n,origin=(x,y,z),yaw=yaw):stairs(P+n,(0,0,0),rise,run,'cc_steel',width=width,rail='cc_silver')
 c=math.cos(yaw);s=math.sin(yaw)
 for side in [-1,1]:
  a=(x+c*side*(width/2+.17),y+1,z-s*side*(width/2+.17));b=(a[0]+s*run,y+rise+1,a[2]+c*run)
  beam(n+' moving handrail',a,b,.10,'black',role='interior')
 route(n+' walk',[(x-s*.8,y,z-c*.8),(x+s*(run+.8),y+rise,z+c*(run+.8))])
def palm(x,z,h=8,y=0):
 beam('palm trunk',(x,y,z),(x+.35,y+h,z+.2),.18,'trunk')
 for j in range(9):
  a=j*math.tau/9;vs=[]
  for k in range(8):
   t=k/7;r=3.4*t;yy=y+h+.65*math.sin(math.pi*t)-1.7*t*t;w=.32*math.sin(math.pi*t)
   for side in [-1,1]:vs.append((x+.35+r*math.cos(a)+side*w*math.sin(a),yy,z+.2+r*math.sin(a)-side*w*math.cos(a)))
  M('palm frond',vs,[(2*k,2*k+1,2*k+3,2*k+2) for k in range(7)],'leaf')
 D('palm planter',(x,.24+y,z),(2.4,.45,2.4),'stone')
def bench(x,z,y=.075):
 D('bench seat',(x,y+.48,z),(2.2,.16,.65),'timber',role='interior');D('bench back',(x,y+.86,z+.25),(2.2,.7,.13),'timber',role='interior')
 for dx in [-.8,.8]:D('bench foot',(x+dx,y+.2,z),(.15,.4,.5),'steel',role='interior')
def reception(n,x,z,w=12):
 B(n+' desk',(x,.68,z),(w,1.2,1.1),'wood',role='interior');D('desk cap',(x,1.32,z),(w+.2,.12,1.3),'marble',role='interior')
 for dx in [-w*.3,0,w*.3]:D('monitor',(x+dx,1.6,z),(.6,.45,.12),'black',role='interior')
 sign(n+' / RECEPTION',(x,3.2,z+.7),.55,yaw=math.pi,role='interior')

# Replace only perimeter/foundation, with a continuous expanded floor at the same datum.
removed=[o for o in bpy.data.objects if 'district edge' in o.name or 'continuous foundation' in o.name]
bpy.data.batch_remove(removed);data['colliders']=[c for c in data['colliders'] if 'district edge' not in c['name'] and c['name']!='continuous foundation']
box('continuous foundation',(-150,-.25,180),(740,.5,960),'concrete')
for x in [-518,218]:B('district edge',(x,2,180),(3,4,960),'stone')
for z in [-298,658]:B('district edge',(-150,2,z),(740,4,3),'stone')
D('boulevard extension',(0,.045,472),(38,.06,365),'asphalt')
for x in [-21,21]:D('boulevard curb',(x,.14,474),(1,.28,365),'stone')
for x in [-12,-5,5,12]:
 for z in range(296,648,12):D('lane stripe',(x,.082,z),(.13,.02,5),'paint')
def road(n,pts,width=18):
 for a,b in zip(pts,pts[1:]):
  dx=b[0]-a[0];dz=b[1]-a[1];L=math.hypot(dx,dz);yaw=math.atan2(-dz,dx)
  D(n+' paving',((a[0]+b[0])/2,.046,(a[1]+b[1])/2),(L+2,.06,width),'asphalt',yaw=yaw)
  for side in [-1,1]:D(n+' curb',((a[0]+b[0])/2+dz/L*side*(width/2+.5),.13,(a[1]+b[1])/2-dx/L*side*(width/2+.5)),(L+1,.25,.55),'stone',yaw=yaw)
  for i in range(max(1,int(L/9))):
   t=(i+.5)/max(1,int(L/9));D(n+' center dash',(a[0]+dx*t,.088,a[1]+dz*t),(3,.02,.11),'paint',yaw=yaw)
road('Harmon Avenue',[(-19,295),(-193,295),(-237,307),(-281,313),(-356,334),(-510,360)],20)
road('Aria Place',[(-19,516),(-70,508),(-138,492),(-213,472),(-241,449),(-245,426),(-224,409)],18)
# Curbside paving strips, a broad walk up Aria Place, crossings and palms.
for z in range(311,639,5):D('Strip sidewalk',(-29,.06,z),(14,.10,4.96),'paving')
road('Waldorf entrance',[(-65,518),(-114,538),(-139,558),(-139,606),(-81,616),(-23,616)],8)
for a,b in [((-28,500),(-214,457)),((-31,483),(-197,454))]:
 dx=b[0]-a[0];dz=b[1]-a[1];D('Aria Place pedestrian promenade',((a[0]+b[0])/2,.09,(a[1]+b[1])/2),(math.hypot(dx,dz),.16,5),'stone',yaw=math.atan2(-dz,dx))
for z in [303,514,617]:
 for x in range(-17,18,4):D('pedestrian crossing',(x,.095,z),(2,.02,5),'paint')
for z in range(320,640,16):palm(-25,z,8+rng.random()*2)
for i in range(11):
 t=i/10;palm(-46-170*t,502-39*t,7.5)
for x,z in [(-32,315),(-33,490),(-191,475)]:
 B('wayfinding pedestal',(x,1.3,z),(.7,2.6,.5),'black');sign('CITYCENTER',(x+.4,1.8,z),.28)
sign('ARIA',(-34,22,312),3);B('Aria boulevard monolith',(-36,11,312),(3,22,3),'black')
print('CityCenter streets built',flush=True)

# Glass curtain-wall towers: segmented curved solids, not rectangular blocks.
def curtain(n,outline,y0,y1,style='aria',lean=(0,0)):
 for side,(a,b) in enumerate(zip(outline,outline[1:]+outline[:1])):
  L=math.dist(a,b);cols=max(1,round(L/2.1));rows=max(1,round((y1-y0)/3.5));dx=b[0]-a[0];dz=b[1]-a[1];ox=dz/L*.08;oz=-dx/L*.08
  for j in range(rows):
   yy=y0+(y1-y0)*j/rows;yy1=y0+(y1-y0)*(j+1)/rows
   for i in range(cols):
    u=i/cols;v=(i+1)/cols
    # Veer's ceramic frit is deliberately irregular; other towers use coherent vertical reflections.
    if style=='veer':m=rng.choices(['yellow','olive','sky','deep','gold'],[32,16,30,15,7])[0]
    elif style=='waldorf':m=['deep','blue','sky','blue','deep','bronze'][i%6]
    else:m=['blue','sky','blue','glint','sky','blue'][int((side*.6+i*.25+j*.035))%6]
    def p(t,y):return (a[0]+dx*t+ox+lean[0]*(y-y0),y,a[1]+dz*t+oz+lean[1]*(y-y0))
    M(n+' curtain panel',[p(u+.014/cols,yy+.055),p(v-.014/cols,yy+.055),p(v-.014/cols,yy1-.055),p(u+.014/cols,yy1-.055)],[(0,3,2,1)],m,role='shell')
   aa=(a[0]+lean[0]*(yy-y0),a[1]+lean[1]*(yy-y0));bb=(b[0]+lean[0]*(yy-y0),b[1]+lean[1]*(yy-y0))
   face(n+' horizontal spandrel',aa,bb,yy,yy+(.33 if style=='vdara' else .13),'pearl' if style in ['aria','vdara'] else 'steel',out=.13)
  for i in range(cols+1):
   u=i/cols;x=a[0]+dx*u+ox*2;z=a[1]+dz*u+oz*2
   beam(n+' facade mullion',(x,y0,z),(x+lean[0]*(y1-y0),y1,z+lean[1]*(y1-y0)),.055 if style!='waldorf' else .105,'bronze' if style=='waldorf' else 'steel',role='shell',sides=4)
def curved(n,x,z,length,thickness,bow,h,style,segments=26,angle=0):
 c=math.cos(angle);s=math.sin(angle)
 def point(u,offset):
  xx=bow*(1-u*u)+offset;zz=u*length/2
  return (x+c*xx+s*zz,z-s*xx+c*zz)
 front=[point(-1+2*i/segments,thickness/2) for i in range(segments+1)];back=[point(-1+2*i/segments,-thickness/2) for i in range(segments+1)]
 for i in range(segments):poly(n+' silhouette '+str(i),[back[i],front[i],front[i+1],back[i+1]],14,h,'deep')
 outline=front+list(reversed(back));curtain(n,outline,14.05,h,style)
 for yy in [h+.3,h+1.3,h+2.3,h+3.3,h+4.3]:
  for a,b in zip(front,front[1:]):face(n+' crown louver',a,b,yy,yy+.20,'silver',out=.22)
 for j in range(0,len(front),3):
  a=front[j];D(n+' roof fin',(a[0],h+2.3,a[1]),(.20,5.2,.20),'silver',role='shell')
 # top cap segmented along the same curve; no bridging across concave plan.
 for i in range(segments):poly(n+' top',[back[i],front[i],front[i+1],back[i+1]],h,h+.28,'steel',False,'shell')

hotel='Vdara'
shell('Vdara lobby',-356,-262,210,273,h=14.25,entries={'south':-299,'east':242},windowed=True,m='deep')
for xx,zz,ll,hh in [(-319,221,66,164),(-329,244,66,169),(-340,264,66,158)]:curved('Vdara offset crescent',xx,zz,ll,17,10,hh,'vdara',16,angle=.12)
for x,z in [(-323,190),(-313,193),(-344,296),(-333,293)]:
 B('Vdara load-bearing pilotis',(x,7,z),(1.5,14,1.5),'silver',role='shell')
 D('Vdara transfer capital',(x,13.2,z),(5.8,1.6,4),'steel',role='shell')
for x in [-345,-331,-317,-280]:
 D('Vdara lobby glazing',(x,6.8,273.35),(10.5,12.2,.12),'blue',role='shell')
 for dx in [-5,0,5]:D('Vdara lobby mullion',(x+dx,6.8,273.55),(.12,12.4,.3),'silver',role='shell')
# Curved entry canopy / pool deck facing Harmon Circle.
for i in range(18):
 a=-.95+i*1.9/18;b=-.95+(i+1)*1.9/18
 pts=[(-307+r*math.sin(t),270+r*math.cos(t)) for r,t in [(13,a),(29,a),(29,b),(13,b)]]
 poly('Vdara curved pool deck',pts,6.9,7.4,'stone',role='shell')
 if i%3==0:beam('Vdara canopy support',(pts[1][0],.075,pts[1][1]),(pts[1][0],6.9,pts[1][1]),.18,'silver',role='shell')
sign('VDARA',(-300,10.8,273.4),2,yaw=0)
reception('VDARA',-327,223);bench(-281,254);bench(-291,254)
for z in [222,244,262]:light('Vdara lobby',-298,z,9)
for x in [-345,-276]:palm(x,282,7)
route('Vdara arrival',[(-299,.075,291),(-299,.075,268),(-299,.075,242),(-257,.075,242)])

hotel='Aria'
shell('Aria casino',-453,-282,347,489,h=14,entries={'east':[396,448],'north':-305,'south':-318})
# Two interlocking arcs, taller southern wing and lower northern wing.
curved('Aria north crescent',-316,406,130,24,24,169,'aria',30,angle=-.12)
curved('Aria south crescent',-374,423,150,24,26,183,'aria',32,angle=.21)
for x,z in [(-330,343),(-308,344),(-347,494),(-368,496)]:
 B('Aria tower bearing',(x,7,z),(1.6,14,1.6),'silver',role='shell')
 D('Aria bearing canopy',(x,13.6,z),(8,1.2,9),'silver',role='shell')
sign('ARIA',(-282,166,388),3.5);sign('ARIA',(-335,180,410),4)
# Main lobby between casino and porte cochere, opens through the casino east door.
shell('Aria lobby',-282,-244,424,476,h=12,entries={'west':448,'east':448},windowed=True,m='deep',shared_sides=('west',))
reception('ARIA',-265,433,w=19)
for z in [440,458]:
 for x in [-274,-253]:bench(x,z);light('Aria lobby',x,z,9,140)
for i in range(20):
 t0=-1+i*2/20;t1=-1+(i+1)*2/20
 a=(-242+17*math.cos(t0),448+25*math.sin(t0));b=(-242+17*math.cos(t1),448+25*math.sin(t1))
 poly('Aria curved porte cochere',[(-245,a[1]),a,b,(-245,b[1])],7.8,8.25,'silver',role='shell')
 if i%4==0:beam('Aria canopy pylon',(a[0],.075,a[1]),(a[0],7.8,a[1]),.24,'silver',role='shell')
sign('ARIA',(-224,8.7,448),1.7)
# Casino islands leave a wide east-west spine and a north-south promenade.
for x in [-420,-388,-352,-315]:
 for z in [375,402,468]:
  if x==-315 and z==375:continue
  for k in range(5):
   xx=x+k*1.6;B('Aria slot cabinet',(xx,1.1,z),(1.2,2,.75),'black',role='interior');D('slot blue screen',(xx,1.5,z-.4),(.94,1,.05),'screen',role='interior');D('slot gold surround',(xx,2.1,z-.39),(1.1,.12,.07),'gold',role='interior')
   D('slot stool',(xx,.65,z-1.4),(.65,.3,.65),'carpet',role='interior')
for x in [-427,-399,-365]:
 for z in [431,453]:
  B('gaming pedestal',(x,.55,z),(1.4,1.1,1),'wood',role='interior');D('gaming table',(x,1.18,z),(4,.18,2.4),'felt',role='interior')
for x in range(-439,-285,22):
 for z in range(360,487,23):light('casino warm pool',x,z,10,135);D('Aria pendant',(x,10.6,z),(3,.18,1),'light',role='interior')
for x in [-446,-407,-365,-325]:B('casino core column',(x,7,416),(1.2,14,1.2),'bronze',role='interior')
for z in [354,482]:D('Aria promenade carpet',(-366,.092,z),(151,.025,10),'carpet',role='interior')
route('Aria casino spine',[(-239,.075,448),(-267,.075,448),(-295,.075,448),(-309,.075,440),(-443,.075,440)])
route('Aria north arrival',[(-305,.075,335),(-305,.075,357),(-295,.075,357),(-295,.075,448)])
print('Aria and Vdara built',flush=True)

hotel='Crystals'
shell('Crystals arcade',-210,-32,323,470,h=18,entries={'east':381,'west':396,'north':-92,'south':-93},windowed=True,roof=False,m='white')
level.volumes[-1].position=(-121,17.975,396.5)
level.volumes[-1].size=(178,35.8,147)

# Angular stainless-steel roof folded around a sequence of tall glazed lanterns.
xs=[-210,-151,-91,-32];zs=[323,354,391,429,470]
def rooftri(n,tri,m):
 # The soffit IS the slab underside, not a nearly coplanar overlay.
 vs=tri+[(x,y-.28,z) for x,y,z in tri]
 fs=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
 signed=sum(Vector(vs[f[0]]).dot(Vector(vs[f[i]]).cross(Vector(vs[f[i+1]]))) for f in fs for i in range(1,len(f)-1))
 if signed<0:fs=[tuple(reversed(f)) for f in fs]
 M(n,vs,[fs[0]]+fs[2:],m,role='shell')
 M(n+' soffit',vs,[fs[1]],'white' if m!='glass' else m,role='shell')
 level.colliders.append(HullCollider(uid(n),[v for p in vs for v in p]))

for i in range(3):
 for j in range(4):
  x0,x1=xs[i],xs[i+1];z0,z1=zs[j],zs[j+1];ridge=(x0+(x1-x0)*(.36 if j%2 else .68),27+((i+j)%3)*4,z0+(z1-z0)*(.27 if i%2 else .71))
  corners=[(x0,18.0,z0),(x1,18.0,z0),(x1,18.0,z1),(x0,18.0,z1)]
  for k in range(4):
   tri=[corners[k],corners[(k+1)%4],ridge];m='glass' if k==(i+j)%4 else ['silver','pearl','steel'][(k+i)%3]
   rooftri('Crystals folded roof',tri,m)
   # Metal panel seams and skylight mullions follow the actual slope of each facet.
   a,b,c=[Vector(p) for p in tri]
   for q in range(1,12):
    t=q/12;p=a.lerp(c,t);r=b.lerp(c,t);p.y+=.035;r.y+=.035;beam('fold seam',p,r,.025 if m!='glass' else .055,'steel' if m!='glass' else 'silver',role='shell',sides=4)
  for a in corners:beam('folded structural rib',(a[0],a[1]-.4,a[2]),(ridge[0],ridge[1]-.4,ridge[2]),.14,'white',role='interior')
# Facade shards: off-axis, leaning quadrilaterals and triangular glazing, with real depth.
for j,(z0,z1,h,brand) in enumerate([(326,353,27,'GUCCI'),(354,374,22,'TIFFANY & CO.'),(389,423,30,'LOUIS VUITTON'),(430,464,25,'PRADA')]):
 vs=[(-31,.12,z0),(-31,.12,z1),(-22,h,z1-5),(-26,h-8,z0+6),(-44,.12,z0),(-44,.12,z1),(-42,h,z1-5),(-43,h-8,z0+6)]
 # Three opaque edge ribbons leave a broad, dark, trapezoid display face.
 M('folded shop front',vs,[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0),(4,7,6,5)],'silver' if j!=3 else 'steel',role='shell')
 # A second inset plane makes the window shape readable from boulevard height.
 quad=[(-30.7,1,z0+3),(-30.7,1,z1-3),(-24.5,h*.68,z1-5),(-28.3,h*.48,z0+6)]
 M('angular storefront glazing',quad,[(0,3,2,1)],'deep',role='shell')
 sign(brand,(-21.8,h*.38,(z0+z1)/2),.85 if j!=2 else 1.0)
 for k in range(1,12):
  t=k/12;beam('cladding vertical joint',(-30.92,.2,z0+(z1-z0)*t),(-24,h-7+5*t,z0+6+(z1-z0-11)*t),.022,'steel',role='shell',sides=4)
sign('THE SHOPS AT CRYSTALS',(-31.45,6.5,381),.65)

# Continuous branching arcade and upper balconies. Public circulation is based on
# Simon's L1/L2 map; individual tenancies are deliberately simplified.
for x,z,w,d in [(-188,396,42,145),(-53,396,41,145),(-120,334,93,22.2),(-120,459,93,22),(-161,396,16,12),(-165.5,383,7.5,9.5)]:floor('Crystals upper gallery',x,z,w,d,6.15,role='interior')
# Balustrades on the atrium void; stair landing gaps stay open.
for a,b in [((-167,345),(-167,383)),((-167,409),(-167,448)),((-73.5,345),(-73.5,448)),((-167,345),(-123,345)),((-99,345),(-73.5,345)),((-167,448),(-112,448)),((-91,448),(-73.5,448))]:rail('Crystals atrium guard',a,b,6.15)
stairs_at('Crystals south escalator',-101,427,rise=6.075,run=22,width=3.2)
stairs_at('Crystals north escalator',-111,367,rise=6.075,run=22,width=3.2,yaw=math.pi)
stairs_at('Crystals grand stair',-142,383,rise=6.075,run=22,width=7,yaw=-math.pi/2)
# Store shells open to the central arcade on both levels.
def shop(n,x,z,w,d,y=0,facing=1):
 for zz in [z-d/2,z+d/2]:B(n+' party wall',(x,y+2.4,zz),(w,4.8,.22),'white',role='interior')
 back=x-facing*w/2;front=x+facing*w/2
 B(n+' back',(back,y+2.4,z),(.22,4.8,d),'stone',role='interior')
 for side in [-1,1]:
  zz=z+side*(d/4+1);D(n+' showcase',(front,y+2.2,zz),(.08,3.4,max(1,d/2-2.5)),'deep',role='interior')
  B(n+' showcase base',(front,y+.28,zz),(.3,.56,max(1,d/2-2.5)),'bronze',role='interior')
 D(n+' fascia',(front,y+4.35,z),(.3,.7,d),'black',role='interior');sign(n,(front+facing*.2,y+4.1,z),.43,yaw=facing*math.pi/2,role='interior')
 for zz in [z-d*.30,z+d*.30]:
  D(n+' plinth',(x,y+.5,zz),(1.6,1,1.5),'stone',role='interior');D('merchandise',(x,y+1.2,zz),(.4,.45,.4),'gold',role='interior')
 light(n,x,z,y+4.2,60,14)
for j,z in enumerate([339,362,411,436,458]):
 for side,x in [(1,-190),(-1,-52)]:shop(['BOTTEGA VENETA','BURBERRY','TOM FORD','CHANEL','GIORGIO ARMANI'][j],x,z,28,17,facing=side)
for j,z in enumerate([340,369,417,445,459]):
 for side,x in [(1,-190),(-1,-52)]:shop(['CARTIER','FENDI','VALENTINO','SAINT LAURENT','RIMOWA'][j],x,z,28,13,y=6.15,facing=side)
# Rockwell-inspired timber Treehouse: swelling ribbed pod in the south atrium.
cx,cz=-127,414;profiles=[(1.3,.15),(1.6,3),(4.2,5),(7.1,8),(8.3,11.5),(6.8,14.5),(3.2,16)]
for j in range(64):
 a=j*math.tau/64;b=(j+.78)*math.tau/64;vs=[(cx+r*math.cos(t),y,cz+r*.78*math.sin(t)) for r,y in profiles for t in [a,b]]
 M('Treehouse timber lamella',vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(profiles)-1)],'timber' if j%3 else 'wood',role='interior')
 # Continuous ribs read as individual timber strips rather than a solid cone.
 for (r,y),(rr,yy) in zip(profiles,profiles[1:]):beam('Treehouse rib',(cx+r*math.cos(a),y,cz+r*.78*math.sin(a)),(cx+rr*math.cos(a),yy,cz+rr*.78*math.sin(a)),.075,'timber',role='interior')
B('Treehouse central support',(cx,2,cz),(2.7,4,2.7),'wood',role='interior')
# Water-and-ice sculpture garden, seasonal planter beds and sculptural seating.
for x,z,r in [(-120,378,4.5),(-132,352,3.0)]:
 outline=[(x+r*math.cos(i*math.tau/32),z+r*.65*math.sin(i*math.tau/32)) for i in range(32)]
 poly('sculpture basin',outline,.10,.40,'white',False,'interior');poly('still water',[(x+(xx-x)*.94,z+(zz-z)*.94) for xx,zz in outline],.41,.43,'water',False,'interior')
 for k in range(7):
  xx=x+rng.uniform(-r*.65,r*.65);zz=z+rng.uniform(-r*.38,r*.38);beam('ice crystal',(xx,.45,zz),(xx+.15,1.6+rng.random()*2,zz),.25,'glass',role='interior')
for x,z in [(-147,431),(-143,371),(-98,355),(-98,400)]:bench(x,z);D('planting island',(x-4,.5,z),(4,.8,2.5),'white',role='interior');D('planting foliage',(x-4,1,z),(3.6,.45,2.1),'leaf',role='interior')
for x in [-159,-89]:
 for z in [332,354,384,418,457]:
  beam('Crystals leaning column',(x,.075,z),(x+(-3 if x==-159 else 3),18,z+3),.30,'white',role='interior');light('Crystals atrium',x,z,12,150,30)
sign('ARIA  /  GRAND STAIR',(-154,5,396),.6,yaw=math.pi/2,role='interior')
sign('COSMOPOLITAN  /  HARMON AVE',(-92,5,325),.5,yaw=math.pi,role='interior')
route('Crystals east entrance',[(-25,.075,381),(-40,.075,381),(-91,.075,381),(-100,.075,398)])
route('Crystals public spine',[(-93,.075,478),(-93,.075,448),(-90,.075,397),(-92,.075,371),(-92,.075,318)])
route('Crystals shop arcade',[(-93,.075,397),(-136,.075,397),(-136,.075,373),(-163,.075,373),(-163,.075,345)])
route('Crystals north escalator approach',[(-92,.075,371),(-111,.075,371),(-111,.075,368)])
route('Crystals south escalator approach',[(-93,.075,427),(-101,.075,427)])
landmark(P+'Crystals Treehouse',(-127,.075,414),tags=['landmark','mall'])
landmark(P+'Crystals supply reserve',(-189,.075,436),tags=['supply-reserve','shop'])

# Aria connection at street level plus a glazed upper bridge from the grand stair.
hotel='Crystals'
shell('Crystals Aria connector',-282,-210,390,402,h=10,entries={'east':396,'west':396},windowed=True,m='deep',shared_sides=('east','west'))
for x in range(-274,-213,9):light('Crystals connector',x,396,7,65)
route('Crystals Aria link',[(-202,.075,396),(-247,.075,396),(-288,.075,396)])
print('Crystals shopping arcade built',flush=True)

hotel='Veer'
for n,x,z,sgn in [('East',-125,455,1),('West',-189,421,-1)]:
 outline=[(x-18,z-14),(x+18,z-14),(x+18,z+14),(x-18,z+14)];y0=18;h=144;lean=(0,sgn*math.tan(math.radians(5)))
 vs=[(xx+lean[0]*(y-y0),y,zz+lean[1]*(y-y0)) for y in [y0,h] for xx,zz in outline];M('Veer '+n+' leaning silhouette',vs,BOXF,'deep',True,'shell');curtain('Veer '+n,outline,y0,h,'veer',lean)
 # Crown screens and rooftop recreation terrace follow the translated top.
 zz=z+lean[1]*(h-y0);D('Veer rooftop terrace',(x,h+.15,zz),(36,.3,28),'stone',role='shell');D('Veer infinity pool',(x+6,h+.36,zz),(9,.14,16),'water',role='shell')
 for xx in [x-18,x+18]:
  for k in range(12):D('Veer rooftop louver',(xx,h+2,zz-13+k*2.3),(.08,4,.16),'silver',role='shell')
 for zz2 in [zz-14,zz+14]:D('Veer crown screen',(x,h+2,zz2),(36,4,.10),'steel',role='shell')
 # Exposed diagonal lobby columns tie the residential tower into the mall podium.
 for xx in [x-16,x+16]:beam('Veer inclined pilotis',(xx,.075,z+sgn*2),(xx,18,z),.45,'silver',role='shell')
 sign('VEER',(x,16.5,z+14.3),1.2,yaw=0)

hotel='Waldorf'
shell('Waldorf arrival lobby',-125,-40,535,621,h=12,entries={'north':-91,'west':576,'east':576},windowed=True,m='deep')
# Angular plan, three folded blades; the continuous vertical fin rhythm is distinct
# from Aria's white horizontal bands and Veer's yellow checker frit.
outline=[(-86,536),(-48,547),(-42,576),(-55,611),(-91,620),(-107,602),(-92,572),(-111,549)]
# Convex pieces for concave plan shadow/collision; facade uses the full perimeter.
center=(-77,577)
for a,b in zip(outline,outline[1:]+outline[:1]):poly('Waldorf folded mass',[center,a,b],12,164,'deep')
curtain('Waldorf shadow box facade',outline,12.05,164,'waldorf')
for a,b in zip(outline,outline[1:]+outline[:1]):
 face('Waldorf sky lobby belt',a,b,77,82,'deep',out=.15)
 for yy in [76.6,82.2,164]:face('Waldorf narrow belt',a,b,yy,yy+.2,'bronze',out=.2)
sign('WALDORF ASTORIA',(-39.6,9.4,576),.9)
reception('WALDORF ASTORIA',-92,608,18)
for x in [-113,-66]:
 for z in [549,587,607]:bench(x,z);light('Waldorf lobby',x,z,9,100)
for z in range(550,610,9):
 for x in [-128,-135]:beam('bamboo courtyard',(x,.075,z),(x+.12,5+rng.random()*2,z),.055,'leaf',sides=5)
floor('Waldorf secluded canopy',-132,577,16,42,6.8,role='shell',m='bronze')
for z in [559,594]:beam('Waldorf canopy pier',(-139,.075,z),(-139,6.8,z),.16,'bronze',role='shell')
route('Waldorf entry',[(-91,.075,528),(-91,.075,552),(-77,.075,568),(-35,.075,576)])

# Human-scale street frontage. These details belong to the visible outer shell,
# including when the enclosed interiors are disabled by the visibility system.
hotel='Crystals'
for i,(x,w,label) in enumerate([(-193,29,'HERMES'),(-158,30,'GIORGIO ARMANI'),(-122,25,'TOM FORD'),(-65,30,'TIFFANY & CO.')]):
 D('Aria Place recessed showroom',(x,6.7,470.32),(w,12.6,.14),'deep',role='shell')
 for xx in [x-w/2,x+w/2]:beam('showroom angled frame',(xx,.2,470.6),(xx+3,15,473),.19,'bronze',role='shell')
 for j in range(1,int(w/3)):
  xx=x-w/2+j*3;D('showroom glazing mullion',(xx,6.6,470.48),(.085,12.6,.12),'silver',role='shell')
 for yy in [1.3,4.6,10]:D('showroom horizontal frame',(x,yy,470.48),(w,.10,.12),'steel',role='shell')
 # Each storefront has its own folded and cantilevered metallic brow.
 tri=[(x-w/2-1,13.3,470.8),(x+w/2+2,17.8,473),(x-w*.1,23+i%2*4,466)]
 rooftri('south facade folded brow',tri,'silver' if i%2 else 'pearl')
 sign(label,(x,5.0,470.65),.66,yaw=0)
 for xx in [x-w*.3,x+w*.3]:D('showroom light',(xx,1.0,470.6),(.16,1.5,.18),'light',role='shell')
 # Low terraces follow Aria Place without obstructing the public entry.
 D('street planter trough',(x, .55,475),(w-4,1.0,2),'stone',role='shell');D('terrace planting',(x,1.2,475),(w-4,.4,1.65),'leaf',role='shell')
for x in [-176,-140,-109,-51]:palm(x,477,6.8)
for z in [333,350,399,414,449]:
 for y in [2,6,10,14]:D('street facade horizontal seam',(-31.2,y,z),(.1,.045,13),'steel',role='shell')
# A monumental entry portal between the shards, scaled to the mall rather than a service door.
for z in [377,385]:beam('Crystals entry angled jamb',(-31,.15,z),(-26,16,z+2),.22,'silver',role='shell')
rooftri('Crystals entry canopy',[(-32,6.5,376),(-23,8,382),(-32,7.5,387)],'silver')
hotel='Waldorf'
for z in [544,557,595,612]:
 D('Waldorf podium shadow-box glazing',(-39.65,5.8,z),(.12,10.5,11),'blue',role='shell')
 for dz in [-5,-2.5,0,2.5,5]:D('Waldorf podium fin',(-39.4,5.8,z+dz),(.4,10.8,.10),'bronze',role='shell')
for x in [-117,-105,-76,-60,-48]:
 D('north podium glazing',(x,5.5,534.7),(8,9.8,.12),'blue',role='shell')
 for dx in [-4,0,4]:D('north podium fin',(x+dx,5.6,534.48),(.12,10.2,.38),'bronze',role='shell')
for y in [2.2,10.9]:
 D('Waldorf lower cornice',(-39.3,y,578),(.8,.3,86),'bronze',role='shell');D('Waldorf north cornice',(-82,y,534.4),(86,.3,.8),'bronze',role='shell')
sign('WALDORF ASTORIA',(-91,6.2,534.25),.7,yaw=math.pi)
hotel='Aria'
for z in [356,373,413,481]:
 D('Aria podium glazing',(-281.65,6.7,z),(.12,11.7,14),'blue',role='shell')
 for dz in [-6,-3,0,3,6]:D('Aria podium curtain fin',(-281.4,6.8,z+dz),(.3,11.9,.1),'silver',role='shell')
for z in [427,469]:
 for x in [-278,-270,-261,-252]:D('Aria lobby window',(x,6,z),(6.5,10.8,.12),'blue',role='shell')
for i in range(15):
 z=426+i*3;D('Aria canopy warm slat',(-234,7.65,z),(17,.10,.25),'timber',role='shell')
for z in [420,483]:palm(-250,z,7.5)


# Low tram guideway with elevated walks: architecture only, no moving service.
hotel='Streets'
guide=[(-225,284),(-242,327),(-235,364),(-231,393),(-215,431),(-198,455),(-178,493),(-172,542),(-185,631)]
for a,b in zip(guide,guide[1:]):
 dx=b[0]-a[0];dz=b[1]-a[1];L=math.dist(a,b);yaw=math.atan2(-dz,dx)
 D('Aria Express guideway',((a[0]+b[0])/2,10.3,(a[1]+b[1])/2),(L+.6,.8,3.4),'stone',yaw=yaw)
 for side in [-1,1]:D('tram rail',((a[0]+b[0])/2+dz/L*side*.8,10.77,(a[1]+b[1])/2-dx/L*side*.8),(L+.6,.12,.14),'steel',yaw=yaw)
 B('tram pier',(a[0],5,a[1]),(.7,10,.7),'stone')
# Street lamps, benches, abandoned delivery crates; keep all pedestrian axes clear.
for z in range(319,642,23):
 beam('street lamp',(-23,.075,z),(-23,6,z),.09,'steel');D('street lamp head',(-23,6,z),(.45,.12,1.1),'light')
for x,z in [(-47,484),(-223,338),(-455,496),(-150,627),(-358,281)]:
 for i in range(3):B('abandoned supply crate',(x+i*1.3,.53,z),(1.1,1.0,.9),'wood')
landmark(P+'Aria Place view',(-18,.1,516),tags=['vista','citycenter'])
route('Strip south walk',[(-27,.075,278),(-27,.075,309),(-27,.075,382),(-27,.075,482),(-27,.075,507),(-27,.075,535),(-27,.075,637)])

# Stair flight colliders deliberately meet/overlap their landing slabs. Trim
# only the covered render faces so the final tread cannot fight the gallery.
bpy.context.view_layer.update()
trimmed_treads=0
for ob in list(bpy.data.objects):
 if ob.type!='MESH' or not ob.name.startswith(P) or ' tread ' not in ob.name:continue
 me=ob.data;matrix=ob.matrix_world;inverse=matrix.inverted();vertices=[];faces=[];changed=False
 for f in me.polygons:
  world=[matrix @ me.vertices[i].co for i in f.vertices]
  normal=matrix.to_3x3() @ f.normal
  covers=[r for r in floor_slabs if abs(r['top']-world[0].z)<1e-5] if normal.z>.99 else []
  x0,x1=min(v.x for v in world),max(v.x for v in world)
  z0,z1=min(-v.y for v in world),max(-v.y for v in world)
  pieces=[(x0,x1,z0,z1)]
  for r in covers:
   pieces=[part for rect in pieces for part in subtract_rectangle(rect,(r['x0'],r['x1'],r['z0'],r['z1']))]
  if covers and pieces!=[(x0,x1,z0,z1)]:
   changed=True
   for a,b,c,d in pieces:
    base=len(vertices);vertices.extend(tuple(inverse @ Vector((x,-z,world[0].z))) for x,z in [(a,d),(b,d),(b,c),(a,c)]);faces.append(tuple(range(base,base+4)))
  else:
   base=len(vertices);vertices.extend(tuple(me.vertices[i].co) for i in f.vertices);faces.append(tuple(range(base,len(vertices))))
 if changed:
  out=bpy.data.meshes.new(me.name+' landing trimmed');out.from_pydata(vertices,[],faces);out.update()
  for material in me.materials:out.materials.append(material)
  ob.data=out;trimmed_treads+=1
print('Trimmed coplanar stair landing faces:',trimmed_treads,flush=True)

# Resolve shared gallery / connector floor surfaces before material batching.
for owner,m,role,vs,fs in slab_union(floor_slabs):
 hotel=owner;M('continuous slab surface',vs,fs,m,role=role)
Path('build/citycenter/slab-surfaces.json').write_text(json.dumps(floor_slabs,indent=2))

# Material batches are saved in the editable source; semantic roles prevent the
# high folded roofs being mistaken for interior props by the visibility exporter.
for (owner,m,role),g in batches.items():
 name=P+owner+' / '+role+' / '+m;me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y) for x,y,z in g['v']],[],g['f']);me.update();ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);me.materials.append(bpy.data.materials['cc_'+m]);ob['visibilityRole']=role
 uv=me.uv_layers.new(name='CityCenterUV')
 for p in me.polygons:
  axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.25,v[axes[1]]*.25)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for ob in labels:
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));o=bpy.data.objects.new(ob.name+' glyphs',me);scene.collection.objects.link(o);o.matrix_world=ob.matrix_world.copy();o['visibilityRole']=ob['visibilityRole']
bpy.data.batch_remove(labels)
addition=level.mesh_level_json()
for field in ['colliders','volumes','lights','landmarks']:data[field]+=addition[field]
for field in ['links','stairs','doors']:data['extras'][field]+=addition['extras'][field]
Path('build/citycenter/addition.mesh-level.json').write_text(json.dumps(addition,indent=2))
Path('build/level/vegas.mesh-level.json').write_text(json.dumps(data,indent=2))
Path('build/level/vegas.doors.json').write_text(json.dumps(old_doors+level.doors_json(),indent=2))
from veer_access import build as build_veer_access
build_veer_access()
orient_closed_solids();bpy.context.scene['citycenter_v1']=True;bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
print('CITYCENTER COMPLETE',serial,'solids',len(addition['colliders']),'volumes',len(addition['volumes']),'doors',len(level.doors),'batches',len(batches),flush=True)
