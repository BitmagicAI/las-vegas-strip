import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'mg-service':'653b36','mg-bark':'6a6353','mg-leaf':'657351','mg-hedge':'52633c','mg-lawn':'68764d','mg-gravel':'aaa79a','mg-garden-paving':'b8b7ab','mg-shade':'36878a','mg-shade-light':'6ca8a6','mg-chair-frame': 'deded6', 'mg-stucco': 'a79370', 'mg-roof': '8f8170', 'mg-deck': 'bdb5a5', 'mg-copper': '98734f', 'mg-seam': '745a41', 'mg-iron': '292d2b', 'mg-door': '614d44', 'mg-glass': '394748', 'mg-frame': '9c9f98', 'mg-brass': 'a48a50', 'mg-trim': 'c8c4b5', 'mg-stone': '837c68', 'mg-soil': '514735', 'mg-wood': '64503b', 'mg-lantern': 'b5a57d', 'mg-tile': '286375', 'mg_pool': '247b8a', 'mg-coping': 'a3694f', 'mg-blue': '386a91', 'stone': 'b3aa95', 'steel': '303632'})
if '--interior-only' not in sys.argv:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('mardi-gras-exterior')
 for obj in bpy.context.scene.objects:
  if obj.type=='MESH':obj.data.validate(verbose=True)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
  if key=='mg-glass':bs.inputs['Roughness'].default_value=.24
  if key in ['mg-frame','mg-iron']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.4
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'mardi-gras-exterior.blend').resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/'mardi-gras-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED mardi-gras-exterior')

# Public meeting rooms stream separately; all finishes are original, photo-guided colors.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
E.colors.update({'mg-room-wall':'c5b89f','mg-room-trim':'dedcd0','mg-ceiling':'d3d1c4','mg-carpet':'67583e','mg-partition':'aaa18d','mg-table-cloth':'576447','mg-seat':'607366','mg-ceiling-light':'f4e8cb'})
E.add('mardi-gras-interior')
for obj in bpy.context.scene.objects:
 if obj.type=='MESH':obj.data.validate(verbose=True)
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF')
 if key.startswith('mg-'):bs.inputs['Roughness'].default_value=.85
 if key=='mg-ceiling-light':
  bs.inputs['Emission Color'].default_value=(.8,.71,.52,1);bs.inputs['Emission Strength'].default_value=.45
from mardi_gras_materials import meeting_finishes
meeting_finishes()
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'mardi-gras-interior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'mardi-gras-interior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
