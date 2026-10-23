"""Rebuild the entrances AND the adjoining spaces, using photo-specific layouts.
Idempotent: starts from an immutable pre-reconstruction local stage. Original level untouched.
"""
import bpy,bmesh,json,math,sys,copy
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from arrival_architecture import Builder,materials,material,PI,TAU
from visibility_export import building
OUT=Path('build/arrival-reconstruction');BASE=OUT/'before'
bpy.ops.wm.open_mainfile(filepath=str((BASE/'staged-vegas.blend').resolve()))
data=json.loads((BASE/'staged-vegas.mesh-level.json').read_text());towers=json.loads(Path('src/work/hotels/towers.json').read_text());materials()
# u across the facade, +v indoors. Distinct plans, not a universal lobby prefab.
SPECS=[
 ('crystals','crystals',(-32,.075,381),-PI/2,26,48,16,'CityCenter / Crystals arcade east'),
 ('aria','aria',(-244,.075,448),-PI/2,26,30,10,'CityCenter / Aria lobby east'),
 ('waldorf','waldorf',(-40,.075,576),-PI/2,9,32,5.4,'CityCenter / Waldorf arrival lobby east'),
 ('vdara','vdara',(-299,.075,273),PI,22,29,6.5,'CityCenter / Vdara lobby south'),
 ('cosmopolitan','cosmopolitan',(-29,.075,242),-PI/2,24,30,7.4,'Cosmopolitan Strip entrance'),
 ('paris','paris',(72,.075,-39),PI/2,24,16,7.6,'paris_west_entrance'),
 ('caesars','caesars',(-92,.075,-242),-PI/2,24,27,9.2,'caesars_main'),
 ('flamingo','flamingo',(90,.075,-237),PI/2,20,30,7.5,'Interiors / Flamingo west'),
 ('horseshoe','horseshoe',(110,.075,-147),0,30,32,7.5,'Interiors / Horseshoe north'),
 ('planet-hollywood','planet-hollywood',(65,.075,218),PI/2,24,29,10,'Interiors / Planet Hollywood west'),
 ('bellagio-south','bellagio',(-155,.075,-76),0,26,23,7.7,'bellagio_south_entrance'),
 ('bellagio-gallery','bellagio',(-131,.075,34),-PI/2,14,26,7.7,'bellagio_north_gallery_exit'),
 ('veer-east','crystals',(-115,.075,453.42520405653335),-PI/2,14,14,7,'Arrival / Veer east residential lobby'),
 ('veer-west','crystals',(-179,.075,422.57479594346665),-PI/2,14,14,7,'Arrival / Veer west residential lobby')]
def reserved(p):
 for t in towers:
  dx=p[0]-t['origin'][0];dz=p[2]-t['origin'][2];c,s=math.cos(t['yaw']),math.sin(t['yaw']);x=c*dx-s*dz;z=s*dx+c*dz
  if abs(x)<4.1 and abs(z)<5.65 and -.1<p[1]<t['firstGuestFloor']*3.6+.5:return True
 return False
builders=[Builder(*s[:7],reserved=reserved) for s in SPECS]

def local(b,p):
 dx,dy,dz=[p[i]-b.origin[i] for i in range(3)];c,s=math.cos(b.yaw),math.sin(b.yaw);return(c*dx-s*dz,dy,s*dx+c*dz)
for b in builders:
 b.floor_exclusions=[]
 for t in towers:
  c,s=math.cos(t['yaw']),math.sin(t['yaw']);ox,oy,oz=t['origin']
  corners=[local(b,(ox+c*x+s*z,oy,oz-s*x+c*z)) for x in [-4.2,4.2] for z in [-7.5,5.75]]
  b.floor_exclusions.append((min(p[0] for p in corners),max(p[0] for p in corners),min(p[2] for p in corners),max(p[2] for p in corners)))
def bounds(b,exterior=False):
 return (-b.w/2-.35,.07,-(.70 if not exterior else 10.5)),(b.w/2+.35,b.h+.45,b.d+.1)

# Clip existing polygons against the remodel's rectangular spatial envelope.
# This cuts the actual opaque wall away. Large batched meshes retain their
# geometry/UVs outside the work, rather than removing an entire resort batch.
def split(poly,axis,cut,upper):
 inside=[];outside=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a[axis]-cut)*(1 if upper else -1);db=(b[axis]-cut)*(1 if upper else -1)
  dest=inside if da<=1e-7 else outside;dest.append(a)
  if (da<0 and db>0) or (da>0 and db<0):
   t=da/(da-db);v=tuple(a[i]+t*(b[i]-a[i]) for i in range(len(a)));inside.append(v);outside.append(v)
 return inside,outside

def subtract(poly,lo,hi):
 remaining=poly;parts=[]
 for ax,limit,upper in [(0,lo[0],False),(0,hi[0],True),(1,lo[1],False),(1,hi[1],True),(2,lo[2],False),(2,hi[2],True)]:
  if len(remaining)<3:break
  remaining,outside=split(remaining,ax,limit,upper)
  if len(outside)>=3:parts.append(outside)
 return parts

report={'clippedObjects':[],'collidersRemoved':0,'properties':{},'routes':[]}
bpy.context.view_layer.update()
for ob in list(bpy.data.objects):
 if ob.type!='MESH':continue
 owner=building(ob.name)
 if not owner:continue
 # The Eiffel structure, hotel guest cores and Bellagio porte cochere retain ownership.
 if any(q in ob.name.lower() for q in ['eiffel tower','tower truss','leg lattice','bellagio arrival','hotel shell','guest core','staircore','guest vestibule']):continue
 boxes=[b for b in builders if b.owner==owner]
 if not boxes:continue
 world=[ob.matrix_world@v.co for v in ob.data.vertices];game=[(v.x,v.z,-v.y) for v in world]
 if not game:continue
 glo=[min(p[i] for p in game) for i in range(3)];ghi=[max(p[i] for p in game) for i in range(3)]
 def overlaps(b):
  lo,hi=bounds(b,True);corners=[b.world((x,y,z)) for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]
  return all(ghi[i]>=min(p[i] for p in corners) and glo[i]<=max(p[i] for p in corners) for i in range(3))
 boxes=[b for b in boxes if overlaps(b)]
 if not boxes:continue
 uv=ob.data.uv_layers.active;newv=[];newf=[];newuv=[];mi=[];smooth=[];changed=0
 for face in ob.data.polygons:
  original=[(*game[ob.data.loops[j].vertex_index],*(uv.data[j].uv if uv else (0,0))) for j in face.loop_indices];parts=[original]
  for b in boxes:
   nextparts=[];exterior=b.owner!='bellagio'
   lo,hi=bounds(b,exterior)
   for part in parts:
    lp=[(*local(b,p[:3]),p[3],p[4]) for p in part]
    if any(max(p[i] for p in lp)<lo[i]+.0001 or min(p[i] for p in lp)>hi[i]-.0001 for i in range(3)) or any(reserved(p[:3]) for p in part):nextparts.append(part);continue
    cut=subtract(lp,lo,hi)
    changed+=1
    for frag in cut:nextparts.append([(*b.world(p[:3]),p[3],p[4]) for p in frag])
   parts=nextparts
  for part in parts:
   if len(part)<3:continue
   start=len(newv);newv.extend((p[0],-p[2],p[1]) for p in part);newf.append(tuple(range(start,start+len(part))));newuv.extend((p[3],p[4]) for p in part);mi.append(face.material_index);smooth.append(face.use_smooth)
 if changed:
  report['clippedObjects'].append({'name':ob.name,'faces':changed})
  if not newf:bpy.data.objects.remove(ob,do_unlink=True);continue
  old=ob.data;me=bpy.data.meshes.new(ob.name+' remodel');me.from_pydata(newv,[],newf);me.update()
  for m in old.materials:me.materials.append(m)
  uvn=me.uv_layers.new();uvn.data.foreach_set('uv',[c for u in newuv for c in u])
  for f,m,s in zip(me.polygons,mi,smooth):f.material_index=m;f.use_smooth=s
  ob.data=me;ob.matrix_world.identity()
print('Arrival shell openings clipped',len(report['clippedObjects']),flush=True)

# Collider subtraction for axis-aligned wall/furniture boxes. Existing ground,
# sloping stairs, lifts and upper hotel shells stay intact.
newcols=[]
for col in data['colliders']:
 owner=building(col['name']);cs=[col]
 if col['shape']=='box' and owner and not any(q in col['name'].lower() for q in ['stair','ramp','lift','guest','core']):
  for b in [b for b in builders if b.owner==owner]:
   more=[];bl,bh=bounds(b,False)
   for c in cs:
    yaw=c.get('yaw',0)-b.yaw
    if abs(math.sin(2*yaw))>.0001:more.append(c);continue
    p=local(b,c['position']);size=c['size'];sx,sz=(size[2],size[0]) if abs(math.sin(yaw))>.7 else(size[0],size[2]);lo=[p[0]-sx/2,p[1]-size[1]/2,p[2]-sz/2];hi=[p[0]+sx/2,p[1]+size[1]/2,p[2]+sz/2]
    if hi[1]<.15 or any(hi[i]<=bl[i] or lo[i]>=bh[i] for i in range(3)) or reserved(c['position']):more.append(c);continue
    report['collidersRemoved']+=1
    # Six disjoint boxes are the complement of the rectangular cut.
    qlo=lo[:];qhi=hi[:]
    for ax in range(3):
     for low in [True,False]:
      aa=qlo[:];bb=qhi[:]
      if low:bb[ax]=min(bb[ax],bl[ax]);qlo[ax]=max(qlo[ax],bl[ax])
      else:aa[ax]=max(aa[ax],bh[ax]);qhi[ax]=min(qhi[ax],bh[ax])
      if all(bb[i]-aa[i]>.015 for i in range(3)):
       cc=copy.deepcopy(c);cc['name']=c['name']+' / arrival cut '+str(ax)+str(low);cc['position']=list(b.world(tuple((aa[i]+bb[i])/2 for i in range(3))));cc['size']=[bb[i]-aa[i] for i in range(3)];cc['yaw']=b.yaw;more.append(cc)
   cs=more
 newcols.extend(cs)
data['colliders']=newcols
# Cull old light clusters in the rebuilt volume. A few bounded sources illuminate
# the authored fixtures; hundreds of bulbs remain emissive meshes, not lights.
data['lights']=[l for l in data['lights'] if not any(all(bounds(b)[0][i]<local(b,l['position'])[i]<bounds(b)[1][i] for i in range(3)) for b in builders)]

def marble_inlay(b,z,r):
 for rr,m in [(r,'granite'),(r-.11,'stone'),(r-.38,'granite')]:b.ring((0,.079,z),rr,.027,m)
 for i in range(0 if b.name=='waldorf' else 16):
  a=i*TAU/16;vs=[(rr*math.cos(aa),.083,z+rr*math.sin(aa)) for rr,aa in [(r-.45,a),(r*.35,a+.10),(r-.45,a+.18)]];b.mesh(vs,[(0,1,2)],'stone')
def paneled_wall(b,side,start,end,classic=False):
 x=side*(b.w/2-.14)
 for z in [start+i*2.7 for i in range(int((end-start)/2.7))]:
  b.box((x,b.h*.48,z),( .08,b.h*.70,2.45),'plaster')
  b.frame((x-side*.06,b.h*.48,z),2.14,b.h*.60,'gold',.04,PI/2)
  if classic:
   for y in [1.05,b.h-.78]:b.box((x-side*.10,y,z),(.13,.10,2.6),'gold')
   b.box((x-side*.22,b.h/2,z+1.32),(.34,b.h-.24,.38),'marble')
def queue(b,x,z,length=5,yaw=0):
 for i in range(4):
  u=x+math.cos(yaw)*i*length/3;v=z-math.sin(yaw)*i*length/3;b.lathe((u,0,v),[(.16,0),(.16,.06),(.025,.12),(.025,.94),(.055,.98),(.05,1.04)],'bronze',16)
  if i<3:b.tube([(u,.95,v),(u+math.cos(yaw)*length/6,.85,v-math.sin(yaw)*length/6),(u+math.cos(yaw)*length/3,.95,v-math.sin(yaw)*length/3)],.025,'red',sides=6)
def sidereception(b,side=1,z=13,length=12,m='walnut',name='RECEPTION'):
 x=side*(b.w/2-2.1);b.counter(x,z,length,PI/2,m)
 b.text(name,(x-side*1.0,2.25,z),.22,length-.5,'gold',-PI/2 if side>0 else PI/2)
 for v in [z-length/2+1,z+length/2-1]:b.planter(x-side*1.9,v,3.1,.34)

def standard_canopy(b,m='bronze',fan=False,depth=7):
 old=b.role;b.role='shell';w=min(b.w,23)
 # Curved metal soffit with front edge, ribs, recessed lights and stone piers.
 for j in range(32):
  x0=-w/2+j*w/32;x1=x0+w/32
  def p(x,z,off=0):return(x,b.h-.65+.65*math.cos(x/w*PI)+off,z)
  q=[p(x0,0),p(x1,0),p(x1,-depth),p(x0,-depth)];b.mesh(q+[(x,y+.22,z) for x,y,z in q],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(2,6,7,3)],m)
  if j%2==0:b.tube([p(x0,0,-.055),p(x0,-depth,-.055)],.035,'silver')
 for x in [-w/2+.55,w/2-.55]:b.column(x,-depth+.5,b.h-.1,.45,m='stone')
 for z in [-2,-4,-6]:
  for x in [-w*.3,0,w*.3]:b.downlight((x,b.h-.4,z),.15)
 b.role=old

def crystals(b):
 b.floor('stone',1.5);b.glass_front(15.8,frame='black');b.role='shell'
 b.text('THE SHOPS AT',(0,6.35,-.18),.40,10,'white');b.text('C R Y S T A L S',(0,5.5,-.18),.80,15,'white');b.text('A  S I M O N  C E N T E R',(0,4.8,-.18),.24,9,'white')
 for x in [-1.0,1.0]:b.tube([(x-.8,7.5,-.2),(x,8,-.2),(x+.8,7.5,-.2),(x,7,-.2)],.055,'white',True)
 # Folded, off-axis canopy + brushed metal seams, attached to glazing.
 q=[(-14,15.9,.2),(14,15.9,.2),(9,13.5,-5),(-10,10.6,-6)];b.mesh(q,[(0,1,2),(0,2,3)],'silver');b.tube(q,.12,'black',True)
 for x in [-11,11]:b.planter(x,-2,4.4,.6,'black')
 b.role='interior'
 # Layered gallery: tall angular floating volumes above two distinct store rows.
 for side in [-1,1]:
  for i,(z,wid) in enumerate([(9,9),(21,10),(34,11)]):
   x=side*(b.w/2-1.5);a=side*(.07 if i%2 else -.09)
   b.box((x,5.0,z),(3,9.8,wid),'white',a)
   b.box((x-side*1.53,3.25,z),(.045,5.7,wid-1.0),'black',a)
   b.box((x-side*1.58,3.05,z),(.025,5.2,wid-1.25),'glass',a)
   for dz in [-wid/2+.6,0,wid/2-.6]:b.box((x-side*1.64,3,z+dz),(.06,5.8,.07),'silver')
   brand=(['LOUIS VUITTON','BOTTEGA VENETA','DIOR'] if side<0 else ['TIFFANY & CO.','GUCCI','CARTIER'])[i]
   b.text(brand,(x-side*1.64,6.8,z),.34,wid-1,'black',-side*PI/2)
   for j in [-1,1]:
    b.box((x-side*1.76,.58,z+j*2.4),(.9,1.04,1.15),'stone',bevel=.03)
    b.lathe((x-side*1.8,1.11,z+j*2.4),[(.16,0),(.24,.26),(.19,.40)],'gold',20)
    b.downlight((x-side*2.5,8.7,z+j*2.4))
  # Asymmetric planes read as folded architecture, not a flat suspended lid.
  b.mesh([(side*13,10.2,1),(side*13,15.7,23),(side*3.5,17.3,18),(side*5,11.7,1)],[(0,1,2,3)],'white')
  b.mesh([(side*13,15.7,23),(side*13,11.5,48),(side*3.5,13.8,48),(side*3.5,17.3,18)],[(0,1,2,3)],'white')
  b.tube([(side*5,11.62,1),(side*3.5,17.22,18),(side*3.5,13.72,48)],.065,'warm')
 b.mesh([(-5,11.7,1),(5,11.7,1),(3.5,17.3,18),(-3.5,17.3,18)],[(0,1,2,3)],'glass')
 # Timber sculptural concierge at the gallery's far end, offset from circulation.
 for j in range(65):
  a=j*TAU/64;pts=[(-6+(2.4+.8*math.cos(y*.5))*math.cos(a),y,40+(2.1+.7*math.cos(y*.5))*math.sin(a)) for y in [i*.3 for i in range(28)]];b.tube(pts,.05,'wood')
 b.counter(-6,39.1,3.8,0,'wood','CONCIERGE');b.text('CONCIERGE',(-6,1.0,38.43),.20,3,'white')
 for x,z in [(-7,4),(7,4),(-6,29),(6,29)]:b.planter(x,z,4,.52,'white')
 for x in [-5,5]:b.sofa(x,24,3,'linen',PI/2);b.ring((x,.08,24),2,.04,'granite')
 for z in [6,17,29,41]:b.light((0,8,z),160,'#f6f4ed',23)

def aria(b):
 b.floor('stone',1.4);b.glass_front(9.9,frame='silver');standard_canopy(b,'silver',depth=9);b.sidewalls('stone');b.ceiling('walnut')
 for z in [5,13,21,28]:
  for side in [-1,1]:b.column(side*9.4,z,9.8,.66,m='stone')
  # Woven diamond coffers: inset mesh lattice, light slots and heavy curved soffits.
  for x in [-6,0,6]:
   b.coffer(x,z,5.6,6.6,9.6,'wood')
   for j in range(-3,4):
    b.tube([(x-2.4,9.33,z+j*.7-1.5),(x+2.4,9.33,z+j*.7+1.5)],.025,'gold',sides=5)
   b.downlight((x,9.23,z),.14)
 sidereception(b,-1,17,16,'granite','ARIA / RECEPTION')
 # Abstract polished river runs above check-in, with branching tributaries.
 for i in range(4):
  pts=[(-10.6+i*.10,4.6+.8*math.sin(j*.30+i*.3),8+j*.38) for j in range(46)];b.tube(pts,.14,'silver',sides=10)
 for j in range(10):b.tube([(-10.5,5,9+j*1.5),(-10.25,5.7,10+j*1.5),(-10.0,6.0,11+j*1.5)],.055,'silver')
 for z in [8,18,26]:b.sofa(7,z,3.1,'teal',PI/2);b.planter(9.5,z+1.9,4.5,.6,'black')
 for j in range(14):
  z=2+j*1.9;b.mesh([(-8,.08,z),(-4,.08,z+.6),(4,.08,z-.2),(8,.08,z+.8),(8,.08,z+1.05),(4,.08,z+.05),(-4,.08,z+.85),(-8,.08,z+.25)],[(0,1,2,3,4,5,6,7)],'marble')
 for z in [5,15,25]:b.light((0,6,z),105,'#fff1d9',18)

def waldorf(b):
 b.floor('marble',1.2);b.glass_front(5.35,frame='bronze');b.sidewalls('marble');b.ceiling('plaster');b.role='shell'
 for side in [-1,1]:b.box((side*4.9,2.8,-1),(.85,5.6,2.5),'red');b.box((side*5.5,3.1,-.6),(.4,6.2,3.3),'stone')
 b.box((0,5.65,-1.2),(11.5,.4,3.8),'stone');b.text('WALDORF ASTORIA',(0,5.15,-3.12),.28,8,'black');b.role='interior'
 for z in [5,12,19,27]:
  marble_inlay(b,z,3.3);b.coffer(0,z,8.4,6.4,5.15,'plaster');b.chandelier(0,z,4.98,1.28,.65,'rods')
  for side in [-1,1]:
   b.box((side*4.2,2.45,z+2.8),(.48,4.9,.6),'marble');b.box((side*3.93,2.45,z+2.8),(.03,4.65,.035),'gold')
   b.frame((side*4.32,2.5,z),4.8,4.45,'gold',.025,PI/2)
 for z in [7,21]:
  for side in [-1,1]:b.sofa(side*3.35,z,2.4,'teal' if side<0 else 'linen',side*PI/2);b.planter(side*3.3,z+2.2,3.2,.38)
 # Freestanding terminal art wall leaves 2m passage on both sides.
 b.box((0,2.5,30),(4.2,5,.28),'marble',solid=True);b.frame((0,2.9,29.82),1.95,3.1,'gold',.04)
 b.box((0,2.9,29.8),(1.82,2.98,.035),'walnut')
 for i in range(9):b.lathe((.25*math.sin(i*.7),1.6+i*.28,29.68),[(.12,0),(.30,.12),(.08,.23)],'red',18,sx=1,sz=.16)
 b.lathe((0,0,28.7),[(.7,0),(.4,.15),(.25,.8),(.85,.88),(.85,.94)],'granite');b.vase(0,28.7,.94)

def vdara(b):
 b.floor('marble',1.3);b.glass_front(6.4,frame='silver');b.sidewalls('plaster');standard_canopy(b,'silver',depth=10);b.ceiling('plaster')
 # Curved low ceiling coves, walnut slats and angular wooden pendant sculptures.
 for j in range(36):
  x=-10.7+j*.6;y=6.25-.48*math.cos(x/22*PI);b.box((x,y,14),(.065,.17,27),'wood')
 for z in [7,16,25]:
  for i in range(8):
   a=i*2.4;b.box((math.cos(a)*2.8,5.05+(i%3)*.25,z+math.sin(a)*1.8),(3.9,.16,.28),'walnut',a,bevel=.035);b.box((math.cos(a)*2.8,4.94+(i%3)*.25,z+math.sin(a)*1.8),(2.7,.025,.07),'warm',a);b.tube([(math.cos(a)*2.8,5.1,z+math.sin(a)*1.8),(math.cos(a)*2.8,6.3,z+math.sin(a)*1.8)],.009,'black',sides=5)
  b.light((0,4.3,z),95,distance=16)
 sidereception(b,1,16,18,'granite','VDARA')
 b.box((10.79,3.05,16),(.08,5.3,21),'walnut');b.box((10.69,3.1,16),(.06,3.1,17),'wood')
 # Original geometric artwork inspired by the reference's colored interlocking arcs.
 for k,(z,color) in enumerate([(10,'red'),(13,'blue'),(16,'lime'),(19,'violet'),(22,'gold')]):
  b.tube([(10.59,3.0+1.25*math.sin(a),z+2.4*math.cos(a)) for a in [j*PI/50 for j in range(51)]],.15,color)
  b.tube([(10.52,3.0-1.05*math.sin(a),z+2.0*math.cos(a)) for a in [j*PI/50 for j in range(51)]],.12,'linen')
 for j in range(75):b.box((-10.75,2.85,1+j*.36),(.12,5.4,.07),'wood')
 for z in [6,17,25]:b.sofa(-8.9,z,3.4,'linen',PI/2);b.planter(-7.6,z+2.1,3.4,.4,'silver')
 # Organic multicolor rug with irregular overlapping elliptical leaf shapes.
 b.box((-1,.080,15.5),(9,.01,22),'fabric')
 for i in range(100):
  x=-4.9+(i*1.618)%8;z=4.8+(i*2.41)%21;r=.25+(i%4)*.15
  b.lathe((x,.088+i%3*.001,z),[(r,0),(r,.002)],['teal','wood','linen','blue','stone'][i%5],18,sx=1,sz=1.8)

def cosmo(b):
 b.floor('granite',1.2);b.glass_front(7.35,frame='black',doorwidth=6,doorheight=4.3);b.sidewalls('black');b.ceiling('black');b.role='shell'
 for j in range(28):
  x=-12+j*.86;b.box((x,6.8,-4),( .30,.15,8),'blue');b.tube([(x,6.65,0),(x+.55,6.65,-4),(x,6.65,-8)],.026,'cool')
 b.box((0,7.0,-8),(24,.7,.5),'black');b.text('THE COSMOPOLITAN',(0,6.96,-8.3),.50,19,'white');b.role='interior'
 for z in [6,15,24]:
  for x in [-6.6,6.6]:
   b.box((x,3.5,z),(1.35,7,1.35),'mirror',bevel=.035)
   for side in [-1,1]:
    for j in range(14):b.box((x+side*.696,.30+j*.48,z),(.015,.46,1.29),['blue','teal','violet','pink'][((j//3)+(0 if z<10 else 1))%4])
    for y in [.12,2.4,4.8,6.96]:b.box((x+side*.714,y,z),(.05,.035,1.34),'silver')
   b.frame((x,3.5,z-.704),1.33,6.94,'silver',.035)
  b.coffer(0,z,10.5,7.5,7.15,'black');b.chandelier(0,z,6.75,1.8,1.3,'rods')
 sidereception(b,-1,16,19,'walnut','THE COSMOPOLITAN')
 for z in [8,16,25]:b.sofa(10,z,3,'teal',-PI/2);b.planter(9,z+2,3.5,.4,'black')
 for z in range(2,29,2):b.box((0,.081,z),(9,.006,.025),'silver')

def paris(b):
 b.floor('marble',1.2);b.sidewalls('marble');b.ceiling('plaster');b.glass_front(7.45,frame='sage',doorwidth=6,doorheight=4.8);b.role='shell'
 # Curving green glass barrel, scrolled supports and fanlight.
 for j in range(33):
  x=-12+j*.75;y=5.8+1.8*math.cos(x/12*PI/2)
  if j<32:
   xx=x+.75;yy=5.8+1.8*math.cos(xx/12*PI/2);b.mesh([(x,y,0),(xx,yy,0),(xx,yy,-9),(x,y,-9)],[(0,1,2,3)],'glass')
  b.tube([(x,y,0),(x,y,-9)],.04,'sage')
 for z in [0,-2,-4,-6,-9]:b.tube([(-12+j*.5,5.8+1.8*math.cos((-12+j*.5)/12*PI/2),z) for j in range(49)],.12,'sage')
 for x in [-11.5,11.5]:b.column(x,-8.4,5.9,.28,True,'sage')
 b.text('P A R I S',(0,6.25,-9.15),.6,8,'gold');b.arch((0,0,-.19),9,7.3,'sage',.13)
 for i in range(11):
  a=i*PI/10;b.tube([(0,3.5,-.17),(4.35*math.cos(a),3.5+3.65*math.sin(a),-.17)],.034,'sage')
 b.role='interior'
 for side in [-1,1]:paneled_wall(b,side,1,16,True)
 for x in [-7,0,7]:
  for z in [4,11.5]:b.coffer(x,z,6.5,6.4,7.3,'plaster');b.chandelier(x,z,6.8,1.15,1.7)
 sidereception(b,-1,9,10,'marble','LA RECEPTION')
 for z in [4,12]:marble_inlay(b,z,3.1)
 for side in [-1,1]:
  b.column(side*10.8,2,7.3,.34,True)
  for z in [4,10,14]:
   # Gilt scrollwork and wall sconces are dimensional details, not printed outlines.
   for k in [-1,1]:b.tube([(side*10.8+k*.5*math.cos(a),5.8+.35*math.sin(a),z) for a in [j*TAU/32 for j in range(33)]],.027,'gold')
 for z in [5,12]:b.sofa(9,z,2.7,'red',-PI/2)

def caesars(b):
 b.floor('marble',1.25);b.sidewalls('marble');b.glass_front(7.8,frame='bronze',doorwidth=6,doorheight=4.8);standard_canopy(b,'marble',depth=8)
 for side in [-1,1]:
  paneled_wall(b,side,2,27,True)
  for z in [3,10,17,24]:b.column(side*10.9,z,7.7,.48,True)
 # True curved coffered dome; sculptural rings and recessed individual coffers.
 cx,cz=0,13
 for k in range(8):
  t0=k*PI/16;t1=(k+1)*PI/16
  for j in range(64):
   a=j*TAU/64;aa=(j+1)*TAU/64
   def p(t,a):return(10*math.cos(t)*math.cos(a),6.6+2.5*math.sin(t),cz+10*math.cos(t)*math.sin(a))
   b.mesh([p(t0,a),p(t0,aa),p(t1,aa),p(t1,a)],[(0,1,2,3)],'plaster')
   if j%4==0 and k<6:b.tube([p(t,a) for t in [t0,t1]],.055,'gold')
  b.ring((0,6.58+2.5*math.sin(t0),cz),10*math.cos(t0),.07,'gold')
 # Four corner soffits close the square room around the dome.
 for x in [-10.5,10.5]:b.box((x,7.2,13),(3,1.1,27),'marble')
 for z in [1,25]:b.box((0,7.2,z),(24,1.1,3),'marble')
 b.chandelier(0,13,8.4,3.1,2.2);marble_inlay(b,13,8)
 for z in [3,23]:b.light((0,5.5,z),110,distance=18)
 # Statue niche offset from clear axial circulation.
 b.lathe((-7,0,13),[(1.1,0),(1.1,.18),(.85,.28),(.85,1.1),(1.0,1.25)],'marble')
 b.lathe((-7,1.24,13),[(.42,0),(.60,.10),(.50,1.5),(.42,1.9),(.57,2.1),(.42,2.45),(.19,2.65),(.23,2.9),(.16,3.15)],'white')
 b.tube([(-7.42,3.7,13),(-8,3.9,13),(-8.4,4.65,13)],.13,'white');b.tube([(-6.6,3.7,13),(-6.25,3.0,13),(-6.3,2.4,13)],.14,'white')
 for i in range(16):a=i*TAU/16;b.tube([(-7+.48*math.cos(a),1.42,13+.48*math.sin(a)),(-7+.43*math.cos(a),2.8,13+.43*math.sin(a))],.027,'stone')
 b.text('CAESARS PALACE',(-7,1.0,12.12),.15,1.6,'gold')
 for z in [6,21]:b.sofa(8,z,3,'red',-PI/2);b.planter(8,z+2.2,3.1,.4)

def flamingo(b):
 b.floor('marble',1.2);b.glass_front(7.4,frame='gold');b.sidewalls('stone');b.ceiling();b.role='shell'
 for i in range(41):
  a=i*PI/40;x=12*math.cos(a);y=4.1+5.0*math.sin(a);b.tube([(0,4,-.2),(x,y,-5.5)],.13,'pink');b.tube([(x,y,-5.5),(x,4.0,-7)],.045,'gold')
 b.text('Flamingo',(0,5.25,-7.15),1.0,12,'pink');b.role='interior'
 for z in [4,11,18,25]:
  for x in [-6,0,6]:b.coffer(x,z,5.5,6.4,7.15,'plaster')
  b.chandelier(0,z,6.9,1.25,.9,'rods')
 sidereception(b,-1,16,20,'marble','FLAMINGO / CHECK IN')
 for j in range(70):
  z=2+j*.38
  for i in range(8):b.box((-9.85,1.65+i*.44,z),(.08,.38,.33),['gold','stone','marble'][((j*7+i*3)%5)%3])
 for z in [5,14,23]:b.sofa(7,z,3,'red',-PI/2);b.planter(8,z+2.2,4,.55)
 for z in [7,10,13]:
  b.box((4,.68,z),(.65,1.2,.45),'white',bevel=.04);b.box((4,1.38,z-.15),(.55,.48,.08),'black');b.text('CHECK IN',(4,1.35,z-.2),.085,.47,'cool')

def horseshoe(b):
 # The public entrance opens onto the eastern circulation aisle. Its previous
 # axis pointed straight at the persistent guest-stair enclosure, hiding the lobby.
 b.floor('marble',1.3);b.glass_front(7.4,frame='silver',doorheight=4.1,dooroffset=7);b.sidewalls('stone');b.ceiling('plaster');b.role='shell'
 b.arch((0,0,-6.5),17,9.2,'red',.7)
 for side in [-1,1]:b.column(side*10.5,-6.4,7.4,.6,m='white')
 for i in range(41):
  a=i*PI/40;b.tube([(10*math.cos(a),5.5+2.3*math.sin(a),-.2),(10*math.cos(a),5.5+2.3*math.sin(a),-6.5)],.075,'white')
 b.text('HORSESHOE',(0,6.45,-6.8),.70,14,'white');b.role='interior'
 # Finish the existing core's rear as a concierge wall, rather than leaving
 # bare service cladding opposite the glass. The circulation aisle is clear.
 b.box((-1,3.3,5.25),(7.3,6.6,.12),'walnut')
 for i in range(30):b.box((-4.5+i*.24,3.3,5.16),(.05,6.5,.04),'wood')
 b.text('HORSESHOE',(-1,4.2,5.08),.48,6.3,'gold')
 b.text('CONCIERGE',(-1,3.48,5.07),.18,4.5,'white')
 b.counter(-1,3.6,5.2,0,'marble','WELCOME')
 for j in range(24):
  z=1+j*1.3;b.box((0,7.1,z),(29,.15,.18),'stone');b.box((0,6.99,z),(28,.03,.035),'warm')
 # Registration gallery wraps around the existing guest stair instead of colliding with it.
 sidereception(b,1,18,21,'marble','HORSESHOE / REGISTRATION')
 for z in [6,14,23]:
  b.sofa(-11.8,z,3,'fabric',PI/2);b.planter(-12,z+2.0,3.2,.42)
  b.light((8,5.5,z),70,distance=14)
 for z in [7,11,15]:
  b.box((8,.65,z),(.6,1.15,.6),'granite',bevel=.035);b.box((8,1.36,z-.15),(.58,.5,.08),'black');b.text('SELF CHECK-IN',(8,1.34,z-.21),.07,.5,'cool')
 queue(b,10,17,8,PI/2)

def ph(b):
 b.floor('granite',1.4);b.glass_front(9.8,frame='black');b.sidewalls('black');b.ceiling('black');b.role='shell'
 for i in range(55):
  a=(i/54)*PI;b.tube([(0,6.5,0),(12*math.cos(a),6.0,-2-7*math.sin(a))],.095,'violet');b.tube([(0,6.35,0),(12*math.cos(a),5.85,-2-7*math.sin(a))],.03,'pink')
 b.text('planet hollywood',(0,6.75,-9.3),.70,16,'white');b.role='interior'
 # Nested oval atrium balconies and suspended crystal curtain, with open center.
 for y,r in [(6.4,9.9),(8.6,10.3),(9.7,8.8)]:
  b.ring((0,y,14),r,.65,'stone',1,1.28);b.ring((0,y-.08,14),r-.72,.055,'violet',1,1.28)
  for j in range(100):
   a=j*TAU/100;b.tube([(r*math.cos(a),y+.04,14+r*1.28*math.sin(a)),(r*math.cos(a),y+.8,14+r*1.28*math.sin(a))],.02,'silver',sides=5)
 for side in [-1,1]:
  for z in [5,13,23]:
   x=side*8.6;b.column(x,z,8.8,.7,m='black')
   for j in range(16):a=j*TAU/16;b.tube([(x+(.78+.13*math.sin(y*.8))*math.cos(a),y,z+(.78+.13*math.sin(y*.8))*math.sin(a)) for y in [i*.35 for i in range(25)]],.038,'crystal')
 sidereception(b,-1,16,18,'granite','PLANET HOLLYWOOD')
 for z in range(3,28):
  for y in [2,2.6,3.2,3.8,4.4,5]:b.ring((-11.65,y,z),.15,.035,'violet')
 b.chandelier(0,14,9.25,3.1,3.0)
 for z in [4,23]:b.sofa(10,z,3,'red',-PI/2)

def bellagio(b,gallery=False):
 b.floor('marble',1.3);b.glass_front(7.55,frame='bronze',doorwidth=5 if gallery else 6,doorheight=4.5);b.sidewalls('marble');b.ceiling('plaster')
 for side in [-1,1]:paneled_wall(b,side,1,b.d,True)
 for z in range(4,int(b.d),6):
  marble_inlay(b,z,min(4.0,b.w/2-1));b.coffer(0,z,b.w-1,5.5,7.4,'plaster')
  b.chandelier(0,z,6.7,1.5 if gallery else 2,1.9)
  for side in [-1,1]:b.column(side*(b.w/2-.65),z+2.5,7.3,.34,True)
 if not gallery:
  sidereception(b,1,13,14,'marble','BELLAGIO / RECEPTION')
  for z in [7,11,15,19]:
   b.box((12.78,3.65,z),(.07,4.6,3.3),'sage');b.frame((12.67,3.65,z),3.0,4.4,'gold',.035,PI/2)
   for y in [2.4,4.0,5.4]:b.box((12.62,y,z),(.03,.03,3.2),'gold')
  for z in [16]:b.sofa(-10,z,3,'teal',PI/2);b.vase(-9,z+2,.15)
 else:
  for side in [-1,1]:
   for z in [6,17]:b.sofa(side*5.4,z,2.5,'teal',side*PI/2);b.planter(side*5.3,z+2.2,3,.35)
  b.text('BELLAGIO',(0,5.8,24.9),.65,8,'gold');b.text('CASINO   /   GUEST GALLERY',(0,5.1,24.9),.22,9,'bronze')

def veer(b):
 b.floor('granite',1.1);b.glass_front(6.95,frame='silver',doorheight=3.4);b.sidewalls('glass');b.ceiling('plaster')
 b.role='shell';b.text('V E E R',(0,5.3,-.16),.66,9,'white');b.text('RESIDENCES',(0,4.5,-.16),.23,6,'white');b.role='interior'
 for x in [-5,5]:b.column(x,5,6.9,.58,m='stone');b.planter(x,2.0,4,.60,'red')
 b.sofa(-4.8,8.1,4,'linen',PI/2);b.sofa(-3.4,10.2,3,'linen',0);b.box((-2.8,.35,7.7),(1.3,.56,1.7),'lime',bevel=.13)
 b.counter(5,9,4,PI/2,'wood','CONCIERGE');b.text('CONCIERGE',(4.3,1.0,9),.16,3,'white',-PI/2)
 for z in [3,8,12]:
  for x in [-3,0,3]:b.downlight((x,6.85,z));b.box((x,6.8,z),(1.0,.08,1.0),'white')
  b.light((0,5,z),65,'#f1f3ee',13)

fun={'crystals':crystals,'aria':aria,'waldorf':waldorf,'vdara':vdara,'cosmopolitan':cosmo,'paris':paris,'caesars':caesars,'flamingo':flamingo,'horseshoe':horseshoe,'planet-hollywood':ph}
newportals=[]
for b,spec in zip(builders,SPECS):
 if b.name.startswith('bellagio'):bellagio(b,'gallery' in b.name)
 elif b.name.startswith('veer'):veer(b)
 else:fun[b.name](b)
 b.finish();data['colliders'].extend(b.colliders);data['lights'].extend(b.lights)
 # Arrival zone is explicit: only this bounded space previews through the glass.
 data['volumes'].append(dict(name='Arrival / '+b.owner+' / '+b.name,position=list(b.world((0,b.h/2,b.d/2))),size=[b.w+.5,b.h+.5,b.d+.5],yaw=b.yaw,tags=['indoors','public','windowed','arrival']))
 report['properties'][b.name]={'components':b.components,'batches':len(b.groups),'colliders':len(b.colliders),'lights':len(b.lights),'dimensions':[b.w,b.d,b.h],'origin':b.origin,'yaw':b.yaw,'door':spec[7]}
 if b.name=='horseshoe':report['properties'][b.name]['doorOffset']=7
 report['routes'].append({'name':b.name,'origin':b.origin,'yaw':b.yaw,'depth':b.d})
 if b.name.startswith('veer'):newportals.append(dict(id=spec[7],position=dict(zip(['x','y','z'],b.world((0,1.7,0)))),rotationY=b.yaw,width=5,height=3.4,thickness=.14,kind='plain',animation='slide',autoOpenRadius=5))
 print('ARRIVAL',b.name,b.components,len(b.colliders),flush=True)
# Three authored leaf finishes. Engine owns their animation, physics and interaction.
for style in ['bronze','silver','black','sage']:
 b=Builder('leaf-'+style,'', (0,0,0),0,5,0,4.2);b.role='shell'
 for i in range(4):
  x=-2.5+(i+.5)*1.25;b.box((x,2.1,0),(1.19,4.08,.023),'glass');b.frame((x,2.1,-.005),1.25,4.2,style,.052)
  b.box((x,2.75,-.02),(1.22,.09,.09),style)
  b.box((x,.18,-.02),(1.13,.2,.075),style);b.box((x,1.0,-.02),(1.13,.045,.06),style)
  for sign in [-1,1]:
   xx=x+(.42 if i%2==0 else -.42);b.tube([(xx,1.0,sign*.11),(xx,1.7,sign*.11)],.019,'silver');b.tube([(xx,1.05,0),(xx,1.05,sign*.11)],.018,'silver');b.tube([(xx,1.65,0),(xx,1.65,sign*.11)],.018,'silver')
  b.box((x,1.50,.018),(.3,.04,.002),'white')
 obs=b.finish();bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.export_scene.gltf(filepath=str((OUT/('door-'+style+'.glb')).resolve()),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_lights=False)
 bpy.data.batch_remove(obs)
(OUT/'extra-doors.json').write_text(json.dumps(newportals,indent=2))
(OUT/'door-overrides.json').write_text(json.dumps({'Interiors / Horseshoe north':{'position':{'x':117,'y':2.125,'z':-147}}},indent=2))
for landmark in data['landmarks']:
 if landmark['name']=='Interiors / Horseshoe entrance':landmark['position'][0]=117
data.setdefault('extras',{})['arrivalReconstruction']={'version':2,'properties':list(report['properties'])}
Path('build/hotels/staged-vegas.mesh-level.json').write_text(json.dumps(data,indent=2))
(OUT/'report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(Path('build/hotels/staged-vegas.blend').resolve()))
print('RECONSTRUCTION COMPLETE',len(builders),flush=True)
