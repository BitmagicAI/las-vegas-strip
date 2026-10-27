"""Offline daylight shape review of the staged GLB source. Not installed-game evidence."""
import bpy,math
from pathlib import Path
from mathutils import Vector
p=Path('build/city-exteriors/towneplace-facade-study');p.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/towneplace-stadium-exterior.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16
s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=30
s.render.resolution_x=1280;s.render.resolution_y=900;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'
for name,eye,target in [('street',(-824,10,1681),(-818,8,1747))]:
 cam.location=(eye[0],-eye[2],eye[1]);t=Vector((target[0],-target[2],target[1]));cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str((p/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
