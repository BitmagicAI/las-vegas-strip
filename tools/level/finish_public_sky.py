"""Apply the final Paris mural UV correction without rebuilding unchanged meshes."""
import bpy
from pathlib import Path
p=Path('build/hotels/staged-vegas.blend').resolve()
bpy.ops.wm.open_mainfile(filepath=str(p))
for image in bpy.data.images:
 if Path(image.filepath).name=='paris-sky.png':
  image.filepath=str(Path('build/public-resorts/textures/paris-sky.png').resolve())
  if image.packed_file:image.unpack(method='REMOVE')
  image.reload();image.pack()
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not any(m and m.name=='pr_sky' for m in o.data.materials):continue
 uv=o.data.uv_layers.active
 for f in o.data.polygons:
  if o.data.materials[f.material_index].name!='pr_sky':continue
  axis=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=axis]
  for j in f.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[j].vertex_index].co
   uv.data[j].uv=(v[axes[0]]/40,v[axes[1]]/40)
bpy.ops.wm.save_as_mainfile(filepath=str(p))
