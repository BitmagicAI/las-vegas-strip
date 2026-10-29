import bpy,math,json
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/double-down-study');out.mkdir(parents=True,exist_ok=True)
m=json.loads(Path('build/strip-landmarks/doubleDown-metadata.json').read_text())
def xyz(p):return(p[0],-p[2],p[1])
for name,view in m['views'].items():
 bpy.ops.wm.open_mainfile(filepath=str(Path('build/strip-landmarks/doubleDown-'+('interior' if name=='bar' else 'exterior')+'.blend').resolve()))
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.6,.65,.7,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
 bpy.ops.object.camera_add(location=xyz(view['eye']));cam=bpy.context.object;cam.rotation_euler=(Vector(xyz(view['target']))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=30;s.camera=cam
 if name=='bar':
  for light in m['lights']:
   bpy.ops.object.light_add(type='POINT',location=xyz(light['p']));o=bpy.context.object;o.data.energy=100;o.data.shadow_soft_size=.4
 else:
  bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.6,-.4,-.5);bpy.context.object.data.energy=3
 s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
