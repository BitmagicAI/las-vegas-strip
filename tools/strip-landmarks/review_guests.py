"""Render the locally exported guest modules, including their actual lighting."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path('build/strip-landmarks')
def pt(p):return Vector((p[0],-p[2],p[1]))
for key in (sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['linq','vanderpump','polo']):
 for kind in ['room','corridor']:
  name=key+'-'+kind
  bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/'+name+'.blend').resolve()))
  s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
  s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
  s.world=bpy.data.worlds.new('Daylight');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
  for l in json.loads(Path('build/hotels/'+name+'.mesh-level.json').read_text())['lights']:
   d=bpy.data.lights.new(l['name'],'POINT');d.energy=l['intensity']*16;d.shadow_soft_size=.3;o=bpy.data.objects.new(l['name'],d);s.collection.objects.link(o);o.location=pt(l['position'])
  cam=bpy.data.objects.new('camera',bpy.data.cameras.new('camera'));s.collection.objects.link(cam);s.camera=cam
  eye,target=((2.7,1.65,2.2),(4.8,1.3,-1.5)) if kind=='room' else ((.3,1.65,2.8),(0,1.5,-2.8))
  cam.location=pt(eye);cam.rotation_euler=(pt(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20 if kind=='room' else 22;s.view_settings.view_transform='AgX'
  s.render.filepath=str((OUT/(name+'-review.png')).resolve());bpy.ops.render.render(write_still=True)
