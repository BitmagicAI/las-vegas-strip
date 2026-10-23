import bpy,json,math
from pathlib import Path
from mathutils import Vector
OUT=Path('build/south-strip')
bpy.ops.wm.open_mainfile(filepath=str(Path('build/highrises/exteriors.blend').resolve()))
for o in bpy.data.objects:o.hide_render=o.get('property') not in ['new-york','excalibur']
bpy.ops.import_scene.gltf(filepath=str((OUT/'coaster.glb').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Daylight');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.50,.65,.82,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.65
sun=bpy.data.lights.new('sun','SUN');sun.energy=2.5;sun.angle=.08;o=bpy.data.objects.new('sun',sun);s.collection.objects.link(o);o.rotation_euler=(.5,-.5,-.2)
cam=bpy.data.objects.new('camera',bpy.data.cameras.new('camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_end=15000;s.view_settings.view_transform='AgX'
bpy.ops.mesh.primitive_plane_add(size=2400,location=(-150,-1700,-.02));floor=bpy.context.object;m=bpy.data.materials.new('ground');m.diffuse_color=(.22,.20,.16,1);floor.data.materials.append(m)
def pt(v):return Vector((v[0],-v[2],v[1]))
for name,eye,aim,lens in [('new-york',(160,112,1835),(-130,65,1535),32),('excalibur',(120,125,1540),(-220,30,1850),42),('station',(-51,32,1430),(-100,14,1480),30),('liberty',(-3,27,1669),(-49,27,1636),38)]:
 cam.location=pt(eye);cam.rotation_euler=(pt(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;s.render.filepath=str((OUT/(name+'-review.png')).resolve());bpy.ops.render.render(write_still=True)
