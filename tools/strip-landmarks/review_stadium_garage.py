"""Local source review; installed captures are separate evidence."""
import bpy,math,os
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/stadium-garage-source-review');out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/stadium-garage-exterior.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12
s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
a=-math.atan2(30.624,25.216);c,t=math.cos(a),math.sin(a)
def pt(q):
 x,y,z=q;return (-824.745+c*x+t*z,-(1779.52-t*x+c*z),y)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=28
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
for name,eye,target in [('arrival',(95,5,-3),(70,5,-18)),('decks',(98,6,-37),(60,5,-28)),('roof',(56,35,-7),(50,3,-25)),('entry',(80,1.9,-25),(57,1.5,-25)),('south-stairs',(70,5,-19),(74,4,-13)),('north-stairs',(20,16,-28),(24,10,-20))]:
 if os.environ.get('HOME2_REVIEW_SHOTS') and name not in os.environ['HOME2_REVIEW_SHOTS'].split(','):continue
 cam.location=pt(eye);cam.rotation_euler=(Vector(pt(target))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22 if name in ['lobby','breakfast'] else 28;s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
