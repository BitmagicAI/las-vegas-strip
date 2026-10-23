import bpy, math, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/vehicles/afterlight-jeep.blend'))
body=bpy.data.objects['Body'];body.location.z=.78
wheel=bpy.data.objects['Wheel']
for x in [-.8775,.8775]:
 for z in [-1.58,1.58]:
  w=wheel.copy();bpy.context.collection.objects.link(w);w.location=(x,-z,.48);w.rotation_euler.y=math.pi/2
  for c in list(wheel.children):
   n=c.copy();n.data=c.data;bpy.context.collection.objects.link(n);n.parent=w
for o in [wheel,*wheel.children]:o.hide_render=True
bpy.data.objects['Charger'].location=(-2.3,.8,0)
bpy.ops.mesh.primitive_plane_add(size=200)
m=bpy.data.materials.new('Concrete');m.diffuse_color=(.19,.20,.19,1);bpy.context.object.data.materials.append(m)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Review ambient');s.world.color=(.45,.45,.45)
for name,loc,power,size in [('key',(4,-5,8),2100,6),('fill',(-4,-2,6),1700,5),('rim',(1,6,5),1600,4)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Review');o=bpy.data.objects.new('Review',d);s.collection.objects.link(o);o.location=(6,-8,4.4);o.rotation_euler=(Vector((-.6,0,1.1))-o.location).to_track_quat('-Z','Y').to_euler();d.lens=50;s.camera=o
s.render.filepath=os.path.abspath('build/vehicles/jeep-review.png');bpy.ops.render.render(write_still=True)
