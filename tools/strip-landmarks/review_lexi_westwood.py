"""Local source review; installed captures are separate evidence."""
import bpy,math,os,json
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/lexi-westwood-source-review');out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/lexi-westwood-interior.blend').resolve()))
with bpy.data.libraries.load(str(Path('build/strip-landmarks/lexi-westwood-exterior.blend').resolve()),link=False) as (src,dst):dst.objects=src.objects
for ob in dst.objects:
 if ob is not None:bpy.context.collection.objects.link(ob)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12
s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
def pt(q):
 x,y,z=q;return (x,-z,y)
for q in [(292,5.1,-3064),(292,5.1,-3071)]:
 bpy.ops.object.light_add(type='AREA',location=pt(q));bpy.context.object.data.energy=260;bpy.context.object.data.size=3
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=28
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
views=[('front',[324,5,-3057],[284,8,-3083]),('pool',[234,4,-3056],[259,8,-3086]),('roof',[231,42,-3028],[283,5,-3084]),('lobby',[292,1.8,-3065],[292,2,-3070])]
for name,eye,target in views:
 cam.location=pt(eye);cam.rotation_euler=(Vector(pt(target))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22 if name=='lobby' else 28;s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
