import bpy, math, json, os, sys
from mathutils import Vector
root=os.path.abspath('build/level');out=os.path.abspath('build/bellagio-v2')
bpy.ops.wm.open_mainfile(filepath=root+'/vegas.blend')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1440;s.render.resolution_y=960;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Bellagio review');s.world.use_nodes=True
nodes=s.world.node_tree.nodes;bg=nodes.get('Background');bg.inputs['Color'].default_value=(.35,.43,.55,1);bg.inputs['Strength'].default_value=.55
env=nodes.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(root+'/skybox.webp');s.world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color'])
bpy.ops.object.light_add(type='SUN',location=(-180,80,160));sun=bpy.context.object;sun.rotation_euler=(math.radians(48),math.radians(-20),math.radians(65));sun.data.energy=2.5;sun.data.color=(1,.83,.65);sun.data.angle=.06
for l in json.load(open(root+'/vegas.mesh-level.json'))['lights']:
 p=l['position'];ld=bpy.data.lights.new('Review '+l.get('name','light'),'POINT');o=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(o);o.location=(p[0],-p[2],p[1]);o.data.energy=l['intensity']*12;c=l['color'].lstrip('#');o.data.color=tuple(int(c[i:i+2],16)/255 for i in (0,2,4));o.data.shadow_soft_size=1
s.view_settings.view_transform='AgX'
shots=[('bellagio-exterior',(-8,25,-32),(-160,43,-18),23),('bellagio-lobby',(-154,1.8,-71),(-168,4,-51),22),('bellagio-casino',(-158,1.8,-39),(-161,3,15),24),('bellagio-service',(-197,1.8,-59),(-197,2,18),24)]
shots += [('bellagio-'+name,(-204.5,1.75,z),(-213,1.6,z),23) for name,z in [('lounge',-58),('stores',-36),('medical',-14),('security',8)]]
shots += [('bellagio-facade-close',(-124,1.8,-78),(-155,32,-30),24)]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for name,p,t,lens in shots:
 cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);s.collection.objects.link(cam);cam.location=(p[0],-p[2],p[1]);target=Vector((t[0],-t[2],t[1]));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_end=1500;s.camera=cam
 if not selected or name in selected:
  s.render.filepath=out+'/'+name+'.png';bpy.ops.render.render(write_still=True);print('RENDERED '+name,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=out+'/bellagio-review.blend')
