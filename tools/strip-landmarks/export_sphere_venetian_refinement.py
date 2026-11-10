"""Scoped original facade export for the claimed three-building garage group."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import export as E
for name in ['sphereGarage-exterior','venetianEmployeeGarage-exterior']:
 E.bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(name)
 E.bpy.ops.export_scene.gltf(filepath=str((E.OUT/(name+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED',name,flush=True)
