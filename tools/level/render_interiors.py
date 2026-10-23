import bpy,os,json,math,sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1120;s.render.resolution_y=760;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Interior review');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.4,.5,.7,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35;s.view_settings.view_transform='AgX'
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.7,-.3,-.5);bpy.context.object.data.energy=2
for l in json.load(open('build/level/vegas.mesh-level.json'))['lights']:
 if l.get('type')!='point':continue
 ld=bpy.data.lights.new(l['name'],'POINT');ob=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(ob);p=l['position'];ob.location=(p[0],-p[2],p[1]);ld.energy=l['intensity']*10;ld.shadow_soft_size=.6;c=l['color'].lstrip('#');ld.color=tuple(int(c[i:i+2],16)/255 for i in [0,2,4])
shots=[('forum-storefront',(-140,2,-281),(-144,3,-285)),('flamingo',(94,2,-237),(158,3,-239)),('horseshoe',(110,2,-89),(110,3,-135)),('planet-hollywood',(95,2,218),(144,3,218)),('miracle-mile',(174,2,252),(174,3,188)),('forum',(-119,2,-262),(-144,3.5,-278)),('curved-escalators',(-94,2,-281),(-110,4,-266)),('paris',(119,2,-41),(132,3,-49)),('cosmopolitan',(-134,2,223),(-126,4,241))]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for n,p,t in shots:
 if selected and n not in selected:continue
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.location=(p[0],-p[2],p[1]);cam.rotation_euler=(Vector((t[0],-t[2],t[1]))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20;cam.data.clip_end=1200;s.camera=cam;s.render.filepath=os.path.abspath('build/interiors/'+n+'.png');bpy.ops.render.render(write_still=True)
