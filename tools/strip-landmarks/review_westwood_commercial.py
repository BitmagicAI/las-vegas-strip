"""Local source review; installed captures are separate evidence."""
import bpy,math,os,json
from pathlib import Path
from mathutils import Vector
out=Path('build/city-exteriors/westwood-commercial-source-review');out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
for name in ['westwood-2650-exterior','highland-steel-exterior','highland-steel-interior','creel-highland-exterior']:
 bpy.ops.import_scene.gltf(filepath=str(Path('build/strip-landmarks',name+'.glb').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12
s.world=bpy.data.worlds.new('Review sky');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.75,.9,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.45,-.4,-.7)
def pt(q):
 x,y,z=q;return (x,-z,y)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=28
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
views=[]
for key in ['westwood-2650','highland-steel','creel-highland']:
 meta=json.loads(Path('build/strip-landmarks',key+'-metadata.json').read_text())
 views.extend([(key+'-'+n,e,t) for n,e,t in meta['reviewViews']])
 if key=='highland-steel':
  door=meta['portals'][0];x,y,z=door['p'];yaw=door['yaw']
  def local(xx,yy,zz):return [x+math.cos(yaw)*xx+math.sin(yaw)*zz,yy,z-math.sin(yaw)*xx+math.cos(yaw)*zz]
  views.append(('highland-display',local(.2,1.75,1.2),local(3.3,1.6,6.5)))
  for light in meta['lights']:
   bpy.ops.object.light_add(type='AREA',location=pt(light['p']));lamp=bpy.context.object;lamp.data.energy=100;lamp.data.shape='RECTANGLE';lamp.data.size=2;lamp.data.size_y=.25
for name,eye,target in views:
 cam.location=pt(eye);cam.rotation_euler=(Vector(pt(target))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=22 if name=='lobby' else 28;s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
