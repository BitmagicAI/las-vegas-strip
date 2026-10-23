import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
OUT=Path('build/sphere');m=json.loads((OUT/'sphere.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str((OUT/'sphere.blend').resolve()))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=True;scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.03,.05,.08,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.25
for x,y,z,power in [(0,21,-52,4500),(-42,16,-43,1800),(42,16,-43,1800),(0,38,20,3500)]:
 light=bpy.data.lights.new('Architectural fill','AREA');light.energy=power;light.color=(.43,.74,1);light.shape='DISK';light.size=14;o=bpy.data.objects.new(light.name,light);scene.collection.objects.link(o);o.location=(x,-z,y)
cam=bpy.data.cameras.new('Review camera');cam.lens=22;obj=bpy.data.objects.new('Review camera',cam);scene.collection.objects.link(obj);scene.camera=obj
folder=OUT/'proof';folder.mkdir(exist_ok=True)
shots=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['atrium','bowl','exterior']
for shot in shots:
 v=m['views'][shot];p=Vector((v['p'][0],-v['p'][2],v['p'][1]));target=Vector((v['target'][0],-v['target'][2],v['target'][1]));obj.location=p;obj.rotation_euler=(target-p).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str((folder/(shot+'-blender.png')).resolve());bpy.ops.render.render(write_still=True)
