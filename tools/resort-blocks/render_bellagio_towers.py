"""Render the tower preview (preview_bellagio_towers.py) with the block's materials. Views: reference (the owner's
Google Earth angle from over the Strip), lake (the film's lake level), spa, top."""
import bpy,json,math,sys,runpy
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,'tools/resort-blocks');import bellagio_palette
O=Path('build/resort-blocks/bellagio-tower-preview');pt=lambda p:Vector((p[0],-p[2],p[1]))
ns=runpy.run_path('tools/strip-landmarks/export.py',run_name='resort_materials');ns['add'].__globals__['OUT']=O
ns['colors'].update(bellagio_palette.COLORS);orig=ns['material']
def mat(k):
 cached=k in ns['materials'];m=orig(k)
 if not cached and k.startswith('bel-'):bellagio_palette.finish(k,m.node_tree.nodes.get('Principled BSDF'))
 return m
ns['add'].__globals__['material']=mat
bpy.ops.wm.read_factory_settings(use_empty=True);ns['materials'].clear();ns['add']('towerPreview-exterior')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.threads_mode='FIXED';s.render.threads=6
s.world=bpy.data.worlds.new('Daylight');s.world.use_nodes=True;bg=s.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.55,.66,.8,1);bg.inputs[1].default_value=.8
sun=bpy.data.lights.new('sun','SUN');sun.energy=3.2;sun.angle=.05;o=bpy.data.objects.new('sun',sun);s.collection.objects.link(o);o.rotation_euler=(math.radians(40),0,math.radians(-110))
me=bpy.data.meshes.new('ground');me.from_pydata([(-900,-900,0),(500,-900,0),(500,300,0),(-900,300,0)],[],[(0,1,2,3)]);g=bpy.data.objects.new('ground',me);s.collection.objects.link(g);gm=bpy.data.materials.new('ground');gm.use_nodes=True;gm.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.45,.42,.38,1);me.materials.append(gm)
cam=bpy.data.objects.new('camera',bpy.data.cameras.new('camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.clip_end=15000;s.view_settings.view_transform='AgX'
views={'reference':([-40,250,345],[-330,62,348],30),'lake':([-60,3,300],[-300,72,330],24),'spa':([-250,150,640],[-392,60,560],30),'top':([-300,420,330],[-330,120,360],35),'rotunda':([-200,150,322],[-302,138,322],40)}
want=[a for a in sys.argv[sys.argv.index('--')+1:]] if '--' in sys.argv else ['reference','lake']
for name in want:
 eye,target,lens=views[name];cam.location=pt(eye);cam.rotation_euler=(pt(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 s.render.filepath=str((O/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
