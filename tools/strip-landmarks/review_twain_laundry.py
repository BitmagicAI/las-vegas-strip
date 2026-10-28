"""Local source review; installed captures are separate evidence."""
import bpy,math,os
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/twain-laundry-source-review');out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/twain-laundry-exterior.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12
s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
def pt(q):
 x,y,z=q;return (x,-z,y)
for q in [(-1573,3,-1112),(-1574,3,-1122)]:
 bpy.ops.object.light_add(type='AREA',location=pt(q));bpy.context.object.data.energy=100;bpy.context.object.data.size=3
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=28
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
for name,eye,target in [('exterior',(1978,7,-548),(1938,2.7,-545)),('roof',(1980,45,-515),(1937,3,-545))]:
 if os.environ.get('HOME2_REVIEW_SHOTS') and name not in os.environ['HOME2_REVIEW_SHOTS'].split(','):continue
 cam.location=pt(eye);cam.rotation_euler=(Vector(pt(target))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20 if name=='exterior' else 28;s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
