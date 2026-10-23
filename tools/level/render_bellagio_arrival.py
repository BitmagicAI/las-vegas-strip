import bpy,sys,math
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/staged-vegas.blend').resolve()))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1400;s.render.resolution_y=950;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Arrival review');s.world.use_nodes=True
bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.50,.58,.72,1);bg.inputs['Strength'].default_value=.7
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.5,-.6,-.4);sun.data.energy=2.0;sun.data.angle=.06
cd=bpy.data.cameras.new('Arrival review');cam=bpy.data.objects.new('Arrival review',cd);s.collection.objects.link(cam);s.camera=cam;cd.clip_end=1500
shots={'main-exterior':((-114,49,2.3),(-128,34,4.8),23),
       'main-vault':((-130.0,34,1.8),(-124,34,6.1),17),
       'gallery-exterior':((-113,34,2.0),(-129,34,3.8),22)}
out=Path('build/bellagio-arrival');out.mkdir(exist_ok=True)
for name,(pos,target,lens) in shots.items():
    if '--' in sys.argv and name not in sys.argv[sys.argv.index('--')+1:]:continue
    cam.location=(pos[0],-pos[1],pos[2]);at=Vector((target[0],-target[1],target[2]));cam.rotation_euler=(at-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens
    s.view_settings.view_transform='AgX';s.render.filepath=str((out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
