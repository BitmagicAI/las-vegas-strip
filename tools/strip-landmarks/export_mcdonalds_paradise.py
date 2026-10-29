import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'mp-stucco': '777362', 'mp-roof': 'aaa79c', 'mp-paving': 'b5b2a7', 'mp-joint': '706b5b', 'mp-glass': '344344', 'mp-frame': 'b8b9ab', 'mp-steel': '9b9c94', 'mp-cream': 'ddd9c1', 'mp-dark': '383c36', 'mp-trim': 'e4e0cd', 'mp-yellow': 'd7b849', 'mp-red': 'a1473a', 'mp-handle': 'c7c9bc', 'mp-pole': '827b59', 'mp-stone-0': 'c9c5b0', 'mp-stone-1': 'bbb49b', 'mp-stone-2': 'd4d0bb', 'mp-stone-3': 'afa98f'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('mcdonalds-paradise-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
 if key=='mp-glass':bs.inputs['Roughness'].default_value=.24
 if key in ['mp-steel','mp-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.4
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'mcdonalds-paradise-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'mcdonalds-paradise-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED mcdonalds-paradise-exterior')
