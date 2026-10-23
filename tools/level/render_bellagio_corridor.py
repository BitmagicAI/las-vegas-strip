"""Render the same shared GLBs used by the streamed guest hallway."""
import bpy, math
from mathutils import Vector
from pathlib import Path
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def v(p):return Vector((p[0],-p[2],p[1]))
def asset(name):
    before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(Path('build/hotels/'+name+'.glb').resolve()))
    col=bpy.data.collections.new(name)
    for ob in set(bpy.data.objects)-before:
        for owner in list(ob.users_collection):owner.objects.unlink(ob)
        col.objects.link(ob)
    return col
def instance(col,p,yaw=0):
    ob=bpy.data.objects.new(col.name,None);ob.instance_type='COLLECTION';ob.instance_collection=col
    bpy.context.scene.collection.objects.link(ob);ob.location=v(p);ob.rotation_euler.z=yaw
def area(p,power=70):
    d=bpy.data.lights.new('Review bounce','AREA');d.energy=power;d.shape='DISK';d.size=2.4;d.color=(1,.91,.80)
    ob=bpy.data.objects.new('Review bounce',d);bpy.context.scene.collection.objects.link(ob);ob.location=v(p)
c=asset('bellagio-corridor');d=asset('bellagio-door');e=asset('bellagio-corridor-end')
for bay in range(8):
    z=-6*bay;instance(c,(0,0,z))
    for side in [-1,1]:instance(d,(side*1.85,1.325,z),side*math.pi/2)
    for dz in [-1.5,1.5]:area((0,3.04,z+dz))
instance(e,(0,0,-42-2.96))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1280;scene.render.resolution_y=854;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Neutral review');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[1].default_value=.12
scene.view_settings.view_transform='AgX'
data=bpy.data.cameras.new('Hall review');camera=bpy.data.objects.new('Hall review',data);scene.collection.objects.link(camera);scene.camera=camera;data.clip_start=.03
for name,p,target,lens in [('hallway',(0,1.66,2.65),(0,1.55,-14),20),('door',(-.90,1.66,1.9),(1.77,1.48,0),22),('console',(.05,1.68,-41.9),(0,1.7,-44.7),22)]:
    camera.location=v(p);camera.rotation_euler=(v(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=lens
    scene.render.filepath=str(Path('build/hotels/bellagio-corridor/'+name+'.png').resolve());bpy.ops.render.render(write_still=True)
