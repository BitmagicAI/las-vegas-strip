import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path('build/resort-blocks/cosmo');pt=lambda p:Vector((p[0],-p[2],p[1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
for name in ['cosmo-exterior','cosmoL1-interior','cosmoL2-interior','cosmoL3-interior','cosmoL4-interior','cosmoL14-interior']:bpy.ops.import_scene.gltf(filepath=str((O/(name+'.glb')).resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6
s.world=bpy.data.worlds.new('Daylight');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.48,.62,.8,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.6
sun=bpy.data.lights.new('sun','SUN');sun.energy=2.5;sun.angle=.09;o=bpy.data.objects.new('sun',sun);s.collection.objects.link(o);o.rotation_euler=(.5,-.5,-.2)
cam=bpy.data.objects.new('camera',bpy.data.cameras.new('camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_end=15000;s.view_settings.view_transform='AgX'
views={'aerial':([60,200,490],[-200,65,682]),'boulevard-pool':([-46,19,688],[-55,18,647]),'chelsea-pool':([-305,25,720],[-345,23,710]),'motorcourt':([-392,2,713],[-345,3,713]),'gallery':([-136,7.54,705],[-58,8.5,700])}
for name,(eye,target) in views.items():
 cam.location=pt(eye);cam.rotation_euler=(pt(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=25;s.render.filepath=str((O/(name+'-review.png')).resolve());bpy.ops.render.render(write_still=True)
