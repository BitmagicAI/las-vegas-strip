"""Neutral daylight review of the actual exported meshes, not a concept image."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
O=Path('build/resort-blocks/bellagio');pt=lambda p:Vector((p[0],-p[2],p[1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
for v in json.loads((O/'venues.json').read_text()):
 for layer in ['exterior','interior']:bpy.ops.import_scene.gltf(filepath=str((O/(v['key']+'-'+layer+'.glb')).resolve()))
for o in bpy.context.scene.objects:
 if str(o.get('source','')).startswith('arrival-tree/') and not str(o.get('source')).endswith('/0'):o.hide_render=True
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6
s.world=bpy.data.worlds.new('Daylight');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.48,.62,.8,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.7
sun=bpy.data.lights.new('sun','SUN');sun.energy=2.5;sun.angle=.09;o=bpy.data.objects.new('sun',sun);s.collection.objects.link(o);o.rotation_euler=(.5,-.5,-.2)
cam=bpy.data.objects.new('camera',bpy.data.cameras.new('camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_end=15000;s.view_settings.view_transform='AgX'
views={'aerial':([0,240,125],[-310,50,365]),'arrival':([-193,2.1,445],[-242,6,445]),'courtyard':([-360,36,488],[-410,0,420]),'patio':([-173,2,352],[-195,3,354]),'lobby':([-231,2,445],[-279,5,445])}
views.update({'lakefront':([-3,47,283],[-102,8,222]),'lake-shore':([-18,2,274],[-101,12,222])})
views.update({'south-arrival':([35,112,674],[-135,8,510]),'south-underpass':([-116,2,517],[-151,4,533])})
views.update({'garage':([-285,28,610],[-285,3,527]),'sign':([-72,12,609],[-46,14,586]),'trees':([-106,8,597],[-117,4,585])})
if '--all' not in sys.argv:views={k:views[k] for k in ['garage','sign','trees']}
if '--trees' in sys.argv:views={k:v for k,v in views.items() if k=='trees'}
for name,(eye,target) in views.items():
 if name=='trees':
  for obj in bpy.context.scene.objects:
   if obj.type=='MESH' and not str(obj.get('source','')).startswith('arrival-tree/'):obj.hide_render=True
 cam.location=pt(eye);cam.rotation_euler=(pt(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=25;s.render.filepath=str((O/(name+'-review.png')).resolve());bpy.ops.render.render(write_still=True)
(O/'render-cameras.json').write_text(json.dumps(dict(lighting='Neutral daylight',lensMm=25,views=views),indent=2))
