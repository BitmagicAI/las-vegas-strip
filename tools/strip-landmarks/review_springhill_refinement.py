"""Local source review; installed captures are separate evidence."""
import bpy,math,os,json
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/springhill-refinement-source');out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/springhillExterior-exterior.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12
s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
def pt(q):
 x,y,z=q;return (x,-z,y)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=28
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
views=[["front", [1630, 7, -2110], [1598, 8, -2134]], ["arrival", [1616, 3.2, -2134.2], [1598.65, 2.8, -2134.2]], ["roof", [1524, 88, -2117], [1550, 74, -2135]], ["deck", [1540.2, 75.7, -2127.8], [1548, 74.7, -2135]]]
for name,eye,target in views:
 cam.location=pt(eye);cam.rotation_euler=(Vector(pt(target))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22 if name=='lobby' else 28;s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
