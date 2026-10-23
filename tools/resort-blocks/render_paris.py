"""Neutral-light exported-geometry review, including the retained Eiffel landmark."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
O=Path('build/resort-blocks/paris');pt=lambda p:Vector((p[0],-p[2],p[1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
for v in json.loads((O/'venues.json').read_text()):
 for layer in ['exterior','interior']:bpy.ops.import_scene.gltf(filepath=str((O/(v['key']+'-'+layer+'.glb')).resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6
s.world=bpy.data.worlds.new('Daylight');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.48,.62,.8,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.7
sun=bpy.data.lights.new('sun','SUN');sun.energy=2.5;sun.angle=.09;o=bpy.data.objects.new('sun',sun);s.collection.objects.link(o);o.rotation_euler=(.5,-.5,-.2)
cam=bpy.data.objects.new('camera',bpy.data.cameras.new('camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_end=15000;s.view_settings.view_transform='AgX'
views={'aerial':([-115,155,505],[152,43,400]),'frontage':([4,6,363],[55,8,352]),'patio':([29,9,470],[58,8,435]),'pool':([116,14,430],[135,12,383]),'arrival':([126.8,3,458],[126.8,9,435]),'arrival-aerial':([4,130,607],[113,13,462]),'facades':([130,14,465],[128,14,435]),'facades-aerial':([87,49,497],[137,12,448])}
views.update({'tower-pool':([-112,115,530],[110,75,400]),'pool-aerial':([82,59,439],[137,10.74,386]),'tower-base':([-42,60,479],[74.5,38,400.5])})
if '--' in sys.argv:views={k:views[k] for k in sys.argv[sys.argv.index('--')+1:]}
for name,(eye,target) in views.items():
 cam.location=pt(eye);cam.rotation_euler=(pt(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=36 if name=='tower-base' else 28;s.render.filepath=str((O/(name+'-review.png')).resolve());bpy.ops.render.render(write_still=True)
