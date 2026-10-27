"""Local source review of inferred public-room furniture, not installed evidence."""
import bpy
from pathlib import Path
from mathutils import Vector
p=Path('build/city-exteriors/towneplace-public-study');p.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/towneplace-stadium-interior.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16
s.world=bpy.data.worlds.new('Room ambient');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
for x in [-826,-816]:
 bpy.ops.object.light_add(type='AREA',location=(x,-1749,3.1));bpy.context.object.data.energy=250;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=5
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=22
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
for name,eye,target in [('lounge',(-823,1.95,1752),(-830,1.5,1752)),('workstation',(-816,1.95,1745),(-820,1.5,1745))]:
 cam.location=(eye[0],-eye[2],eye[1]);t=Vector((target[0],-target[2],target[1]));cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str((p/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
