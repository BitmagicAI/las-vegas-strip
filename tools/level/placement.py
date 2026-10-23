"""Rigid component placement; visuals and gameplay records move together."""
import bpy, math
from mathutils import Matrix
from bmlevel import level
FIELDS=('colliders','doors','volumes','landmarks','lights','stairs','visual_points')
def checkpoint():
 return set(bpy.data.objects),{k:len(getattr(level,k)) for k in FIELDS}
def relocate(mark, origin=(0,0,0), target=(0,0,0), yaw=0):
 bpy.context.view_layer.update()
 objects,starts=mark;c,s=math.cos(yaw),math.sin(yaw)
 def point(p):
  x,y,z=p[0]-origin[0],p[1]-origin[1],p[2]-origin[2]
  return (target[0]+c*x+s*z,target[1]+y,target[2]-s*x+c*z)
 matrix=Matrix.Translation((target[0],-target[2],target[1])) @ Matrix.Rotation(yaw,4,'Z') @ Matrix.Translation((-origin[0],origin[2],-origin[1]))
 for obj in set(bpy.data.objects)-objects:obj.matrix_world=matrix @ obj.matrix_world
 for key in FIELDS:
  rows=getattr(level,key)
  for i in range(starts[key],len(rows)):
   row=rows[i]
   if key=='visual_points':rows[i]=point(row);continue
   for field in ('position','target','foot','top'):
    if hasattr(row,field):setattr(row,field,point(getattr(row,field)))
   if hasattr(row,'vertices'):row.vertices=[v for j in range(0,len(row.vertices),3) for v in point(row.vertices[j:j+3])]
   if hasattr(row,'yaw'):row.yaw+=yaw
   if hasattr(row,'rotation_y'):row.rotation_y+=yaw
 bpy.context.view_layer.update()
