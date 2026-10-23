import bpy,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path('build/hotels/resort-expansion/review');OUT.mkdir(exist_ok=True)
sets=['paris','caesars','cosmopolitan','flamingo','horseshoe','planet-hollywood','aria','vdara','waldorf']
def g(p):return Vector((p[0],-p[2],p[1]))
for key in sets:
 for kind in ['room','corridor']:
  bpy.ops.wm.open_mainfile(filepath=str(Path(f'build/hotels/{key}-{kind}.blend').resolve()));sc=bpy.context.scene
  if kind=='corridor':
   original=[o for o in sc.objects if o.type=='MESH']
   for z in [-6,-12,-18]:
    for o in original:n=o.copy();n.data=o.data;sc.collection.objects.link(n);n.location.y-=z
   # Real shared leaf, installed in both corridor doorways for review.
   with bpy.data.libraries.load(str(Path(f'build/hotels/{key}-door.blend').resolve())) as (src,dst):dst.objects=list(src.objects)
   for ob in dst.objects:
    if not ob or ob.type!='MESH':continue
    for side in [-1,1]:
     for z in [0,-6,-12,-18]:
      n=ob.copy();n.data=ob.data;sc.collection.objects.link(n);n.matrix_world=Matrix.Translation(g((side*1.85,1.325,z))) @ Matrix.Rotation(-side*math.pi/2,4,'Z') @ ob.matrix_world
  sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=900;sc.render.resolution_y=620;sc.render.resolution_percentage=100
  sc.world=bpy.data.worlds.new('Architectural review');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.30,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
  for pos,power,size in ([((2,3.1,0),180,3),((5,2.9,0),170,3)] if kind=='room' else [((0,2.95,z),150,2) for z in [0,-6,-12,-18]]):
   d=bpy.data.lights.new('review fill','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new('review fill',d);sc.collection.objects.link(o);o.location=g(pos)
  camera_data=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',camera_data);sc.collection.objects.link(camera)
  pos=(.8,1.70,.28) if kind=='room' else (.12,1.7,2.70);target=(4.3,1.35,-.38) if kind=='room' else (0,1.7,-18)
  camera.location=g(pos);camera.rotation_euler=(g(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=19 if kind=='room' else 23;sc.camera=camera
  sc.render.image_settings.file_format='PNG';sc.render.filepath=str((OUT/f'{key}-{kind}.png').resolve());bpy.ops.render.render(write_still=True)
  print('REVIEW',key,kind,flush=True)
