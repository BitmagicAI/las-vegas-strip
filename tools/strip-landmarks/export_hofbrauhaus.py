"""Isolated exporter: original materials, no changes to other resort assets."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
from hofbrauhaus_materials import finishes,trees
E.colors.update({'hb-plaster':'e3e0d4','hb-stone':'cfccc2','hb-frame':'66554d','hb-glass':'47616a','hb-planter':'46463c','hb-leaf':'405a32','hb-flower':'b84b54','hb-blue':'284c7a','hb-roof':'ac5b3d','hb-bay':'626c65','hb-copper':'66958a'})
E.colors.update({'hb-cream':'e0cfab','hb-cobble':'8c8c86','hb-floor':'9a7454','hb-vault':'e6ca79','hb-oak':'ac7336','hb-darkwood':'574431','hb-iron':'302f2c','hb-bottle':'52613b','hb-sky':'92b4c5','hb-bark':'665040','hb-lamp':'efd3a1','hb_pool':'649ca4'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear()
if '--interior-only' not in sys.argv:
 # Reuse our original clay-tile maps, never reference photography. UVs follow
 # the building axes and slope, so tile size stays constant across roof faces.
 roof=E.material('bcr-tile-paint').copy();roof.name='Strip / hb-roof-paint'
 E.materials['hb-roof']=roof
 E.add('hofbrauhaus-exterior')
 import math
 co=math.cos(1.7868214428245313);si=math.sin(1.7868214428245313)
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH' or obj.data.materials[0]!=roof:continue
  uv=obj.data.uv_layers.new(name='Roof metres')
  for loop in obj.data.loops:
   p=obj.data.vertices[loop.vertex_index].co
   dx,dz=p.x-1922.741,-p.y-969.671
   u,v=co*dx-si*dz,si*dx+co*dz
   uv.data[loop.index].uv=(u/1.12,v*math.sqrt(1+.36**2)/.78)
 for key in ['hb-glass','hb-copper']:
  bs=E.materials[key].node_tree.nodes.get('Principled BSDF')
  bs.inputs['Roughness'].default_value=.26 if key=='hb-glass' else .52
  bs.inputs['Metallic'].default_value=.12 if key=='hb-glass' else .48
 trees()
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'hofbrauhaus-exterior.blend').resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/'hofbrauhaus-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED hofbrauhaus-exterior')


# Export the streamed public rooms separately from the permanent exterior.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
E.add('hofbrauhaus-interior')
finishes();trees(interior=True)
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'hofbrauhaus-interior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
