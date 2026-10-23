import bpy,json,math
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/staged-vegas.blend').resolve()))
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
for name,pp,tt in [('horseshoe',(110,1.95,-144),(110,2.6,-122)),('cosmo',(-32,1.95,242),(-54,2.6,242)),('paris',(75,1.95,-39),(97,2.6,-39))]:
 p=Vector((pp[0],-pp[2],pp[1]));t=Vector((tt[0],-tt[2],tt[1]));d=(t-p).normalized()
 for j in range(4):
  hit,pos,n,face,obj,mat=s.ray_cast(dg,p,d,distance=60)
  if not hit:break
  print(name,'RAY',obj.name,'distance',round((pos-p).length,3),'at',tuple(pos),flush=True);p=pos+d*.03
