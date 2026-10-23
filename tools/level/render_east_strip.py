import bpy,os,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('East Strip review');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.5,.6,.8,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.4,-.5,-.8);bpy.context.object.data.energy=2.5
bpy.ops.object.camera_add();cam=bpy.context.object;cam.location=(0,0,600);cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=850;cam.data.clip_end=1500;s.camera=cam
mat=bpy.data.materials.new('Map labels');mat.diffuse_color=(1,.8,.2,1)
for label,x,z in [('NORTH ↑',0,-310),('FLAMINGO',145,-237),('HORSESHOE',110,-116),('PARIS',173,-75),('PLANET HOLLYWOOD',131,218),('CAESARS',-140,-230),('BELLAGIO',-155,0),('COSMOPOLITAN',-125,230)]:
 curve=bpy.data.curves.new(label,'FONT');curve.body=label;curve.size=7;curve.align_x='CENTER';ob=bpy.data.objects.new(label,curve);s.collection.objects.link(ob);ob.location=(x,-z,200);curve.materials.append(mat)
s.render.filepath=os.path.abspath('build/east-strip/plan.png');bpy.ops.render.render(write_still=True)
