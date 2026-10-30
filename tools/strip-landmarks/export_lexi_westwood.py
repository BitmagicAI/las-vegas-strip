import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import ast
source=ast.parse(Path("tools/strip-landmarks/lexi_westwood.py").read_text())
E.colors.update(next(ast.literal_eval(n.value)for n in source.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="COLORS" for t in n.targets)))
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('lexi-westwood-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['lx-metal','lx-iron']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='lx-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='ag-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='lx-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('lexi-westwood-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('lexi-westwood-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
