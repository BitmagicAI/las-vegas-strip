"""Export only the new gateway; preserve installed STRAT through the merge installer."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'sg-blue-paint':'294d76','sg-pier':'b7b0a3','sg-metal':'3c4249','sg-pink':'c76791','sg-pale':'e5d7d2','sg-lens':'b6cbd9'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('stratGateway-exterior')
for mat in bpy.data.materials:
 if mat.name in ['Strip / sg-pink','Strip / sg-lens']:
  bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=bs.inputs['Base Color'].default_value;bs.inputs['Emission Strength'].default_value=.18 if 'pink' in mat.name else .15
p=E.OUT/'stratGateway-exterior.glb';bpy.ops.export_scene.gltf(filepath=str(p.resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('Exported original gateway:',p)
