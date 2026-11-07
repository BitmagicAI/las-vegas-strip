"""Scoped pair export, preserving the established arrival foliage importer."""
import sys,runpy
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import bpy
import export as E
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('nynyIrishKiosk-exterior')
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'nynyIrishKiosk-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
runpy.run_path('tools/strip-landmarks/export_nyny_landscape.py',run_name='__main__')
