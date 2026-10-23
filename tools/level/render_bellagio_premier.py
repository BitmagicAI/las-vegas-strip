"""Local visual QA for the actual saved runtime room asset."""
import bpy, math
from mathutils import Vector
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/bellagio-room.blend').resolve()))
def v(p):return Vector((p[0],-p[2],p[1]))
def area(name,p,target,power,size,color):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
    ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=v(p);ob.rotation_euler=(v(target)-ob.location).to_track_quat('-Z','Y').to_euler()
area('window daylight',(7.83,2.1,0),(4,1,0),320,3.7,(.78,.86,1))
area('room ceiling bounce',(5.2,3.20,.35),(5.2,0,.35),200,3.6,(1,.88,.73))
area('entry bounce',(1.3,3.16,.4),(1.3,0,.4),90,1.8,(1,.88,.75))
area('bath ceiling',(1.7,3.12,-1.7),(1.7,0,-1.7),90,1.5,(1,.9,.78))
area('vanity reflected glow',(2.05,1.9,-2.73),(1.8,1,-.7),28,1.1,(1,.90,.78))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1280;scene.render.resolution_y=854;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Review exterior');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.39,.49,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
scene.view_settings.view_transform='AgX'
data=bpy.data.cameras.new('Room review');ob=bpy.data.objects.new('Room review',data);scene.collection.objects.link(ob);scene.camera=ob;data.lens=19;data.clip_start=.03
for name,p,target,lens in [('bedroom',(3.13,1.6,1.18),(6.0,1.36,-.45),19),('bathroom',(1.66,1.63,-.64),(1.78,1.45,-2.71),15),('bedroom-reverse',(7.52,1.68,-.20),(3.6,1.35,1.35),20)]:
    ob.location=v(p);ob.rotation_euler=(v(target)-ob.location).to_track_quat('-Z','Y').to_euler();data.lens=lens
    scene.render.filepath=str(Path('build/hotels/bellagio-premier/'+name+'.png').resolve());bpy.ops.render.render(write_still=True)
