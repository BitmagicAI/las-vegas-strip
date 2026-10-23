import bpy,json,math,os,sys
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/staged-vegas.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.world=bpy.data.worlds.new('Public architecture review');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.45,.52,.63,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
shots=[
 ('bellagio',(-158,2,-60),(-178,3.2,-62)),
 ('paris',(92,2,-37),(81,3.4,-25)),
 ('caesars',(-98,2,-242),(-118,4.0,-235)),
 ('cosmopolitan',(-44,2,243),(-43,3,264)),
 ('chandelier',(-48,2,231),(-59,4.4,218)),
 ('flamingo',(150,2,-240),(157,3.4,-251)),
 ('horseshoe',(110,2,-91),(110,4,-124)),
 ('planet-hollywood',(87,2,218),(81,4,232)),
 ('aria',(-259,2,451),(-266,4.5,429)),
 ('vdara',(-306,2,246),(-327,3.3,219)),
 ('waldorf',(-55,2,575),(-93,4,571)),
 ('veer',(-119,2,449),(-127,2.5,453)),
 ('crystals',(-100,2,402),(-127,7,414)),
 ('paris-entry',(51,2,-55),(71,5.7,-39)),
 ('flamingo-entry',(71,2,-246),(91,6,-237)),
 ('horseshoe-entry',(99,2,-166),(110,6,-147)),
 ('cosmo-entry',(-9,2,256),(-29,6,242)),
 ('planet-hollywood-entry',(48,2,232),(65,5.2,218)),
 ('aria-entry',(-211,2,462),(-243,5.2,448)),
 ('waldorf-entry',(-22,2,586),(-40,3.4,576)),
 ('vdara-entry',(-280,2,300),(-301,6,277)),
]
out=Path('build/public-resorts/renders');out.mkdir(exist_ok=True)
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
objects=[]
for ob in s.objects:
 if ob.type!='MESH':continue
 ps=[ob.matrix_world@Vector(v) for v in ob.bound_box];lo=Vector(tuple(min(p[i] for p in ps) for i in range(3)));hi=Vector(tuple(max(p[i] for p in ps) for i in range(3)));objects.append((ob,lo,hi))
lights=[]
for rec in json.loads(Path('build/hotels/staged-vegas.mesh-level.json').read_text())['lights']:
 if rec.get('type')!='point':continue
 ld=bpy.data.lights.new(rec['name'],'POINT');o=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(o);p=rec['position'];o.location=(p[0],-p[2],p[1]);ld.energy=rec['intensity']*14;ld.shadow_soft_size=1.0;c=rec['color'].lstrip('#');ld.color=tuple(int(c[i:i+2],16)/255 for i in [0,2,4]);lights.append(o)
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.6,-.5,-.8);sun.data.energy=2.5
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=21;cam.data.clip_end=900
for name,p,target in shots:
 if selected and name not in selected:continue
 cam.location=(p[0],-p[2],p[1]);aim=Vector((target[0],-target[2],target[1]));cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
 for ob,lo,hi in objects:
  # Keep complete nearby architectural batches and omit remote resorts.
  ob.hide_render=lo.x>p[0]+115 or hi.x<p[0]-115 or lo.y>-p[2]+115 or hi.y<-p[2]-115 or lo.z>40
 for ob in lights:ob.hide_render=(ob.location-cam.location).length>90
 s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True);print('REVIEW',name,flush=True)
