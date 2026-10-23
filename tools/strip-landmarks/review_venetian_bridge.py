import bpy,json,math
from pathlib import Path
from mathutils import Vector
OUT=Path('build/strip-landmarks');meta=next(v for v in json.load(open(OUT/'venues.json')) if v['key']=='venetian')
def pt(p):return Vector((p[0],-p[2],p[1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
for p in ['build/geographic-strip/city.glb','build/strip-landmarks/venetian-exterior.glb','build/strip-landmarks/venetian-interior.glb']:
 bpy.ops.import_scene.gltf(filepath=str(Path(p).resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=950;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6
s.world=bpy.data.worlds.new('Daylight');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.50,.65,.82,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.55
sun=bpy.data.lights.new('sun','SUN');sun.energy=2.8;sun.angle=.08;o=bpy.data.objects.new('sun',sun);s.collection.objects.link(o);o.rotation_euler=(.5,-.5,-.2)
cam=bpy.data.objects.new('camera',bpy.data.cameras.new('camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_end=15000;s.view_settings.view_transform='AgX'
for name in ['rialto-overview','rialto-underpass','palace-plaza']:
 v=meta['views'][name];cam.location=pt(v['eye']);cam.rotation_euler=(pt(v['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=30;s.render.filepath=str((OUT/('venetian-'+name+'-combined.png')).resolve());bpy.ops.render.render(write_still=True)
