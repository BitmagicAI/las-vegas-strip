"""Export scoped original SAHARA crown geometry; never installs or bakes shared data."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'sar-crown':'bdb4a0','sar-inset':'354e59'})
key=next(a.split('=',1)[1] for a in sys.argv if a.startswith('--only='))
assert key == 'saharaExterior'
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+'-exterior')
m=E.materials['sar-inset'];bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=.75;bs.inputs['Roughness'].default_value=.24
bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+'-exterior.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
