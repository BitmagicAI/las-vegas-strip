import bpy
from pathlib import Path
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(Path('build/south-strip/liberty-scan.glb').resolve()))
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  vs=[o.matrix_world@Vector(v) for v in o.bound_box];print('SCAN',o.name,len(o.data.polygons),'bounds',[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)],'materials',[m.name for m in o.data.materials],flush=True)
