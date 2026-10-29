"""Source-only views, not installed verification."""
import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/flex-twain-source-review');out.mkdir(parents=True,exist_ok=True)
def pt(q):
 x,y,z=q;return (x,-z,y)
meta=json.loads(Path('build/strip-landmarks/flex-twain-metadata.json').read_text())
for part in ['exterior','interior']:
 bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/flex-twain-'+part+'.blend').resolve()))
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12
 s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 if part=='exterior':
  bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
 else:
  for z in [-552,-546,-541]:
   bpy.ops.object.light_add(type='AREA',location=pt((1889,3,z)));bpy.context.object.data.energy=110;bpy.context.object.data.size=4
 bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=22
 s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
 views={'front':{'eye':[1903,6,-571],'target':[1889,2.5,-552]},'roof':{'eye':[1907,25,-571],'target':[1889,2,-545]}} if part=='exterior' else meta['views']
 for name,v in views.items():
  cam.location=pt(v['eye']);cam.rotation_euler=(Vector(pt(v['target']))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
