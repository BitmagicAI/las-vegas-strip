"""Local source review; installed captures are separate evidence."""
import bpy,math,os
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/motel6-source-review');out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/motel6-stadium-exterior.blend').resolve()))
with bpy.data.libraries.load(str(Path('build/strip-landmarks/motel6-stadium-interior.blend').resolve()),link=False) as (src,dst):dst.objects=src.objects
for ob in dst.objects:
 if ob:bpy.context.collection.objects.link(ob)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12
s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
def pt(q):
 x,y,z=q;return (x,-z,y)
for q in [(-786,2.8,2003),(-793,2.8,2004)]:
 bpy.ops.object.light_add(type='AREA',location=pt(q));bpy.context.object.data.energy=100;bpy.context.object.data.size=3
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=28
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
for name,eye,target in [('pool',(-813,5,2003),(-804,1,2016)),('arrival',(-766,5,1989),(-785,3,2005)),('roof',(-761,65,1960),(-813,2,2028)),('gallery',(-770,5,2040),(-781,3,2028)),('lobby',(-783,1.9,2003),(-789,1.3,2007)),('laundry',(-791,1.9,2002),(-796,1,2007))]:
 if os.environ.get('HOME2_REVIEW_SHOTS') and name not in os.environ['HOME2_REVIEW_SHOTS'].split(','):continue
 cam.location=pt(eye);cam.rotation_euler=(Vector(pt(target))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22 if name in ['lobby','breakfast'] else 28;s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
