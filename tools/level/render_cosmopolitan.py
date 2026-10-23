import bpy,math,os,sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Cosmopolitan review');s.world.use_nodes=True;bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.42,.52,.7,1);bg.inputs['Strength'].default_value=.65
env=s.world.node_tree.nodes.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(os.path.abspath('build/level/skybox.webp'));s.world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color'])
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(math.radians(40),math.radians(-25),math.radians(135));sun.data.energy=2.4;sun.data.angle=.04
s.view_settings.view_transform='AgX'
shots=[('overview',(70,140,20),(-116,84,224),26),('street',(10,2,215),(-85,53,219),19),('casino',(-36,1.8,242),(-98,3,235),23)]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
import json
for l in json.load(open('build/level/vegas.mesh-level.json'))['lights']:
 if not l['name'].startswith('Cosmopolitan'):continue
 p=l['position'];ld=bpy.data.lights.new(l['name'],'POINT');ob=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(ob);ob.location=(p[0],-p[2],p[1]);ld.energy=l['intensity']*15;ld.shadow_soft_size=1;c=l['color'].lstrip('#');ld.color=tuple(int(c[i:i+2],16)/255 for i in (0,2,4))
for name,p,t,lens in shots:
 if selected and name not in selected:continue
 cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);s.collection.objects.link(cam);cam.location=(p[0],-p[2],p[1]);target=Vector((t[0],-t[2],t[1]));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;cd.clip_end=1500;s.camera=cam;s.render.filepath=os.path.abspath('build/cosmopolitan/'+name+'.png');bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
