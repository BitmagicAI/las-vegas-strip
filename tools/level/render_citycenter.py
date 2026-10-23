import bpy,os,sys,math,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.world=bpy.data.worlds.new('CityCenter daylight review');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.5,.64,.85,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.55,-.5,-.8);bpy.context.object.data.energy=2.5;bpy.context.object.data.angle=.04
shots=[
 ('aria-ceiling',(-295,1.85,440),(-365,11,420),21),
 ('crystals-soffit',(-155,1.85,388),(-181,7,401),21),
 ('citycenter-aerial',(125,240,630),(-221,72,419),34),
 ('aria-place',(7,1.8,516),(-225,55,467),21),
 ('crystals-boulevard',(12,2,389),(-114,24,400),22),
 ('crystals-atrium',(-90,1.85,391),(-127,8,414),21),
 ('crystals-upper',(-105,7.95,450),(-128,11,395),24),
 ('aria-arrival',(-220,1.8,460),(-354,69,412),23),
 ('vdara',(-245,4,300),(-330,72,246),21),
 ('waldorf',(-11,1.8,613),(-83,72,577),20),
]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
review_lights=[]
for rec in json.load(open('build/level/vegas.mesh-level.json'))['lights']:
 if not any('CityCenter / '+h in rec['name'] for h in ['Crystals','Aria']):continue
 p=rec['position'];light_data=bpy.data.lights.new('review '+rec['name'],'POINT');o=bpy.data.objects.new(light_data.name,light_data);s.collection.objects.link(o);o.location=(p[0],-p[2],p[1]);o.data.energy=1800;o.data.color=(1,.82,.61);o.data.shadow_soft_size=2.5;o['review_owner']='Aria' if 'CityCenter / Aria' in rec['name'] else 'Crystals';review_lights.append(o)
for n,p,t,lens in shots:
 if selected and n not in selected:continue
 for o in review_lights:o.hide_render=not ((n.startswith('crystals-') and n not in ['crystals-boulevard'] and o['review_owner']=='Crystals') or (n=='aria-ceiling' and o['review_owner']=='Aria'))
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.location=(p[0],-p[2],p[1]);cam.rotation_euler=(Vector((t[0],-t[2],t[1]))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_end=1800;s.camera=cam;s.render.filepath=os.path.abspath('build/citycenter/'+n+'.png');bpy.ops.render.render(write_still=True)
