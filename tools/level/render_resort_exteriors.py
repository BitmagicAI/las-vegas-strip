import bpy,os,sys,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.world=bpy.data.worlds.new('Daylight exterior review');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.5,.62,.85,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.5,-.6,-.75);bpy.context.object.data.energy=2.6;bpy.context.object.data.angle=.04
shots=[
 ('planet-hollywood',(-33,27,200),(126,48,220),30),
 ('planet-hollywood-aerial',(-55,145,149),(135,46,223),37),
 ('flamingo',(-1,19,-307),(146,36,-237),34),
 ('flamingo-aerial',(28,136,-169),(148,34,-237),34),
 ('horseshoe',(0,17,-174),(111,41,-123),28),
 ('horseshoe-aerial',(29,110,-190),(111,32,-117),35),
 ('planet-hollywood-entry',(40,1.8,217),(65,5,219),23),
 ('flamingo-entry',(72,1.8,-237),(92,5,-236),22),
 ('horseshoe-entry',(111,1.8,-167),(111,4,-146),23),
]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for n,p,t,lens in shots:
 if selected and n not in selected:continue
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.location=(p[0],-p[2],p[1]);cam.rotation_euler=(Vector((t[0],-t[2],t[1]))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_end=1400;s.camera=cam;s.render.filepath=os.path.abspath('build/exteriors/'+n+'.png');bpy.ops.render.render(write_still=True)
