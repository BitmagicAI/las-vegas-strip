"""Scoped export, retaining shared material settings and source colours."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import export as E
E.colors.update({'ga-nave-floor':'ded9cc','ga-nave-border':'4d4c48','ga-nave-cream':'e1dfd3','ga-pew-wood':'795139','ga-nave-dark':'292c2a','ga-nave-gold':'b49c61','ga-nave-stone':'d7cdb7'})
for name in ['guardianAngel-exterior','guardianAngel-interior']:
 E.bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(name)
 E.bpy.ops.export_scene.gltf(filepath=str((E.OUT/(name+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED',name,flush=True)
