import bpy, math, json, os, sys
from mathutils import Vector
root=os.path.abspath('build/level');out=os.path.abspath('build/caesars')
bpy.ops.wm.open_mainfile(filepath=root+'/vegas.blend')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.render.resolution_x=1440;s.render.resolution_y=960;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Bellagio review');s.world.use_nodes=True
nodes=s.world.node_tree.nodes;bg=nodes.get('Background');bg.inputs['Color'].default_value=(.35,.43,.55,1);bg.inputs['Strength'].default_value=.85
env=nodes.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(root+'/skybox.webp');s.world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color'])
bpy.ops.object.light_add(type='SUN',location=(-180,80,160));sun=bpy.context.object;sun.rotation_euler=(math.radians(48),math.radians(-20),math.radians(-65));sun.data.energy=2.5;sun.data.color=(1,.83,.65);sun.data.angle=.06
for l in json.load(open(root+'/vegas.mesh-level.json'))['lights']:
 p=l['position'];ld=bpy.data.lights.new('Review '+l.get('name','light'),'POINT');o=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(o);o.location=(p[0],-p[2],p[1]);o.data.energy=l['intensity']*12;c=l['color'].lstrip('#');o.data.color=tuple(int(c[i:i+2],16)/255 for i in (0,2,4));o.data.shadow_soft_size=1
s.view_settings.view_transform='AgX'
shots=[('caesars-overview',(25,115,-115),(-143,42,-237),32),('caesars-street',(-20,3,-226),(-144,37,-236),24),('caesars-casino',(-98,1.8,-242),(-145,3,-240),22),('caesars-service',(-158,1.8,-250),(-171,2,-250),22)]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for name,p,t,lens in shots:
 cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);s.collection.objects.link(cam);cam.location=(p[0],-p[2],p[1]);target=Vector((t[0],-t[2],t[1]));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_end=1500;s.camera=cam
 if not selected or name in selected:
  s.render.filepath=out+'/'+name+'.png';bpy.ops.render.render(write_still=True);print('RENDERED '+name,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=out+'/caesars-review.blend')
