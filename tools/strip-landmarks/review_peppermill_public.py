"""Source render review; actual installed views are a separate gate."""
import bpy,math
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/peppermill-public-source');out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/peppermillRetail-interior.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16
s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.6,.65,.8,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for x,z,col in [(884,-1972,(.7,.35,1)),(900,-1972,(.8,.5,1)),(883,-1957,(1,.8,.65)),(901,-1957,(1,.7,.9))]:
 bpy.ops.object.light_add(type='AREA',location=(x,-z,3.4));o=bpy.context.object;o.data.energy=180;o.data.color=col;o.data.shape='DISK';o.data.size=5
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=21
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
def pt(q):x,y,z=q;return (x,-z,y)
for name,eye,target in [['lounge',[878,2,-1970],[891,1.5,-1973]],['dining',[881,2,-1961],[899,1.8,-1957]]]:
 cam.location=pt(eye);cam.rotation_euler=(Vector(pt(target))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
