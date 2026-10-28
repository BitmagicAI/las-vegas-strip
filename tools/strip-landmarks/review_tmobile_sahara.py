import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/tmobile-sahara-source-review');out.mkdir(parents=True,exist_ok=True)
def pt(q):
 x,y,z=q;return (x,-z,y)
for part in ['exterior']:
 bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/tmobile-sahara-'+part+'.blend').resolve()))
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.75,.85,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
 bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
 if part=='interior':
  for x in [-1688,-1683,-1678]:
   bpy.ops.object.light_add(type='AREA',location=pt((x,2.95,-3194.5)));bpy.context.object.data.energy=130;bpy.context.object.data.size=3
 bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=24
 s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
 views=[('exterior',[-1719,4,-3168],[-1719,3,-3191]),('roof',[-1745,26,-3172],[-1718,3,-3205])] if part=='exterior' else [(k,v['eye'],v['target']) for k,v in json.load(open('build/strip-landmarks/tmobile-sahara-metadata.json'))['views'].items() if k in ['booths','counter']]
 for name,eye,target in views:
  cam.location=pt(eye);cam.rotation_euler=(Vector(pt(target))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
