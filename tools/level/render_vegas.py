import bpy, math, json, os
from mathutils import Vector
root=os.path.abspath('build/level')
bpy.ops.wm.open_mainfile(filepath=root+'/vegas.blend')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Mojave dusk');s.world.use_nodes=True
nodes=s.world.node_tree.nodes;bg=nodes.get('Background');bg.inputs['Color'].default_value=(.22,.29,.4,1);bg.inputs['Strength'].default_value=.45
env=nodes.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(root+'/skybox.webp');s.world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color'])
bpy.ops.object.light_add(type='SUN',location=(-180,80,160));sun=bpy.context.object;sun.rotation_euler=(math.radians(68),math.radians(-20),math.radians(-70));sun.data.energy=2.5;sun.data.color=(1,.69,.42);sun.data.angle=.08
for l in json.load(open(root+'/vegas.mesh-level.json'))['lights']:
 p=l['position'];bpy.ops.object.light_add(type='POINT',location=(p[0],-p[2],p[1]));o=bpy.context.object;o.data.energy=l['intensity']*12;c=l['color'].lstrip('#');o.data.color=tuple(int(c[i:i+2],16)/255 for i in (0,2,4));o.data.shadow_soft_size=2
# Thin upper energy shell for the same sanctuary visible in-game.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=16,location=(-42,0,.1))
dome=bpy.context.object;dome.name='Sanctuary preview energy';m=bpy.data.materials.new('Energy preview');m.use_nodes=True
n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');tr=n.new('ShaderNodeBsdfTransparent');em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(.08,.65,1,1);em.inputs[1].default_value=.65;mix.inputs[0].default_value=.025;m.node_tree.links.new(tr.outputs[0],mix.inputs[1]);m.node_tree.links.new(em.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],out.inputs[0]);dome.data.materials.append(m)
s.view_settings.view_transform='AgX'
os.makedirs(root+'/renders',exist_ok=True)
shots=[('sanctuary',(-57,3,-15),(80,30,-39),25),('strip',(-9,2.3,-134),(52,28,-28),28),('district',(-245,190,-305),(0,15,15),37)]
for name,p,t,lens in shots:
 bpy.ops.object.camera_add(location=(p[0],-p[2],p[1]));cam=bpy.context.object;target=Vector((t[0],-t[2],t[1]));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_end=1500;s.camera=cam
 s.render.filepath=root+'/renders/'+name+'.png';bpy.ops.render.render(write_still=True)
 print('RENDERED '+name,flush=True)

# Preserve the presentation lighting and all three editable cameras.
bpy.ops.wm.save_as_mainfile(filepath=root+'/vegas-presentation.blend')
