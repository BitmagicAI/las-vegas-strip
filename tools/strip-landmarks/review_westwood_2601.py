"""Local source review; installed captures are separate evidence."""
import bpy,math,os,json
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/westwood-2601-source-review');out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/westwood-2601-exterior.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12
s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
def pt(q):
 x,y,z=q;return (x,-z,y)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=28
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
views=[('front',[166,6,-2900],[119,5,-2946]),('roof',[185,70,-2870],[110,4,-2925]),('annex',[135,6,-2915],[87,5,-2887]),('north-end',[162.302,5,-2978.071],[141.245,5,-2973.11])]
for name,eye,target in views:
 cam.location=pt(eye);cam.rotation_euler=(Vector(pt(target))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22 if name=='lobby' else 28;s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
