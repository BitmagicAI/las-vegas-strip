"""Deterministic, editable central Strip environment. Game coordinates: X east, -Z north."""
import os, sys, math, random, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'blender-level'))
from bmlevel import *
import bpy, numpy as np
from mathutils import Vector
_box, _decor, _text = box, decor, text
def box(name,*args,**kwargs):return _box(scene.collection.name+' / '+name,*args,**kwargs)
def decor(name,*args,**kwargs):return _decor(scene.collection.name+' / '+name,*args,**kwargs)
def text(name,string,pos,material,yaw=0,size=.5,extrude=.01,both_faces=False):
 def glyph(label,at,angle):
  curve=bpy.data.curves.new(label,'FONT');curve.body=string;curve.size=size;curve.extrude=extrude;curve.align_x='CENTER'
  obj=bpy.data.objects.new(scene.collection.name+' / '+label,curve);scene.collection.objects.link(obj);obj.location=(at[0],-at[2],at[1]);obj.rotation_euler=(math.pi/2,0,angle);curve.materials.append(bpy.data.materials[material])
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(dg));new=bpy.data.objects.new(obj.name+' glyphs',mesh);scene.collection.objects.link(new);new.matrix_world=obj.matrix_world.copy();bpy.data.objects.remove(obj,do_unlink=True)
  return max(v.co.x for v in mesh.vertices)-min(v.co.x for v in mesh.vertices)
 normal=(math.sin(yaw),0,math.cos(yaw))
 front=tuple(pos[i]+normal[i]*.15 for i in range(3));width=glyph(name,front,yaw)
 decor(name+' opaque signboard',(pos[0],pos[1]+size*.38,pos[2]),(width+.5,size*1.35,.2),'steel',yaw=yaw,bevel=.04)
 if both_faces:glyph(name+' reverse',tuple(pos[i]-normal[i]*.15 for i in range(3)),yaw+math.pi)
random.seed(47)
OUT='build/level'
os.makedirs(OUT,exist_ok=True)
# Textured physically based palette, embedded in GLB.
for name,rgb,metal,rough,glow in [
 ('limestone',(.55,.45,.32),0,.88,0),('concrete',(.29,.28,.25),0,.94,0),
 ('asphalt',(.085,.083,.078),0,.96,0),('bronze',(.24,.13,.065),.8,.48,0),
 ('steel',(.13,.17,.18),.8,.5,0),('window',(.055,.105,.12),.68,.25,0),
 ('soot',(.025,.021,.017),0,1,0),('paint',(.55,.48,.3),0,.9,0),
 ('rust',(.22,.08,.025),.45,.93,0),('foliage',(.14,.15,.065),0,.95,0),
 ('emissive_amber',(1,.35,.055),.2,.35,2),('emissive_cyan',(.03,.7,1),.2,.3,3),
 ('emissive_pink',(1,.06,.26),.2,.3,2),('emissive_white',(.75,.9,1),0,.4,2)]:
 mat(name,rgb,metal=metal,roughness=rough,glow=glow)
# Exportable image maps; multi-scale mineral variation and pores, world-scaled UVs.
for name in ['limestone','concrete','asphalt','rust','soot']:
 m=bpy.data.materials[name]; p=m.node_tree.nodes['Principled BSDF']; base=np.array(p.inputs['Base Color'].default_value[:3])
 n=1024; rng=np.random.default_rng(sum(map(ord,name))); fine=rng.random((n,n)); yy,xx=np.mgrid[:n,:n]
 broad=(np.sin(xx*.027+np.sin(yy*.013)*3)+np.cos(yy*.037+xx*.004))*.07
 pat=np.clip(.78+fine*.35+broad,0,1.3)
 if name=='limestone': pat*=np.where((yy%256<5)|(xx%512<5),.62,1)
 if name=='asphalt':
  crack=np.abs(np.sin(xx*.024+np.sin(yy*.011)*2))<.023
  pat*=np.where(crack,.35,1)
 pix=np.ones((n,n,4),dtype=np.float32);pix[:,:,:3]=np.clip(base[None,None,:]*pat[:,:,None],0,1)
 im=bpy.data.images.new(name+'_albedo',width=n,height=n);im.pixels.foreach_set(pix.ravel());im.pack()
 node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
 # Explicit tangent-space normal texture survives GLB (procedural nodes would not).
 dy,dx=np.gradient(fine*.12+broad*.8); norm=np.stack((-dx,-dy,np.ones_like(dx)),axis=-1);norm/=np.linalg.norm(norm,axis=-1)[:,:,None]
 pix[:,:,:3]=norm*.5+.5
 ni=bpy.data.images.new(name+'_normal',width=n,height=n);ni.colorspace_settings.name='Non-Color';ni.pixels.foreach_set(pix.ravel());ni.pack()
 tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=ni;nm=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(tex.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])

def beam(name,a,b,r,material='bronze',vertices=8):
 a=Vector((a[0],-a[2],a[1]));b=Vector((b[0],-b[2],b[1]));d=b-a
 verts=[(r*math.cos(i*math.tau/vertices),r*math.sin(i*math.tau/vertices),z) for z in [-d.length/2,d.length/2] for i in range(vertices)]
 faces=[tuple(reversed(range(vertices))),tuple(range(vertices,vertices*2))]+[(i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices) for i in range(vertices)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);o.location=(a+b)/2;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();me.materials.append(bpy.data.materials[material])

def ring(name,x,y,z,r,material,minor=.09):
 bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=8,location=(x,-z,y),major_radius=r,minor_radius=minor)
 o=bpy.context.object;o.name=name;o.data.materials.append(bpy.data.materials[material])

def tower(name,x,z,w,d,h,material='limestone',step=4):
 with context(name):
  box('mass',(x,h/2,z),(w,h,d),material,bevel=.35)
  for y in np.arange(8,h-2,step):
   decor('floor band '+str(y),(x,float(y),z),(w+.5,.24,d+.5),'concrete')
   for a in np.arange(-w/2+2,w/2-1,4):
    for side in [-1,1]:
     if random.random()<.08: continue
     decor('window '+str(y)+str(a)+str(side),(x+float(a),float(y)+1.3,z+side*(d/2+.055)),(2.7,2.1,.09),'window' if random.random()>.13 else 'soot')
   for a in np.arange(-d/2+2,d/2-1,4):
    for side in [-1,1]:
     decor('end window '+str(y)+str(a)+str(side),(x+side*(w/2+.055),float(y)+1.3,z+float(a)),(.09,2.1,2.7),'window')
  for y in [3,h-1,h+1]: decor('cornice '+str(y),(x,y,z),(w+1.4,.65,d+1.4),material)
  for a in np.arange(-w/2+1,w/2,8):
   for side in [-1,1]: decor('pilaster '+str(a)+str(side),(x+float(a),h/2,z+side*(d/2+.2)),(.35,h,.45),material)
  for i in range(int(w/10)):
   xx=x-w/2+5+i*10;box('roof plant '+str(i),(xx,h+2.1,z),(4,2,4),'steel')

with context('District ground'):
 slab('continuous foundation',(0,0),(440,600),'concrete')
 decor('boulevard',(0,.03,0),(38,.055,580),'asphalt')
 decor('Flamingo Road',(0,.04,-166),(420,.055,26),'asphalt')
 for x in [-21,21]: decor('curb '+str(x),(x,.13,0),(1,.26,580),'limestone')
 for x in [-12,-5,5,12]:
  for z in range(-280,281,12):
   if abs(z+166)>18: decor('lane '+str(x)+' '+str(z),(x,.071,z),(.13,.02,5),'paint')
 for z in [134,-146,-186]:
  for x in range(-17,18,4): decor('crosswalk '+str(x)+' '+str(z),(x,.087,z),(2,.03,5),'paint')
 for x in [-218,218]: box('district edge '+str(x),(x,2,0),(3,4,600),'concrete')
 for z in [-298,298]: box('district edge '+str(z),(0,2,z),(440,4,3),'concrete')

print('Ground complete',flush=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bellagio import build_bellagio
bellagio_meta=build_bellagio(globals())
# Forecourt paving and protected camp geometry.
with context('Sanctuary'):
 for x in range(-62,-23,4):
  for z in range(-22,23,4): decor('paver '+str(x)+' '+str(z),(x,.05,z),(3.9,.08,3.9),'limestone')
 ring('shield footing',-42,.16,0,16,'emissive_cyan',.11)
 for i in range(8):
  a=i*math.pi/4+math.pi/8;x=-42+16*math.cos(a);z=16*math.sin(a)
  box('field projector '+str(i),(x,.7,z),(.6,1.4,.6),'steel',bevel=.1)
  decor('projector light '+str(i),(x,1.5,z),(.25,.2,.25),'emissive_cyan')
 for i in range(3):box('base storage '+str(i),(-52+i*2.4,.6,-8),(2,1.2,1),'steel',bevel=.08)
 text('sanctuary designation','AFTERLIGHT / SAFE HAVEN',(-42,2.4,-11),'emissive_cyan',size=.65,both_faces=True)
 spawn((-42,.25,0),yaw=math.pi/2)
 landmark('sanctuary',(-42,.1,0),tags=['safe-zone','deposit'])
 lamp('sanctuary fill',(-42,6,0),'#62dfff',100,34)

print('Bellagio and sanctuary complete',flush=True)
from paris import build_paris
paris_meta=build_paris(globals())
from caesars import build_caesars
caesars_meta=build_caesars(globals())
tower('Flamingo hotel',145,-237,110,44,64)
text('Flamingo neon','Flamingo',(145,68,-263),'emissive_pink',yaw=math.pi,size=7)
for x in [86,100,114,128,142,156,170,184,198]:
 decor('Flamingo fin '+str(x),(x,35,-261),(1,58,.8),'rust')
tower('Horseshoe north wing',110,-116,36,62,56,'concrete')
text('Horseshoe lettering','HORSESHOE',(89.33,53,-116),'emissive_amber',yaw=-math.pi/2,size=2.3,both_faces=True)
from cosmopolitan import build_cosmopolitan
cosmopolitan_meta=build_cosmopolitan()
tower('Planet Hollywood resort',131,218,72,66,91,'concrete')
text('Planet Hollywood lettering','PLANET HOLLYWOOD',(94.7,84,218),'emissive_amber',yaw=-math.pi/2,size=2.4)
# Open-front, two-sided supply arcades; roofed recesses behind them shelter hordes.
supplies=[('food','KITCHEN / RATIONS',-55,-91,'emissive_amber',36),('medicine','FIELD CLINIC',56,-113,'emissive_cyan',60),('weapons','SECURITY ARMORY',68,92,'emissive_amber',96),('ammo','SERVICE / MUNITIONS',-76,126,'emissive_amber',84)]
mission=[];hides=[]
for kind,label,x,z,accent,pop in supplies:
 with context(kind+' supply arcade'):
  # West/east flank walls, roof, open north/south entries.
  for side in [-1,1]:box('sidewall '+str(side),(x+side*12,2.8,z),(1,5.6,22),'concrete')
  box('canopy',(x,5.9,z),(25, .7,24),'concrete')
  for zz in [-11,11]:
   decor('canopy trim '+str(zz),(x,5.65,z+zz),(24,.18,.2),accent)
   text('supply sign '+str(zz),label,(x,4.45,z+zz),accent,yaw=0 if zz>0 else math.pi,size=.72)
  for i in range(4):
   box('supply locker '+str(i),(x-8+i*5, .7,z+6),(2,1.4,1.1),'steel',bevel=.07)
   decor('locker stripe '+str(i),(x-8+i*5,1,z+5.4),(1.7,.18,.06),accent)
  landmark('cache_'+kind,tuple(bellagio_meta['foodPosition']) if kind=='food' else (x,.15,z),tags=['supply',kind])
  volume('food_arcade' if kind=='food' else 'cache_'+kind,(x,2,z),(18,4,18),roofed=False,tags=['mission','open-arcade'])
  lamp(kind+' fixture',(x,4.8,z),'#ffc078' if kind!='medicine' else '#8cdfff',90,22)
  # Separate covered blind recess across service lane, facing the cache.
  hx=x+(-27 if x<0 else 27);hz=z
  for zz in [-8,8]:box('hide side '+str(zz),(hx,2.3,hz+zz),(12,4.6,.7),'soot')
  box('hide roof',(hx,4.9,hz),(12,.7,17),'concrete')
  back=hx+(-6 if x<0 else 6)
  box('hide back',(back,2.3,hz),(.7,4.6,17),'soot')
  volume('former_food_hide' if kind=='food' else 'hide_'+kind,(hx,2,hz),(9,4,13),roofed=False,tags=['horde-hide','open-front'])
  landmark('hide_'+kind,tuple(bellagio_meta['hordePosition']) if kind=='food' else (hx,.1,hz),tags=['horde-hide'])
  exits=[[hx+(6 if x<0 else -6),.1,hz-5],[hx+(6 if x<0 else -6),.1,hz+5]]
  for i,p in enumerate(bellagio_meta['hordeExits'] if kind=='food' else exits):landmark('emerge_'+kind+'_'+str(i),p,tags=['horde-exit'])
  hides.append(dict(id=kind,position=[hx,0,hz],triggerRadius=24,dormantPopulation=pop,initialScouts=2,exits=exits))
  mission.append(dict(id=kind,title=label,position=[x,.1,z],quantity={'food':12,'medicine':4,'weapons':1,'ammo':72}[kind],collectRadius=3))
mission[0].update(position=bellagio_meta['foodPosition'],title=bellagio_meta['foodTitle'])
hides[0].update(position=bellagio_meta['hordePosition'],exits=bellagio_meta['hordeExits'])
print('Architecture and supply arcades complete',flush=True)
# Sidewalk detail: repeated palms, lamp standards, bollards and architectural neon.
for side in [-1,1]:
 for z in range(-265,281,28):
  if abs(z-166)<22: continue
  x=side*26
  beam('palm trunk',(x,0,z),(x+.8,9,z+.4),.35,'rust',10)
  verts=[];faces=[]
  for j in range(11):
   a=j*math.tau/11;length=random.uniform(4,6);base=len(verts)
   for k in range(17):
    t=k/16;rr=length*t;cy=9+2.2*math.sin(t*math.pi)-2*t*t
    width=.42*math.sin(math.pi*t)**.6
    for side in [-1,1]:verts.append((x+.8+rr*math.cos(a)+side*width*math.sin(a),-(z+.4+rr*math.sin(a)-side*width*math.cos(a)),cy))
   for k in range(16):faces.append((base+k*2,base+k*2+1,base+k*2+3,base+k*2+2))
   for k in range(2,16):
    t=k/16;rr=length*t;cy=9+2.2*math.sin(t*math.pi)-2*t*t;wid=.85*math.sin(math.pi*t)
    for side in [-1,1]:
     b=len(verts);verts.extend([(x+.8+rr*math.cos(a),-(z+.4+rr*math.sin(a)),cy),(x+.8+(rr+.2)*math.cos(a),-(z+.4+(rr+.2)*math.sin(a)),cy-.03),(x+.8+(rr+.6)*math.cos(a)+side*wid*math.sin(a),-(z+.4+(rr+.6)*math.sin(a)-side*wid*math.cos(a)),cy-.45)])
     faces.append((b,b+1,b+2))
  me=bpy.data.meshes.new('palm fronds');me.from_pydata(verts,[],faces);ob=bpy.data.objects.new('palm fronds',me);bpy.context.scene.collection.objects.link(ob);me.materials.append(bpy.data.materials['foliage'])
  beam('street lamp',(side*23,0,z+8),(side*23,7,z+8),.12,'steel')
  beam('lamp arm',(side*23,7,z+8),(side*18,7,z+8),.1,'steel')
  decor('lamp head',(side*18,6.9,z+8),(1,.12,.5),'emissive_amber')
# Rubble stays off authored travel corridors and cache clearances.
for i in range(360):
 x=random.choice([-1,1])*random.uniform(30,206);z=random.uniform(-280,280)
 if any((x-a)**2+(z-b)**2<22**2 for a,b in [(-42,0)]+[(a[2],a[3]) for a in supplies]):continue
 if abs(x+42)<8 or abs(x-40)<8 or abs(z-166)<19:continue
 if -139<x<-67 and -85<z<60:continue
 if x<-118 and -119<z<85:continue
 if 65<x<190 and -145<z<20:continue
 if -215<x<-35 and -297<z<-173:continue
 w=random.uniform(.3,1.8);h=random.uniform(.15,.9)
 decor('rubble fragment '+str(i),(x,h/2,z),(w,h,random.uniform(.3,1.7)),random.choice(['concrete','limestone','rust']),yaw=random.random()*6.28,bevel=.08)
# Asphalt fractures and drifting sand, visible close-up.
for i in range(130):
 x=random.uniform(-18,18);z=random.uniform(-285,285)
 decor('road scar '+str(i),(x,.078,z),(random.uniform(.015,.065),.012,random.uniform(1,8)),'soot',yaw=random.uniform(-1,1))
# Explicit route graph: wide loops, north/south approach of every cache.
route={'home':(-42,0),'west_south':(-42,-63),'food_entry':(-55,-76),'food_exit':(-55,-108),'south_west':(-42,-134),'south_east':(40,-134),'medical_entry':(56,-128),'medical_exit':(56,-98),'east_south':(40,-74),'east_center':(40,0),'east_north':(40,67),'armory_entry':(68,77),'armory_exit':(68,107),'north_east':(40,146),'north_west':(-42,146),'ammo_entry':(-76,141),'ammo_exit':(-76,111),'west_north':(-42,96)}
for name,(x,z) in route.items():volume(name,(x,1.5,z),(3,3,3),roofed=False,tags=['route'])
chain=['home','west_south','food_entry','food_arcade','food_exit','south_west','south_east','medical_entry','cache_medicine','medical_exit','east_south','east_center','east_north','armory_entry','cache_weapons','armory_exit','north_east','north_west','ammo_entry','cache_ammo','ammo_exit','west_north','home']
for a,b in zip(chain,chain[1:]):link(a,b)
# Reserve secondary horde zones, without visible stand-in characters.
for ident,x,z,pop in [('north_garage',92,154,96),('south_casino',89,-185,168)]:
 with context(ident):
  box('back',(x+9,3,z),(1,6,22),'soot');box('roof',(x,6,z),(19,.6,23),'concrete')
  for dz in [-11,11]:box('side '+str(dz),(x,3,z+dz),(19,6,.6),'concrete')
  landmark('hide_'+ident,(x,.1,z),tags=['horde-hide'])
  volume('hide_'+ident,(x,2,z),(16,4,18),roofed=False,tags=['horde-hide','open-front'])
  hides.append(dict(id=ident,position=[x,0,z],triggerRadius=28,dormantPopulation=pop,initialScouts=3,exits=[[x-9,.1,z-6],[x-9,.1,z+6]]))
print('Adding architectural decay',flush=True)
for cx,cz,w,d,h in [(110,-116,36,62,56),(145,-237,110,44,64)]:
 frontx=cx+(w/2+.09 if cx<0 else -w/2-.09)
 for i in range(12):
  zz=cz+random.uniform(-d*.45,d*.45);yy=random.uniform(5,h*.8);sh=random.uniform(5,17);sw=random.uniform(2,5)
  # Charred, irregular strips break up repetitive window grids.
  verts=[(frontx,-(zz-sw),yy-sh/2),(frontx,-(zz+sw),yy-sh*.4),(frontx,-(zz+sw*.5),yy+sh/2),(frontx,-(zz-sw*.2),yy+sh*.3)]
  me=bpy.data.meshes.new('fire scarring');me.from_pydata(verts,[],[(0,1,2,3),(3,2,1,0)]);o=bpy.data.objects.new('fire-damaged facade',me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials['soot'])
 for i in range(45):
  zz=cz+random.uniform(-d/2,d/2);xx=frontx+(1 if cx<0 else -1)*random.uniform(1,8);hh=random.uniform(.2,1.3)
  decor('facade rubble '+str(cx)+' '+str(i),(xx,hh/2,zz),(random.uniform(.4,2),hh,random.uniform(.5,2.2)),'concrete',yaw=random.random()*6.28,bevel=.13)
 for i in range(8):
  zz=cz+random.uniform(-d/2,d/2)
  beam('exposed roof rebar',(frontx,h,zz),(frontx+random.uniform(-1,1),h+random.uniform(1.5,3.5),zz+.7),.035,'rust',5)
# Split the broad sidewalks with long tiled promenade strips and service gutters.
for xx in [-43,41]:
 for zz in range(-278,282,4):
  if abs(zz)<25 and xx<0:continue
  decor('promenade panel '+str(xx)+' '+str(zz),(xx,.07,zz),(8,.08,3.9),'limestone')
# Fast export constructs one combined mesh per material without thousands of operator graph updates.
def fast_export(path):
 from visibility_export import export_visibility
 return export_visibility(path)
scene.export_glb=fast_export
from geometry_quality import orient_closed_solids
orient_closed_solids()
bpy.context.view_layer.update()
# Per-face world UVs preserve real-world texel scale on large buildings.
for o in bpy.data.objects:
 if o.type!='MESH' or o.get('preserve_uv'):continue
 if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
 uv=o.data.uv_layers.active.data
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));ab=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   v=o.matrix_world @ o.data.vertices[o.data.loops[li].vertex_index].co
   uv[li].uv=(v[ab[0]]/6,v[ab[1]]/6)
print('Exporting scene',flush=True)
bpy.ops.file.pack_all()
export(OUT,'vegas')
manifest={'safeZone':{'center':[-42,0,0],'radius':16,'height':18},'supplies':mission,'hides':hides,'routes':route,'dormantPopulation':sum(h['dormantPopulation'] for h in hides),'charactersReady':True,'characterIntegration':{'status':'experimental-prototype','ids':['b610'+str(i) for i in range(1,10)],'player':'b6101','visibleScouts':7,'fullHordesImplemented':False},'bellagio':bellagio_meta,'paris':paris_meta,'caesars':caesars_meta,'cosmopolitan':cosmopolitan_meta}
with open('src/work/vegas-missions.json','w') as f:json.dump(manifest,f,indent=2)
