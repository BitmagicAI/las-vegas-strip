import bpy,math,os
from mathutils import Vector
from pathlib import Path
OUT=Path('build/hotels/review');OUT.mkdir(exist_ok=True)
def g(p):return Vector((p[0],-p[2],p[1]))
for name in ['bellagio-room','veer-room','bellagio-corridor','veer-corridor','bellagio-stair']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/hotels/'+name+'.blend'))
 scene=bpy.context.scene
 if name.endswith('corridor'):
  originals=[o for o in scene.objects if o.type=='MESH']
  for z in [-6,6,12]:
   for o in originals:
    n=o.copy();n.data=o.data;scene.collection.objects.link(n);n.location.y-=z
 scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1100;scene.render.resolution_y=750;scene.render.resolution_percentage=100
 scene.world=bpy.data.worlds.new('Review world');scene.world.color=(.5,.5,.5)
 for p,power,size in [((1.0,2.85,0),220,4),((4,2.6,0),160,3),((0,2.8,8),250,4)]:
  data=bpy.data.lights.new('Review fill','AREA');data.energy=power;data.shape='DISK';data.size=size
  o=bpy.data.objects.new('Review fill',data);scene.collection.objects.link(o);o.location=g(p);o.rotation_euler=(0,0,0)
 if name.endswith('room'):pos=(.28,1.75,.15);target=(4,1.45,.0)
 elif name.endswith('corridor'):pos=(.1,1.7,-5.4);target=(0,1.65,12)
 else:pos=(.0,1.65,-3.8);target=(-1.65,2.1,2)
 data=bpy.data.cameras.new('Review camera');camera=bpy.data.objects.new('Review camera',data);scene.collection.objects.link(camera);camera.location=g(pos);camera.rotation_euler=(g(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=20;scene.camera=camera
 scene.render.image_settings.file_format='PNG';scene.render.filepath=str((OUT/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
 print('REVIEW',name,flush=True)
