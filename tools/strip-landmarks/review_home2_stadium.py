"""Local source review; installed captures are separate evidence."""
import bpy,math,os
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/home2-source-review');out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/home2-stadium-exterior.blend').resolve()))
with bpy.data.libraries.load(str(Path('build/strip-landmarks/home2-stadium-interior.blend').resolve()),link=False) as (src,dst):dst.objects=src.objects
for ob in dst.objects:
 if ob:bpy.context.collection.objects.link(ob)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12
s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
a=-math.atan2(30.624,25.216);c,t=math.cos(a),math.sin(a)
def pt(q):
 x,y,z=q;return (-824.745+c*x+t*z,-(1779.52-t*x+c*z),y)
for q in [(51,3.05,10),(59,3.05,9),(54,3.05,16)]:
 bpy.ops.object.light_add(type='AREA',location=pt(q));bpy.context.object.data.energy=160;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=4
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=28
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
for name,eye,target in [('patio',(80,6,10),(72,1.5,1)),('grills',(73,1.95,4.5),(73,1.35,-1)),('pool',(12,13,-25),(11,.5,-7)),('pool-deck',(19,1.95,-3),(9,1,-9)),('street',(30,13,68),(32,8,12)),('entrance',(98,7,24),(60,6,10)),('pool-side',(12,9,-40),(28,7,7)),('lobby',(64,1.95,8),(50,1.3,12)),('breakfast',(52,1.95,10),(56,1.2,17))]:
 if os.environ.get('HOME2_REVIEW_SHOTS') and name not in os.environ['HOME2_REVIEW_SHOTS'].split(','):continue
 cam.location=pt(eye);cam.rotation_euler=(Vector(pt(target))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22 if name in ['lobby','breakfast'] else 28;s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
