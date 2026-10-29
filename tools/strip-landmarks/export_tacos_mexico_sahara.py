import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'tm-wall': 'd6d2c6', 'tm-floor': '999185', 'tm-roof': 'b7b9b5', 'tm-roof-under': 'b4b1a7', 'tm-red': 'a33e3a', 'tm-seam': '999e9a', 'tm-stone': 'd0c4b6', 'tm-panel': 'cac5b9', 'tm-glass': '374448', 'tm-metal': '9a9f9f', 'tm-letter': 'ede9d6', 'tm-paving': 'a86057', 'tm-service': '8d8880', 'tm-grout': '73665b', 'tm-tile-red': '963d39', 'tm-tile-cream': 'ddd7bc', 'tm-table': 'cfb77f', 'tm-frame': '2d3031', 'tm-seat': '9d3439', 'tm-bright': 'bfc5c4', 'tm-lamp': 'eee4be'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('tacos-mexico-sahara-'+part+'')
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
  if key=='tm-glass':bs.inputs['Roughness'].default_value=.24
  if key in ['tm-metal','tm-frame','tm-bright']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.4
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('tacos-mexico-sahara-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('tacos-mexico-sahara-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED tacos-mexico-sahara-'+part+'')
