import bpy,json,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/hotels/staged-vegas.blend'))
out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 out.append(dict(name=o.name,lo=[lo[0],lo[2],-hi[1]],hi=[hi[0],hi[2],-lo[1]],polys=len(o.data.polygons),materials=[m.name if m else None for m in o.data.materials]))
open('build/public-resorts/inventory.json','w').write(json.dumps(out,indent=2))
print('INVENTORY',len(out),flush=True)
