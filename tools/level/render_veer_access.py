"""Entrance review includes the actual streamed ground entry and stair meshes."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
def g(p):return Vector((p[0],-p[2],p[1]))
bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/staged-vegas.blend').resolve()))
towers=json.loads(Path('src/work/hotels/towers.json').read_text())
for t in towers:
 if t['set']!='veer':continue
 transform=Matrix.Translation(g(t['origin']))@Matrix.Rotation(t['yaw'],4,'Z')
 shear=Matrix.Identity(4);shear[0][2]=t['lean'][0];shear[1][2]=-t['lean'][1];transform=transform@shear
 for kind in ['entry','stair']:
  with bpy.data.libraries.load(str(Path('build/hotels/veer-'+kind+'.blend').resolve()),link=False) as (src,dst):dst.objects=list(src.objects)
  for ob in dst.objects:
   if ob and ob.type=='MESH':bpy.context.scene.collection.objects.link(ob);ob.matrix_world=transform@ob.matrix_world
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16
scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Veer review daylight');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.58,.68,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
sun=bpy.data.lights.new('Sun','SUN');sun.energy=2;ob=bpy.data.objects.new('Sun',sun);scene.collection.objects.link(ob);ob.rotation_euler=(.35,-.4,-1.1)
for x,z in [(-125,453.4252),(-188,422.5748)]:
 light=bpy.data.lights.new('Arcade fill','AREA');light.energy=1300;light.shape='DISK';light.size=5
 ob=bpy.data.objects.new('Arcade fill',light);scene.collection.objects.link(ob);ob.location=g((x,5.2,z))
camera=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.lens=25
for name,p,target in [
 ('east',(-122,1.8,451.5),(-130.5,2.7,453.4252)),
 ('west',(-186,1.8,420.6),(-194.5,2.7,422.5748)),
 ('street',(-92,1.8,480),(-93,3.5,470))]:
 camera.location=g(p);camera.rotation_euler=(g(target)-camera.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(Path('build/veer-access/'+name+'.png').resolve());bpy.ops.render.render(write_still=True)
