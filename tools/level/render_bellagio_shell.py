"""Street review of the repaired streamed exterior, using its real materials."""
import bpy,math
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/staged-vegas.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1440;s.render.resolution_y=960;s.render.resolution_percentage=100
# Only this resort is in the shot; omit the distant city from the review render.
for ob in bpy.data.objects:
    if ob.type=='MESH' and not ob.name.startswith('Bellagio '):ob.hide_render=True
s.world=bpy.data.worlds.new('Facade review');s.world.use_nodes=True
bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.32,.44,.62,1);bg.inputs['Strength'].default_value=.7
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.7,-.35,-.8);sun.data.energy=2.5;sun.data.color=(1,.88,.72);sun.data.angle=.06
cd=bpy.data.cameras.new('Facade');cam=bpy.data.objects.new('Facade',cd);s.collection.objects.link(cam)
cam.location=(-42,18,1.8);target=Vector((-159,18,45));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=25;cd.clip_end=500;s.camera=cam
s.view_settings.view_transform='AgX';s.render.filepath=str(Path('build/hotels/bellagio-shell-repair/exterior.png').resolve());bpy.ops.render.render(write_still=True)
