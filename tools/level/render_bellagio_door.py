import bpy,math
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/staged-vegas.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Door review');s.world.use_nodes=True
bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.42,.50,.65,1);bg.inputs['Strength'].default_value=.8
bpy.ops.object.light_add(type='AREA',location=(-135,-34,5));fill=bpy.context.object;fill.data.energy=600;fill.data.shape='DISK';fill.data.size=5
fill.rotation_euler=(Vector((-131,-34,1.5))-fill.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.5,-.6,-.4);sun.data.energy=2
cd=bpy.data.cameras.new('Door');cam=bpy.data.objects.new('Door',cd);s.collection.objects.link(cam)
cam.location=(-135,-34,1.75);target=Vector((-128,-34,2.1));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=25;cd.clip_end=1500;s.camera=cam
s.view_settings.view_transform='AgX';s.render.filepath=str(Path('build/hotels/bellagio-door-repair/door.png').resolve());bpy.ops.render.render(write_still=True)
